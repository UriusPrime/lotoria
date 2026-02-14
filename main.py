from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine
from models import User, PlayerSave
from schemas import RegisterRequest, LoginRequest, TokenResponse
from auth import (
    get_db, hash_password, verify_password,
    create_access_token
)
from save_routes import router as save_router


# ------------------------------------------------------------------
# Database (CREATE TABLES ON STARTUP)
# ------------------------------------------------------------------
Base.metadata.create_all(bind=engine)


# ------------------------------------------------------------------
# App
# ------------------------------------------------------------------
app = FastAPI(title="Game Backend")


# ------------------------------------------------------------------
# CORS (Unity / Android)
# ------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------
# Health check (Render relies on this)
# ------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# ------------------------------------------------------------------
# Auth
# ------------------------------------------------------------------
@app.post("/auth/register", response_model=TokenResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username exists")

    user = User(
        username=data.username,
        password_hash=hash_password(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return {"access_token": token}


@app.post("/auth/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.id)
    return {"access_token": token}


# ------------------------------------------------------------------
# Save routes
# ------------------------------------------------------------------
app.include_router(save_router, prefix="/save")