"""
Chapter 05 Lab: Production Authentication & Role-Based Access Control (RBAC)
FastAPI application with JWT generation, password hashing, and endpoint security.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

# ---------------------------------------------------------------------------
# Security & Auth Setup
# ---------------------------------------------------------------------------
SECRET_KEY = "lab-super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# Mock In-Memory User Database for Lab Demo
fake_users_db = {
    "admin_alex": {
        "user_id": "usr_001",
        "username": "admin_alex",
        "email": "alex@example.com",
        "hashed_password": pwd_context.hash("AdminSecret123!"),
        "role": "admin",
    },
    "user_sarah": {
        "user_id": "usr_002",
        "username": "user_sarah",
        "email": "sarah@example.com",
        "hashed_password": pwd_context.hash("UserSecret123!"),
        "role": "user",
    },
}

# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    user_id: str
    role: str

class UserProfile(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    role: str

# ---------------------------------------------------------------------------
# Auth Helper Functions & Dependencies
# ---------------------------------------------------------------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None or role is None:
            raise credentials_exception
        return TokenPayload(user_id=user_id, role=role)
    except jwt.PyJWTError:
        raise credentials_exception

def require_role(required_role: str):
    """Higher-order dependency for Role-Based Access Control (RBAC)."""
    def role_checker(current_user: TokenPayload = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Requires '{required_role}' role privileges.",
            )
        return current_user

    return role_checker

# ---------------------------------------------------------------------------
# FastAPI Router
# ---------------------------------------------------------------------------
app = FastAPI(title="Lab 05: Auth & Security Engine", version="1.0.0")

@app.post("/api/v1/auth/token", response_model=TokenResponse, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user["user_id"], "role": user["role"]}
    )
    return TokenResponse(access_token=access_token)

@app.get("/api/v1/users/me", response_model=UserProfile, tags=["User Profile"])
async def read_current_user_profile(current_user: TokenPayload = Depends(get_current_user)):
    # Look up user record from token payload
    for user in fake_users_db.values():
        if user["user_id"] == current_user.user_id:
            return UserProfile(**user)
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/api/v1/admin/dashboard", tags=["Admin Portal"])
async def get_admin_metrics(
    admin_user: TokenPayload = Depends(require_role("admin")),
):
    return {
        "message": "Welcome to the Secure Admin Console",
        "admin_id": admin_user.user_id,
        "system_status": "All security perimeters operational",
    }
