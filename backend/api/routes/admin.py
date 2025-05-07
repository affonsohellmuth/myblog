# api/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List

from .. import auth, crud, schemas, models
from ..database import get_db
from fastapi.templating import Jinja2Templates

# Configuração de templates
templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/api/admin/posts", response_model=List[schemas.Post])
async def admin_get_posts(
    skip: int = 0, 
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para obter todos os posts (inclusive não publicados)
    para o administrador.
    """
    posts = crud.get_posts(db, skip=skip, limit=limit, published_only=False)
    return posts


@router.get("/api/admin/drafts", response_model=List[schemas.Post])
async def admin_get_drafts(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para obter todos os rascunhos do administrador
    """
    drafts = crud.get_drafts(db, current_user.id, skip=skip, limit=limit)
    return drafts


@router.post("/api/admin/posts", response_model=schemas.Post)
async def admin_create_post(
    post: schemas.PostCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para criar um novo post
    """
    # Criar um novo post associado ao usuário autenticado
    db_post = crud.create_post(db, post, current_user.id)
    return db_post


@router.put("/api/admin/posts/{post_id}", response_model=schemas.Post)
async def admin_update_post(
    post_id: int,
    post_update: schemas.PostUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para atualizar um post existente
    """
    # Verificar se o post existe
    db_post = crud.get_post(db, post_id)
    
    if not db_post:
        raise HTTPException(status_code=404, detail="Post não encontrado")
    
    # Verificar se o usuário autenticado é o autor do post
    if db_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    # Atualizar o post
    updated_post = crud.update_post(db, post_id, post_update)
    return updated_post


@router.delete("/api/admin/posts/{post_id}", response_model=dict)
async def admin_delete_post(
    post_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para excluir um post existente
    """
    # Verificar se o post existe
    db_post = crud.get_post(db, post_id)
    
    if not db_post:
        raise HTTPException(status_code=404, detail="Post não encontrado")
    
    # Verificar se o usuário autenticado é o autor do post
    if db_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    # Excluir o post
    result = crud.delete_post(db, post_id)
    
    if result:
        return {"message": "Post excluído com sucesso"}
    else:
        raise HTTPException(status_code=500, detail="Erro ao excluir o post")