# Blog Pessoal

Um blog pessoal desenvolvido com FastAPI, SQLAlchemy e templates Jinja2.

Este é um projeto que criei para praticar e me desafiar um pouco. Ao invés de fazer um CRUD genérico e sem propósito, decidi montar um blog pessoal onde posso postar artigos, opiniões e qualquer outra coisa que me der vontade.

## Motivação

Apesar de existirem várias soluções prontas para criar blogs, minha intenção aqui era programar algo mais robusto e que atendesse uma demanda minha. Foi uma forma de aprender na prática e desenvolver algo útil ao mesmo tempo.


## Estrutura do Projeto

O projeto está organizado em duas partes principais:

- **Backend**: Contém a API e a lógica de negócios
- **Frontend**: Contém os templates HTML e arquivos estáticos

```
my_blog/
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── admin.py
│   │   │   ├── auth.py
│   │   │   └── posts.py
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── crud.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── schemas.py
│   └── main.py
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── js/
│   │       ├── admin.js
│   │       └── login.js
│   └── templates/
│       ├── admin/
│       │   ├── dashboard.html
│       │   ├── edit-post.html
│       │   └── login.html
│       ├── 404.html
│       ├── index.html
│       ├── post.html
│       └── sobre.html
├── .env
└── requirements.txt
```

## Funcionalidades

- Visualização de posts
- Página "Sobre"
- Painel administrativo
- Autenticação JWT
- CRUD de posts
- Rascunhos e publicação de posts

## Tecnologias Utilizadas

- **Backend**: FastAPI, SQLAlchemy, Pydantic, JWT
- **Frontend**: HTML, CSS, JavaScript
- **Banco de Dados**: PostgreSQL
