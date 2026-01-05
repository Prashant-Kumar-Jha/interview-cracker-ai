from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models import User

# ✅ Use pbkdf2_sha256 (NO 72-byte limit)
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    password = password.strip()
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    plain = plain.strip()
    return pwd_context.verify(plain, hashed)

def register_user(db: Session, name: str, email: str, password: str):
    user = User(
        name=name,
        email=email,
        password=hash_password(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user
