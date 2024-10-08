from typing import Optional
from fastapi import UploadFile
from pydantic import BaseModel, EmailStr, conint, field_validator
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserBase(UserCreate):
    id: int
    created_at: datetime

class User(BaseModel):
    email: EmailStr
    id: int
    created_at: datetime
    name: str
    password: str
    profile_pic: Optional[str] = None
    class config: 
        orm_mode = True

class UsersData(User):
    current_user: bool
        
class UserOut(User):
    votes_count: int
    downvotes_count: int
    posts_count: int

class UserLogin(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    name: str
    profile_pic: Optional[UploadFile] = None

class UserUpdated(BaseModel):
    name: str
    profile_pic: Optional[str] = None
    email: EmailStr
    id: int


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    created_at: datetime
    user_id: int
    owner: User
    class config:
        orm_mode = True


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    # dir: conint(ge=0, le=1)
    dir: int
    
    @field_validator("dir")
    def validate_dir(cls, value):
        if value not in (0, 1):
            raise ValueError("Vote 'dir' must be either 0 or 1")
        return value

class Counts(BaseModel):
    counts: int
    
class DownVote(BaseModel):
    post_id: int
    # dir: conint(ge=0, le=1)
    dir: int
    
    @field_validator("dir")
    def validate_dir(cls, value):
        if value not in (0, 1):
            raise ValueError("Vote 'dir' must be either 0 or 1")
        return value
