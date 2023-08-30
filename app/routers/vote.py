from typing import List, Optional
from fastapi import Depends, HTTPException, status, APIRouter
from .. import models, schemas, oauth2
from ..database import Session, get_db

router = APIRouter(
    prefix="/vote",
    tags=["Votes"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == vote.post_id)
    post = post_query.first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post does not exist")
    
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()
    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"The user {current_user.email} has voted on this post already")
        
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        # votes = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id).count()
        # post_query.update({"votes": votes}, synchronize_session=False)
        
        db.commit()
        return "successfully voted!"

    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote does not exist")
        vote_query.delete(synchronize_session=False)

        # votes = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id).count()
        # db.commit()
        # print(votes)
        # post_query.update({"votes": votes}, synchronize_session=False)
        db.commit()
        return "successfully deleted vote!"