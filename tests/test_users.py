from app import schemas
from jose import jwt
import pytest
from app.config import settings


def test_root(client):
    res = client.get("/")
    assert res.json().get('message') == "Welcome to my good api"
    assert res.status_code == 200

def test_create_user(client):
    res = client.post("/users/", json={"email": "test@gmail.com", "password": "testpassword", "name": "testname"})
    new_user = schemas.User(**res.json())
    assert res.status_code == 201
    assert new_user.email == "test@gmail.com"


# def test_login_user(client, test_user):
#         res = client.post("/login", data={"email": test_user['email'], "password": test_user['password']})
#         login_res = schemas.Token(**res.json())
#         payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=[settings.algorithm])
#         id = payload.get("user_id")
#         assert id ==  test_user['id']
#         assert login_res.token_type == "bearer"
#         assert res.status_code == 200

# @pytest.mark.parametrize("email, password, status_code",[
#                          ('wrongemail@gmail.com', 'testpassword', 403),
#                          ('test@gmail.com', 'wrongpassword', 403),
#                          ('wrong@gmail.com', 'wrong', 403),
#                          (None, 'testpassword', 422),
#                          ('test@gmail.com', None, 422)
# ])
# def test_incorrect_login(test_user, client, email, password, status_code):
#      res =  client.post("/login", data={"email": email,  "password": password})
#      assert res.status_code == status_code