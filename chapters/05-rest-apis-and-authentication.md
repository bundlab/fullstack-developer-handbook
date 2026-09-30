# Chapter 05: REST APIs and Authentication

Building robust backend APIs requires strict adherence to architectural constraints, clear contract schemas, secure authentication flows, and fine-grained authorization mechanisms.

---

## 1. RESTful API Architecture Principles

Representational State Transfer (REST) is an architectural style designed around stateless communication and resource manipulation via standard HTTP methods.

```
Client                                  Server
  │                                       │
  │─── POST /api/v1/orders ──────────────►│ (Create Resource)
  │◄── 201 Created { "id": "ord_101" } ───│
  │                                       │
  │─── GET /api/v1/orders/ord_101 ────────►│ (Read Resource)
  │◄── 200 OK { "status": "shipped" } ────│
  │                                       │
  │─── PUT /api/v1/orders/ord_101 ────────►│ (Replace Resource)
  │◄── 200 OK { "status": "delivered" } ──│
  │                                       │
  │─── DELETE /api/v1/orders/ord_101 ─────►│ (Delete Resource)
  │◄── 204 No Content ────────────────────│

```

### HTTP Method Mapping & Idempotency

| Method | Resource Action | Primary Success Status | Idempotent? | Safe? |
| --- | --- | --- | --- | --- |
| **GET** | Retrieve resource | `200 OK` | Yes | Yes |
| **POST** | Create new resource | `201 Created` | No | No |
| **PUT** | Replace existing resource completely | `200 OK` / `204 No Content` | Yes | No |
| **PATCH** | Partial update of existing resource | `200 OK` | No | No |
| **DELETE** | Remove resource | `200 OK` / `204 No Content` | Yes | No |

---

## 2. Authentication vs. Authorization

```
┌─────────────────────────────────────────────────────────────┐
│                    Authentication (Who are you?)             │
│   Verifies user identity via Credentials, Passwords, or Tokens│
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Authorization (What can you do?)          │
│   Verifies access permissions via Roles, Claims, or Scopes  │
└─────────────────────────────────────────────────────────────┘

```

* **Authentication (AuthN):** The process of verifying *who* a user is (e.g., login with email/password, OAuth2 social login).
* **Authorization (AuthZ):** The process of determining *what* actions an authenticated user can perform (e.g., Role-Based Access Control / RBAC).

---

## 3. JSON Web Tokens (JWT) & Stateless Auth

JWTs allow stateless authorization between parties by signing a JSON payload containing claims.

```
  Header (Algorithm & Type)        Payload (Claims & Expiry)          Signature
┌───────────────────────────┐   ┌───────────────────────────┐   ┌───────────────────┐
│ { "alg": "HS256",         │ . │ { "sub": "usr_99",        │ . │ HMACSHA256(       │
│   "typ": "JWT" }          │   │   "role": "admin",        │   │   base64UrlHeader +│
└───────────────────────────┘   │   "exp": 1700000000 }     │   │   "." +           │
                                └───────────────────────────┘   │   base64UrlPayload,│
                                                                │   secretKey)      │
                                                                └───────────────────┘

```

### Password Hashing Security Best Practices

* **Never store plaintext passwords.**
* Use slow, adaptive hashing algorithms with automatically generated salts:
* **Argon2id** (Recommended)
* **bcrypt** (Cost factor $\ge 12$)
* **PBKDF2**



---

## 4. Production Authentication & Authorization Workflow

In a modern production FastAPI application, user authentication and access control are handled through a multi-layered security pipeline:

1. **Password Hashing & Verification (`CryptContext`)**:
Passlib with `bcrypt` safely hashes plaintext passwords before storing them in the database. When a user logs in, their input is hashed and verified against the stored hash without ever persisting or transmitting raw credentials.

2. **JWT Generation (`create_access_token`)**:
Upon successful credential validation, the server issues a signed, time-limited JSON Web Token (JWT). The token payload carries non-sensitive identity claims (such as `user_id` and `role`) alongside an explicit expiration timestamp (`exp`).

3. **Bearer Token Extraction (`OAuth2PasswordBearer`)**:
FastAPI's built-in `OAuth2PasswordBearer` security scheme automatically inspects incoming HTTP requests for the standard `Authorization: Bearer <token>` header, extracting the raw JWT for validation.

4. **Stateless Claims Verification (`get_current_user`)**:
The `get_current_user` dependency decodes and validates the signature of incoming JWTs using a server-side secret key. If the token has expired or been tampered with, an immediate `HTTP 401 Unauthorized` response is thrown before request execution reaches the route handler.

5. **Role-Based Access Control / RBAC (`require_role`)**:
A higher-order dependency wrapper allows endpoint authorization based on user roles (e.g., `admin`, `editor`, `user`). If an authenticated user attempts to access a resource restricted to a higher permission level, a strict `HTTP 403 Forbidden` response is returned.

---

### Production API Auth Implementation Pattern (FastAPI)

```python
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

# Configuration
SECRET_KEY = "prod-super-secret-key-change-in-env"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

class TokenData(BaseModel):
    user_id: str
    role: str

# Password Utilities
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# JWT Utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Role-Based Access Control (RBAC) Dependency
async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
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
        return TokenData(user_id=user_id, role=role)
    except jwt.PyJWTError:
        raise credentials_exception

def require_role(required_role: str):
    def role_checker(current_user: TokenData = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this resource"
            )
        return current_user
    return role_checker

```

---