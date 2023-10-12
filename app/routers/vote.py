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
    
    # Check if the user has previously downvoted the post
    downvote_query = db.query(models.DownVote).filter(models.DownVote.post_id == vote.post_id, models.DownVote.user_id == current_user.id)
    found_downvote = downvote_query.first()

    # Remove the downvote if it exists
    if found_downvote:
        downvote_query.delete(synchronize_session=False)
        print("Found downvote, deleted it!")

    # Continue with processing the upvote logic
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()

    if vote.dir == 1:
        if found_vote:
            # If the user has already voted (dir == 1), remove the vote
            vote_query.delete(synchronize_session=False)
            db.commit()
            return "Vote removed successfully!"
        
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return "Vote added successfully!"
    
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote does not exist")
        
        # The user is trying to remove a vote (dir != 1)
        vote_query.delete(synchronize_session=False)
        db.commit()
        return "Vote removed successfully!"
