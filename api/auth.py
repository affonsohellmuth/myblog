# api/auth.py
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import OAuth2PasswordBearer, OAuth2
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.utils import get_authorization_scheme_param
from typing import Dict, Optional
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.requests import Request

from . import models, schemas
from .database import get_db

# Carregar as variáveis do .env
load_dotenv()

# Agora, a SECRET_KEY será lida a partir do .env
SECRET_KEY = os.getenv("SECRET_KEY")  # Obter a chave do arquivo .env
ALGORITHM = os.getenv("ALGORITHM", "HS256")  # Carregar o algoritmo com valor padrão, se necessário
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))  # Definir o tempo de expiração

# Adicionando o print para verificar se a chave foi carregada corretamente
print(f"SECRET_KEY: {SECRET_KEY}")  # Isso irá imprimir a chave carregada do .env

# Instância para verificação de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Classe personalizada para OAuth2 que verifica tanto o header quanto o cookie
class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        # Primeiro tenta obter o token do header Authorization
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        
        # Se não encontrar no header, tenta obter do cookie
        if not authorization or scheme.lower() != "bearer":
            # Tenta obter do cookie
            cookie_authorization: str = request.cookies.get("access_token")
            if cookie_authorization:
                scheme, param = get_authorization_scheme_param(cookie_authorization)
        
        # Se não encontrou em nenhum lugar ou o esquema não é bearer, retorna erro
        if not authorization and not cookie_authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Não autenticado",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        
        # Retorna o token encontrado (do header ou do cookie)
        return param

# OAuth2 com suporte a senha e cookie
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Aqui é onde a SECRET_KEY é usada para criar o JWT

    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    print(f"Token recebido: {token}")  # Verifique o token aqui
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        print(f"Username extraído do token: {username}")  # Verifique o username extraído do token
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        print("Erro ao decodificar token")  # Verifique o erro
        raise credentials_exception
        
    user = get_user(db, username=token_data.username)
    if user is None:
        print("Usuário não encontrado no banco de dados")
        raise credentials_exception
        
    return user


async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    return current_user