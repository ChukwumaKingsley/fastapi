from typing import List, Optional
from fastapi import Depends, HTTPException, status, APIRouter
from .. import models, schemas, oauth2
from ..database import Session, get_db

router = APIRouter(
    prefix="/vote",
    tags=["Votes"]
)

@router.post("/{post_id}", status_code=status.HTTP_201_CREATED)
def vote(post_id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    post = post_query.first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post does not exist")
    
    # Check if the user has previously voted the post
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == post_id, models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()

    if found_vote:
        vote_query.delete(synchronize_session=False)
        db.commit()
        return "Vote removed successfully!"

    else:
        new_vote = models.Vote(post_id=post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return "Vote added successfully!"
    

@router.get("/post_votes/{post_id}", response_model=schemas.Counts)
def get_votes(post_id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    vote_count_query = db.query(models.Vote).filter(models.Vote.post_id == post_id).all()
    if not vote_count_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post ${post_id} does not exist.")
    vote_counts = len(vote_count_query)
    print(vote_counts)
    return {"counts": vote_counts}
