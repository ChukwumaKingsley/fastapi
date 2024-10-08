from typing import List, Optional
from fastapi import Depends, Form, HTTPException, UploadFile, status, APIRouter
from sqlalchemy import case, func, literal
from .. import models, schemas, utils, oauth2
from ..database import Session, get_db
from pydantic import EmailStr
import cloudinary.uploader
from ..config import settings

cloudinary.config(
    cloud_name= settings.cloud_api_name,
    api_key=settings.cloud_api_key,
    api_secret=settings.cloud_api_secret
)


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)



@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    #hash the password
    existing_user =  db.query(models.User).filter(models.User.email == user.email.lower()).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with this email already exists")
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    user.email = user.email.lower()
    # new_user = models.User(**user.dict())
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/me", response_model=schemas.UserOut)
def get_user(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {current_user.id} does not exist!")

    # Count the number of votes for the current user
    num_votes = db.query(func.count(models.Vote.user_id)).filter(models.Vote.user_id == current_user.id).scalar()
    # Count the number of downvotes for the current user
    num_downvotes = db.query(func.count(models.DownVote.user_id)).filter(models.DownVote.user_id == current_user.id).scalar()
    # Count the number of posts for the current user
    num_posts = db.query(func.count(models.Post.user_id)).filter(models.Post.user_id == current_user.id).scalar()
    # Add the counts to the user object
    user.votes_count = num_votes
    user.downvotes_count = num_downvotes
    user.posts_count = num_posts

    return user

@router.get("/user/{id}", response_model = schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"User with id {id} does not exist!")
    
    # Count the number of votes for the current user
    num_votes = db.query(func.count(models.Vote.user_id)).filter(models.Vote.user_id == id).scalar()
    # Count the number of downvotes for the current user
    num_downvotes = db.query(func.count(models.DownVote.user_id)).filter(models.DownVote.user_id == id).scalar()
    # Count the number of posts for the current user
    num_posts = db.query(func.count(models.Post.user_id)).filter(models.Post.user_id == id).scalar()
    # Add the counts to the user object
    user.votes_count = num_votes
    user.downvotes_count = num_downvotes
    user.posts_count = num_posts
    return user

@router.get("/all", response_model=List[schemas.UsersData])
def get_all_users(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), search: Optional[str] = ""):
    users = db.query(models.User).filter(func.lower(models.User.name).contains(search.lower())).all()

    # Add a new column current_user to the results
    for user in users:
        user.current_user = user.id == current_user.id

    return users

@router.put("/change_password", status_code=status.HTTP_200_OK)
def update_password(UserData: schemas.PasswordUpdate, current_user: int = Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.id == current_user.id)
    user = user_query.first()
    
    if not user: #check if the user exists
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = f'User does not exists.')
    if not utils.verify(UserData.old_password, user.password): #check if the old password is correct
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Incorrect old password!")
    if utils.verify(UserData.new_password, user.password): #Ensure the new and old passwords are not thesame
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Old and new passwords cannot be thesame")

    
    UserData.new_password = utils.hash(UserData.new_password)
    password_update = {"password": UserData.new_password}

    user_query.update(password_update, synchronize_session = False)
    db.commit()
    return "Password was successfully changed"

@router.put("/update", status_code=status.HTTP_200_OK, response_model=schemas.UserUpdated)
def update_user(
    name: str = Form(...),
    profile_pic: UploadFile = Form(None),
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
    ):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()


    if user.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized to change another's details")

    api_key = settings.cloud_api_key
    api_secret = settings.cloud_api_secret

    headers = {
        'Authorization': f'Basic {api_key}:{api_secret}'
    }

    if profile_pic:
        response = cloudinary.uploader.upload(
            profile_pic.file,
            public_id="profile_picture"+str(current_user.id),
            folder="kornekt-profile-pics",
            headers=headers
        )
        image_url = response.get("secure_url")
        db.query(models.User).filter(models.User.id == current_user.id).update({"name": name, "profile_pic": image_url}, synchronize_session=False)
        db.query(models.Post).filter(models.Post.user_id == current_user.id).update({"user_name": name})
    else:
        db.query(models.User).filter(models.User.id == current_user.id).update({"name": name}, synchronize_session=False)
        db.query(models.Post).filter(models.Post.user_id == current_user.id).update({"user_name": name})
    db.commit()
    db.refresh(user)
    return user

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    user_query = db.query(models.User).filter(models.User.id == current_user.id)
    user = user_query.first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = f'user with does not exist.')
    
    if user.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Not authorized to perform requested action!')
    
    user_query.delete(synchronize_session=False)
    db.commit()
    return {"message": f"user with was successfully deleted!"}