from typing import List, Optional
from fastapi import Depends, HTTPException, status, APIRouter
from .. import models, schemas, oauth2
from ..database import Session, get_db

router = APIRouter(
    prefix="/downvote",
    tags=["Downvotes"]
)


@router.post("/{post_id}", status_code=status.HTTP_201_CREATED)
def downvote(post_id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    post = post_query.first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post does not exist")
    
    # Check if the user has previously voted the post
    downvote_query = db.query(models.DownVote).filter(models.DownVote.post_id == post_id, models.DownVote.user_id == current_user.id)
    found_vote = downvote_query.first()

    if found_vote:
        downvote_query.delete(synchronize_session=False)
        db.commit()
        return "Downvote removed successfully!"

    else:
        new_downvote = models.DownVote(post_id=post_id, user_id=current_user.id)
        db.add(new_downvote)
        db.commit()
        return "Downvote added successfully!"
