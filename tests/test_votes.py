import pytest
from app import models


@pytest.fixture()
def test_vote(test_post, session, test_user2):
    new_vote = models.Vote(post_id=test_post[3].id, user_id=test_user2['id'])
    session.add(new_vote)
    session.commit()

def test_vote_on_post(authorized_client, test_post):
    res = authorized_client.post("/vote/", json={"post_id": test_post[3].id, "dir": 1})
    assert res.status_code == 201

def test_vote_twice_on_post(authorized_client, test_post, test_vote):
    res = authorized_client.post("/vote/", json={"post_id": test_post[3].id, "dir": 1})
    assert res.status_code == 409