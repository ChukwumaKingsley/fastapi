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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with this email already exists")
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/me", response_model = schemas.User)
def get_user(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"User with id {id} does not exist!")
    return user

@router.get("/user/{id}", response_model = schemas.User)
def get_user(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"User with id {id} does not exist!")
    return user

@router.get("/all", response_model=List[schemas.User])
def get_all_users(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    users = db.query(models.User).all()
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
def update_user(user_data: schemas.UserUpdate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()

    if user.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized to change another's details")

    for key, value in user_data.dict().items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user