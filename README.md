# 🔐 Secure Locker API

A FastAPI-based secure locker backend where users can register, login, and store encrypted secrets securely.

## 🚀 Features
- User Registration & Login (JWT-based)
- Encrypted secret storage using `cryptography`
- JWT Authentication
- SQLite database
- REST API with Swagger UI

## 🔧 Technologies Used
- FastAPI
- SQLAlchemy
- SQLite
- Cryptography (Fernet)
- JWT (Python-JOSE)
- Passlib (Bcrypt)
- Uvicorn
- uv (dependency management)

## 📦 Installation

```bash
uv venv
uv pip install -r uv.lock

Note: You must have uv installed. Get it here: https://github.com/astral-sh/uv

🛠 .env File Setup
Create a .env file in root with the following:

env
Copy
Edit
DATABASE_URL=sqlite:///./securelocker.db
ENCRYPTION_KEY=<your_fernet_key>
SECRET_KEY=<your_jwt_secret>

▶️ Running the API
bash
Copy
Edit
uvicorn app.main:app --reload
Visit: http://localhost:8000/docs

🔐 Swagger Auth Instructions
Register via /register

Login via /login (use form)

Copy access_token from response

Click Authorize in Swagger and paste token as:

php-template
Copy
Edit
Bearer <token>
📂 Folder Structure
pgsql
Copy
Edit
.
├── app/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── db.py
│   ├── crud.py
│   ├── auth.py
├── .env
├── uv.lock
├── pyproject.toml
├── README.md