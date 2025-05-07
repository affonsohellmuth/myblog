# api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.responses import RedirectResponse

from .. import auth, crud, schemas
from ..database import get_db
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

# Obter duração do token
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

router = APIRouter()


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Log para depuração
    print(f"Tentativa de login para: {form_data.username}")
    print(f"Valor de ACCESS_TOKEN_EXPIRE_MINUTES: {ACCESS_TOKEN_EXPIRE_MINUTES}")
    
    # Autenticar usuário
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Criar token de acesso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Log do token gerado para depuração
    print(f"Token gerado para: {user.username}")
    print(f"Token: {access_token}")
    
    # Definir o cookie de autenticação
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,  # Não acessível via JavaScript
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False  # Definir como True em produção com HTTPS
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/api/admin/validate-token", response_model=schemas.User)
async def validate_token(current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Endpoint para validar o token JWT e retornar informações do usuário.
    Só será bem-sucedido se o token for válido.
    """
    return current_user