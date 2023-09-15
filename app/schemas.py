from typing import Optional
from pydantic import BaseModel, EmailStr, conint, field_validator
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
    # dir: conint(ge=0, le=1)
    dir: int
    
    @field_validator("dir")
    def validate_dir(cls, value):
        if value not in (0, 1):
            raise ValueError("Vote 'dir' must be either 0 or 1")
        return value
