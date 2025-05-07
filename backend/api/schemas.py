# api/schemas.py
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class PostBase(BaseModel):
    title: str
    content: str
    is_published: bool = False


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_published: Optional[bool] = None


class Post(PostBase):
    id: int
    created_at: datetime
    updated_at: datetime
    author_id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None  # Torna o campo email opcional

class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    posts: List[Post] = []

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None