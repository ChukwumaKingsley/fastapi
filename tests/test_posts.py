# from typing import List
from app import schemas

def test_get_all_posts(authorized_client, test_post):
    res = authorized_client.get("/posts/")
    # def validate(post):
    #     return schemas.Post(**post)
    # post_map = map(validate, res.json())
    # print(post_map)
    # post_list = list(post_map)
    # print(post_list)
    assert res.status_code == 200

def test_unauthorized_user_get_all_posts(client, test_post):
    res = client.get("/posts/")
    assert res.status_code == 401

def test_unauthorized_user_get_one_posts(client, test_post):
    res = client.get(f"/posts/{test_post[0].id}")
    assert res.status_code == 401

def test_get_unexistent_post(authorized_client, test_post):
    res = authorized_client.get(f"/posts/99999")
    assert res.status_code == 404

def test_get_one_post(authorized_client, test_post):
    res = authorized_client.get(f"/posts/{test_post[0].id}")
    post = schemas.Post(**res.json())
    print(post)
