from typing import List
from fastapi import Depends, HTTPException, status, APIRouter
from .. import models, schemas, utils, oauth2
from ..database import Session, get_db
from pydantic import EmailStr

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)



@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    #hash the password
    existing_user =  db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with email {user.email} already exist!")
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/user/{id}", response_model = schemas.User)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"User with id {id} does not exist!")
    return user

@router.get("/all", response_model=List[schemas.User])
def get_all_users(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    users = db.query(models.User).all()
    return users

@router.put("/change_password/{email}")
def update_password(email: EmailStr, UserData: schemas.PasswordUpdate, db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.email == email)
    user = user_query.first()
    
    if not user: #check if the user exists
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = f'User {email} does not exists.')
    if not utils.verify(UserData.old_password, user.password): #check if the old password is correct
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Incorrect old password!")
    
    UserData.password = utils.hash(UserData.password)
    password_update = {"password": UserData.password}

    user_query.update(password_update, synchronize_session = False)
    db.commit()
    return "Password was successfully changed"