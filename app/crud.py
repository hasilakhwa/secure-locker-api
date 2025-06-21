from sqlalchemy.orm import Session
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

from app.models import User, Secret
from app.schemas import UserCreate

# ----------------------------------------
# Load .env & initialize Fernet
# ----------------------------------------
load_dotenv()
encryption_key = os.getenv("ENCRYPTION_KEY")
fernet = Fernet(encryption_key.encode())

# ----------------------------------------
# Password Hashing
# ----------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ----------------------------------------
# User Management
# ----------------------------------------
def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

# ----------------------------------------
# Secret Management
# ----------------------------------------
def encrypt_content(content: str) -> str:
    return fernet.encrypt(content.encode()).decode()

def create_secret(db: Session, title: str, content: str, user_id: int):
    encrypted = encrypt_content(content)
    new_secret = Secret(title=title, content_encrypted=encrypted, user_id=user_id)
    db.add(new_secret)
    db.commit()
    db.refresh(new_secret)
    return new_secret

def delete_secret(db: Session, secret_id: int, user_id: int):
    secret = db.query(Secret).filter(Secret.id == secret_id, Secret.user_id == user_id).first()
    if not secret:
        return None
    db.delete(secret)
    db.commit()
    return secret

def update_secret(db: Session, secret_id: int, user_id: int, title: str, content: str):
    secret = db.query(Secret).filter(
        Secret.id == secret_id,
        Secret.user_id == user_id
    ).first()

    if not secret:
        return None

    secret.title = title
    secret.content_encrypted = encrypt_content(content)

    db.commit()
    db.refresh(secret)
    return secret
