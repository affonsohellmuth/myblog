# api/crud.py
from sqlalchemy.orm import Session
from typing import List, Optional

from . import models, schemas, auth


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_posts(db: Session, skip: int = 0, limit: int = 100, published_only: bool = True):
    query = db.query(models.Post)
    
    if published_only:
        query = query.filter(models.Post.is_published == True)
    
    return query.order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()


def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()


def create_post(db: Session, post: schemas.PostCreate, user_id: int):
    db_post = models.Post(**post.dict(), author_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def update_post(db: Session, post_id: int, post_update: schemas.PostUpdate):
    db_post = get_post(db, post_id)
    
    if not db_post:
        return None
    
    update_data = post_update.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_post, key, value)
    
    db.commit()
    db.refresh(db_post)
    return db_post


def delete_post(db: Session, post_id: int):
    db_post = get_post(db, post_id)
    
    if not db_post:
        return False
    
    db.delete(db_post)
    db.commit()
    return True


def get_drafts(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Post)
        .filter(models.Post.author_id == user_id, models.Post.is_published == False)
        .order_by(models.Post.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )