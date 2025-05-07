# api/routes/posts.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter()


@router.get("/posts/", response_model=List[schemas.Post])
def read_posts(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Retorna todos os posts publicados, visíveis para o público
    """
    posts = crud.get_posts(db, skip=skip, limit=limit, published_only=True)
    return posts


@router.get("/posts/{post_id}", response_model=schemas.Post)
def read_post(post_id: int, db: Session = Depends(get_db)):
    """
    Retorna um post específico, verificando se ele está publicado
    """
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post não encontrado")
    
    # Se o post não está publicado, não deve ser visível publicamente
    if not db_post.is_published:
        raise HTTPException(status_code=404, detail="Post não encontrado")
    
    return db_post