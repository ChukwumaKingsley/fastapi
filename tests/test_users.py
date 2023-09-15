from app import schemas
from .database import client, session

def test_root(client):
    res = client.get("/")
    assert res.json().get('message') == "Welcome to my good api"
    assert res.status_code == 200

def test_create_user(client):
    res = client.post("/users/", json={"email": "test@gmail.com", "password": "testpassword"})
    new_user = schemas.User(**res.json())
    assert res.status_code == 201
    assert new_user.email == "test@gmail.com"