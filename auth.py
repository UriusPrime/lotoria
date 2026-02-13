from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User

# --- Config ---
SECRET_KEY = "CHANGE_THIS_LATER"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

# --- Password hashing (argon2 to avoid bcrypt 72-byte limit) ---
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- Database session ---
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Hash & verify ---
def hash_password(password: str) -> str:
    """
    Hash a password using argon2.
    Truncates to 256 characters just in case (very generous).
    """
    truncated = password[:256]
    return pwd_context.hash(truncated)

def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against a hashed value.
    Truncate input for safety.
    """
    truncated = password[:256]
    return pwd_context.verify(truncated, hashed)

# --- JWT token ---
def create_access_token(user_id: int) -> str:
    """
    Create a JWT access token for a user.
    """
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# --- Current user ---
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Decode JWT token and retrieve current user from DB.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user