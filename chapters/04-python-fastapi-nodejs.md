# Chapter 04: Python / FastAPI / Node.js

Modern backend systems require high throughput, low latency execution, efficient handling of concurrent I/O operations, and strong contract definitions.

---

## 1. Asynchronous I/O Mechanisms

Both FastAPI (via Python's `asyncio`) and Node.js (via its C-based Event Loop & `libuv`) rely on non-blocking I/O to handle thousands of concurrent requests on single-threaded event loops without blocking main execution threads.

```
┌────────────────────────────────────────────────────────┐
│                   Incoming HTTP Request                │
└───────────────────────────┬────────────────────────────┘
                            │
              ┌─────────────▼─────────────┐
              │    Event Loop Dispatcher  │
              └─────────────┬─────────────┘
                            │
         ┌──────────────────┴──────────────────┐
         │                                     │
         ▼                                     ▼
┌─────────────────┐                   ┌─────────────────┐
│ Async I/O Task  │                   │ Async I/O Task  │
│ (DB Query,      │                   │ (External API,  │
│  File Read)     │                   │  Redis Cache)   │
└────────┬────────┘                   └────────┬────────┘
         │                                     │
         └──────────────────┬──────────────────┘
                            │
              ┌─────────────▼─────────────┐
              │ Non-blocking Response     │
              └───────────────────────────┘

```

> **Key Rule:** Never execute CPU-bound computation synchronously inside an `async` route handler—it freezes the event loop for all concurrent users. For heavy computations, offload to worker queues (e.g., Celery, Redis Streams) or process pools.

---

## 2. Python & FastAPI Backend Engineering

FastAPI leverages Python type hints and Pydantic for high-speed serialization, automatic validation, and native OpenAPI/Swagger documentation generation.

### Production Pattern: Dependency Injection & Async SQLAlchemy

```python
import time
from typing import AsyncGenerator
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Database Configuration
DATABASE_URL = "sqlite+aiosqlite:///./app.db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True)

# Dependency Injection for Database Session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# Pydantic Schemas for Request/Response Contracts
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

app = FastAPI(title="Async FastAPI Service", version="1.0.0")

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = UserModel(username=user_in.username, email=user_in.email)
    db.add(db_user)
    try:
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists")

```

---

## 3. Node.js Architecture & Runtime Execution

Node.js executes JavaScript on Google's V8 engine and handles asynchronous I/O via `libuv`.

### Production Pattern: Express + TypeScript Architecture

```typescript
import express, { Request, Response, NextFunction } from 'express';

interface CreateOrderRequest {
  itemId: string;
  quantity: number;
  unitPrice: number;
}

const app = express();
app.use(express.json());

// Async Error Handling Middleware Wrapper
const asyncHandler = (fn: Function) => (req: Request, res: Response, next: NextFunction) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

// Route Handler
app.post(
  '/api/v1/orders',
  asyncHandler(async (req: Request<{}, {}, CreateOrderRequest>, res: Response) => {
    const { itemId, quantity, unitPrice } = req.body;

    if (!itemId || quantity <= 0) {
      return res.status(400).json({ error: 'Invalid order parameters' });
    }

    const totalAmount = quantity * unitPrice;
    
    // Simulate non-blocking DB insertion
    await new Promise((resolve) => setTimeout(resolve, 50));

    res.status(201).json({
      orderId: `ord_${Date.now()}`,
      itemId,
      totalAmount,
      status: 'pending',
    });
  })
);

// Global Error Middleware
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error('[Error Pipeline]:', err.stack);
  res.status(500).json({ error: 'Internal Server Error' });
});

```

---

## 4. Framework Comparison Matrix

| Feature | Python / FastAPI | Node.js / Express / NestJS |
| --- | --- | --- |
| **Primary Language** | Python 3.10+ | TypeScript / JavaScript |
| **Concurrency Model** | `asyncio` Event Loop | `libuv` Event Loop |
| **Validation & Schemas** | Pydantic (Type hints) | Zod / class-validator |
| **Auto API Docs** | OpenAPI (Swagger) built-in | Swagger module integration required |
| **Best Use Cases** | Data Pipelines, AI/ML Services, High-Performance APIs | Real-time WebSockets, Microservices, I/O Heavy Apps |

---

## 🧪 Practical Lab Exercise: FastAPI Server Entrypoint (`labs/backend/app/main.py`)

### Goal

Implement the core entrypoint for the lab backend using FastAPI. It will include dynamic health probes, request latency tracking, and CORS support.
