from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

from app.db import SessionLocal, engine, Base, get_db
from app import models, schemas, crud
from app.auth import create_access_token, get_current_user
from app.models import Secret

load_dotenv(dotenv_path=".env")
Base.metadata.create_all(bind=engine)

app = FastAPI()

# ----------------------------------------
# Utility: DB session dependency
# ----------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------------------
# Root
# ----------------------------------------
@app.get("/")
def root():
    return {"message": "Secure Locker API is running"}

# ----------------------------------------
# User Registration & Login
# ----------------------------------------
@app.post("/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ----------------------------------------
# Secrets CRUD
# ----------------------------------------
@app.post("/secrets")
def create_secret(
    secret: schemas.SecretCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_secret(
        db=db,
        title=secret.title,
        content=secret.content,
        user_id=current_user.id
    )

@app.get("/secrets")
def read_secrets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    encryption_key = os.getenv("ENCRYPTION_KEY")
    if not encryption_key:
        raise HTTPException(status_code=500, detail="ENCRYPTION_KEY is missing or not loaded")

    fernet = Fernet(encryption_key.encode())
    secrets = db.query(Secret).filter(Secret.user_id == current_user.id).all()

    result = []
    for secret in secrets:
        decrypted = fernet.decrypt(secret.content_encrypted.encode()).decode()
        result.append({
            "id": secret.id,
            "title": secret.title,
            "content": decrypted
        })

    return result

@app.delete("/secrets/{secret_id}")
def delete_secret(
    secret_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    deleted = crud.delete_secret(db=db, secret_id=secret_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Secret not found")
    return {"message": "Secret deleted successfully"}

@app.put("/secrets/{secret_id}")
def update_secret(
    secret_id: int,
    secret_update: schemas.SecretUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    updated = crud.update_secret(
        db=db,
        secret_id=secret_id,
        user_id=current_user.id,
        title=secret_update.title,
        content=secret_update.content
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Secret not found")

    return {"message": "Secret updated successfully"}
