from fastapi.testclient import TestClient
from sqlalchemy import create_engine
import pytest
from sqlalchemy.orm import sessionmaker
from app.oauth2 import create_access_token
from app.main import app
from app.config import settings
from app import models
from app.database import get_db, Base

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}/{settings.database_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)

@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client(session):
    def overide_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = overide_get_db
    yield TestClient(app)
    
@pytest.fixture
def test_user(client):
     user_data = {"email": "test@gmail.com", "password": "testpassword", "name": "testname"}
     res = client.post("/users/", json=user_data)
     assert res.status_code == 201
     new_user = res.json()
     new_user['password'] = user_data['password']
     return new_user

@pytest.fixture
def test_user2(client):
     user_data = {"email": "test2@gmail.com", "password": "testpassword", "name": "testname2"}
     res = client.post("/users/", json=user_data)
     assert res.status_code == 201
     new_user = res.json()
     new_user['password'] = user_data['password']
     return new_user

@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

@pytest.fixture
def test_post(session, test_user, test_user2):
    post_data = [
        {
            "title": "One titile",
            "content": "Another content",
            "user_id": test_user['id'],
            "user_name": test_user['name']
        },
        {
            "title": "Two titile",
            "content": "Another Two content",
            "user_id": test_user['id'],
            "user_name": test_user['name']
        },
        {
            "title": "3 titile",
            "content": "3 Another content",
            "user_id": test_user['id'],
            "user_name": test_user['name']
        },
        {
            "title": "One titile four",
            "content": "Another content four",
            "user_id": test_user2['id'],
            "user_name": test_user2['name']
        }
    ]

    def create_post_model(post):
        return models.Post(**post)
    
    post_map = map(create_post_model, post_data)
    posts = list(post_map)
    session.add_all(posts)
    session.commit()

    posts = session.query(models.Post).all()
    return posts

