import pytest
from app import schemas


def test_get_all_posts(authorized_client, test_post):
    res = authorized_client.get("/posts/")
    def validate(post):
        return schemas.Post(**post)
    post_map = map(validate, res.json())
    assert res.status_code == 200
    assert res.json()[0]['id'] == 1

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
    assert post.id == test_post[0].id
    assert post.content == test_post[0].content

@pytest.mark.parametrize("title, content, published",[
    ("Awesome title", "Cool content", True),
    ("Awesome", "Cool mums", True),
    ("Hungry munchies", "Really", False)
])
def test_create_post(authorized_client, test_user, test_post, title, content, published):
    res = authorized_client.post("/posts/", json={"title": title, "content": content, "published": published})

    created_post = schemas.PostCreate(**res.json())
    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published ==  published

def test_create_post_set_publish_default(authorized_client, test_user, test_post, title = "Tities", content = "Giggles"):
    res = authorized_client.post("/posts/", json={"title": title, "content": content})

    created_post = schemas.PostCreate(**res.json())
    assert res.status_code == 201
    assert (created_post.title == title) and (created_post.content == content) and (created_post.published ==  True)

def test_unauthorized_user_create_posts(client, test_post):
    res = client.post("/posts/", json={"title": "title", "content": "content", "published": False})
    assert res.status_code == 401

def test_unauthorized_user_delete_posts(client, test_post):
    res = client.delete(f"/posts/{test_post[0].id}")
    assert res.status_code == 401

def test_delete_post_success(authorized_client, test_post, test_user):
    res = authorized_client.delete(f"/posts/{test_post[0].id}")
    assert res.status_code == 204

def test_delete_nonexistent_post(authorized_client, test_post, test_user):
    res = authorized_client.delete(f"/posts/34433")
    assert res.status_code == 404

def test_delete_post_not_user(authorized_client, test_post, test_user):
    res = authorized_client.delete(f"/posts/{test_post[3].id}")
    assert res.status_code == 403

def test_update_post(authorized_client, test_post, test_user):
    data = {
        "title": "Updated title.",
        "content": "Updated content.",
        "id": test_post[0].id
    }
    res = authorized_client.put(f"/posts/{test_post[0].id}", json=data)
    updated_post = schemas.Post(**res.json())
    assert res.status_code == 200
    assert updated_post.title == data["title"]

def test_update_another_user_post(authorized_client, test_post, test_user):
    data = {
        "title": "Updated title.",
        "content": "Updated content.",
    }
    res = authorized_client.put(f"/posts/{test_post[3].id}", json=data)
    assert res.status_code == 403

def test_unauthorized_user_update_posts(client, test_post):
    data = {
        "title": "Updated title.",
        "content": "Updated content.",
    }
    res = client.put(f"/posts/{test_post[0].id}", json=data)
    assert res.status_code == 401

def test_update_nonexistent_post(authorized_client, test_post, test_user):
    data = {
        "title": "Updated title.",
        "content": "Updated content.",
    }
    res = authorized_client.put(f"/posts/34433", json=data)
    assert res.status_code == 404