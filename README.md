# Meu Blog Pessoal 📝

Este é um projeto que criei para praticar e me desafiar um pouco. Ao invés de fazer um CRUD genérico e sem propósito, decidi montar um **blog pessoal** onde posso postar artigos, opiniões e qualquer outra coisa que me der vontade.

## 💡 Motivação

Apesar de existirem várias soluções prontas para criar blogs, minha intenção aqui era **programar algo mais robusto** e que atendesse uma demanda minha. Foi uma forma de aprender na prática e desenvolver algo útil ao mesmo tempo.

## 🛠️ Tecnologias utilizadas

* **Back-end:** Python com FastAPI
* **Banco de dados:** PostgreSQL
* **Tabelas:** `posts`, `users` (no momento, apenas eu como usuário)
* **Front-end:** HTML, CSS e JavaScript puro

## 🔐 Autenticação

A autenticação é feita via **JWT**, garantindo que apenas usuários autenticados possam acessar determinadas rotas, como o painel administrativo.

## 🖥️ Painel Administrativo

Existe um **Dashboard** acessível apenas para o usuário administrador, permitindo:

* Criar, editar, publicar ou salvar posts como rascunho
* Fazer tudo isso diretamente pelo Front-end (sem precisar usar Postman ou editar o código)

Isso deixou o fluxo mais prático e ágil pra mim. 😄

## 🚧 Em desenvolvimento

O projeto ainda está em evolução. Pretendo adicionar novas funcionalidades e melhorar a estrutura com o tempo.
