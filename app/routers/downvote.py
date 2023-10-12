from typing import List, Optional
from fastapi import Depends, HTTPException, status, APIRouter
from .. import models, schemas, oauth2
from ..database import Session, get_db

router = APIRouter(
    prefix="/downvote",
    tags=["Downvotes"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def downvote(downvote: schemas.DownVote, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == downvote.post_id)
    post = post_query.first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post does not exist")
    
    downvote_query = db.query(models.DownVote).filter(models.DownVote.post_id == downvote.post_id, models.DownVote.user_id == current_user.id)
    found_downvote = downvote_query.first()

    if downvote.dir == 1:
        if found_downvote:
            # If the user has already downvoted (dir == 1), remove the downvote
            downvote_query.delete(synchronize_session=False)
            db.commit()
            return "Downvote removed successfully!"
        
        new_downvote = models.DownVote(post_id=downvote.post_id, user_id=current_user.id)
        db.add(new_downvote)
        db.commit()
        return "Downvote added successfully!"
    
    else:
        if not found_downvote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Downvote does not exist")
        
        # The user is trying to remove a downvote (dir != 1)
        downvote_query.delete(synchronize_session=False)
        db.commit()
        return "Downvote removed successfully!"
