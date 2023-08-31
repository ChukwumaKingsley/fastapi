from typing import Optional
from pydantic import BaseModel, EmailStr, conint
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserBase(UserCreate):
    id: int
    created_at: datetime

class User(BaseModel):
    email: EmailStr
    id: int
    created_at: datetime
    class config: 
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

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

class PostOut(BaseModel):
    Post: Post
    votes: int
    class config:
        orm_mode = True

class PasswordUpdate(BaseModel):
    old_password: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)
