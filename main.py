# main.py
import os
import logging
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime

from api import models, crud, schemas, auth
from api.database import engine, get_db
from api.routes import auth as auth_routes
from api.routes import posts as posts_routes
from api.routes import admin as admin_routes
from dotenv import load_dotenv

load_dotenv()

models.Base.metadata.create_all(bind=engine)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Blog Pessoal API")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_routes.router, tags=["auth"])
app.include_router(posts_routes.router, tags=["posts"])
app.include_router(admin_routes.router, tags=["admin"])

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    posts = crud.get_posts(db, published_only=True)
    current_year = datetime.now().year
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "posts": posts, "year": current_year}
    )

@app.get("/post/{post_id}", response_class=HTMLResponse)
async def view_post(post_id: int, request: Request, db: Session = Depends(get_db)):
    post = crud.get_post(db, post_id)
    if not post or not post.is_published:
        return templates.TemplateResponse(
            "404.html", 
            {"request": request}
        )
    current_year = datetime.now().year
    return templates.TemplateResponse(
        "post.html", 
        {"request": request, "post": post, "year": current_year}
    )

@app.get("/sobre", response_class=HTMLResponse)
async def sobre(request: Request):
    current_year = datetime.now().year
    return templates.TemplateResponse(
        "sobre.html", 
        {"request": request, "year": current_year}
    )

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(
    request: Request,
    current_user: models.User = Depends(auth.get_current_active_user)
):

    return templates.TemplateResponse(
        "admin/dashboard.html", 
        {"request": request, "user": current_user}
    )

@app.get("/admin/edit-post/{post_id}", response_class=HTMLResponse)
async def admin_edit_post(
    post_id: int,
    request: Request,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post não encontrado")
    
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    return templates.TemplateResponse(
        "admin/edit-post.html", 
        {"request": request, "user": current_user, "post": post}
    )

@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login(request: Request):
    return templates.TemplateResponse(
        "admin/login.html", 
        {"request": request}
    )

@app.on_event("startup")
async def startup_db_client():
    db = next(get_db())
    try:
        admin_user = crud.get_user_by_username(db, "admin")
        
        if not admin_user:
            logger.info("Criando usuário administrador padrão...")
            
            admin_password = os.getenv("ADMIN_PASSWORD", "a12053637")
            
            admin_user = schemas.UserCreate(
                username="admin",
                email="admin@myblog.com",
                password=admin_password
            )
            
            crud.create_user(db, admin_user)
            logger.info("Usuário administrador criado com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao inicializar o banco de dados: {str(e)}")
    finally:
        db.close()