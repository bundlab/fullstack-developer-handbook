# Chapter 06: PostgreSQL and Database Design

Relational database design serves as the foundation for enterprise application persistence, balancing strict data integrity with high-throughput query execution.

---

## 1. Entity-Relationship (ER) Modeling & Normalization

Database normalization systematically eliminates data redundancy, prevents update anomalies, and ensures data integrity through structured relations.

```
┌─────────────────┐       1 : N       ┌─────────────────┐       N : 1       ┌─────────────────┐
│     users       │───────────────────│     orders      │───────────────────│    products     │
├─────────────────┤                   ├─────────────────┤                   ├─────────────────┤
│ id (PK)         │                   │ id (PK)         │                   │ id (PK)         │
│ email           │                   │ user_id (FK)    │                   │ name            │
│ created_at      │                   │ status          │                   │ unit_price      │
└─────────────────┘                   └─────────────────┘                   └─────────────────┘

```

### The Three Core Normal Forms

1. **First Normal Form (1NF):**
* Every column contains atomic (indivisible) values.
* No repeating groups or array attributes stored in single fields.


2. **Second Normal Form (2NF):**
* Meets 1NF.
* All non-key attributes are fully dependent on the primary key (eliminates partial key dependencies on composite keys).


3. **Third Normal Form (3NF):**
* Meets 2NF.
* Eliminates transitive dependencies (non-key columns must not depend on other non-key columns).



---

## 2. PostgreSQL Indexing Strategies & Query Optimization

Indexes speed up read operations by providing fast data lookup mechanisms, but incur a small penalty on write operations (`INSERT`, `UPDATE`, `DELETE`).

```
                              ┌──────────────────┐
                              │  B-Tree Index    │
                              │   Root Node      │
                              └────────┬─────────┘
                                       │
                      ┌────────────────┴────────────────┐
                      ▼                                 ▼
             ┌─────────────────┐               ┌─────────────────┐
             │ Internal Node   │               │ Internal Node   │
             └────────┬────────┘               └────────┬────────┘
                      │                                 │
              ┌───────┴───────┐                 ┌───────┴───────┐
              ▼               ▼                 ▼               ▼
         ┌─────────┐     ┌─────────┐       ┌─────────┐     ┌─────────┐
         │ Leaf    │     │ Leaf    │       │ Leaf    │     │ Leaf    │
         │ (TID)   │     │ (TID)   │       │ (TID)   │     │ (TID)   │
         └─────────┘     └─────────┘       └─────────┘     └─────────┘

```

### PostgreSQL Index Types

* **B-Tree (Default):** Ideal for equality (`=`) and range queries (`<`, `<=`, `>`, `>=`, `BETWEEN`).
* **GIN (Generalized Inverted Index):** Optimized for composite items, `JSONB` document keys, and array containment (`@>`).
* **GiST / SP-GiST:** Designed for multi-dimensional spatial data (PostGIS geometry, ranges).
* **BRIN (Block Range Index):** Ultra-lightweight indexes for massive, sequentially appended time-series data.

```sql
-- Composite Index for multi-column filtering
CREATE INDEX idx_orders_user_status ON orders (user_id, status);

-- GIN Index for fast JSONB querying
CREATE INDEX idx_user_metadata_gin ON users USING GIN (metadata);

-- Query using JSONB operator
SELECT * FROM users WHERE metadata @> '{"role": "admin"}';

```

---

## 3. Transaction Guarantees: The ACID Model

Transactions ensure data safety and state consistency across concurrent operations.

* **Atomicity:** All operations within a transaction succeed completely or roll back entirely.
* **Consistency:** Transactions transition the database from one valid state to another, enforcing all schema constraints.
* **Isolation:** Concurrent transactions execute without interfering with one another based on chosen isolation levels.
* **Durability:** Committed transactions survive hardware or power failures via the Write-Ahead Log (WAL).

### Transaction Isolation Levels in PostgreSQL

| Isolation Level | Dirty Read | Non-Repeatable Read | Phantom Read | Serialization Anomaly |
| --- | --- | --- | --- | --- |
| **Read Committed** *(Default)* | Prevented | Allowed | Allowed | Allowed |
| **Repeatable Read** | Prevented | Prevented | Prevented | Allowed |
| **Serializable** | Prevented | Prevented | Prevented | Prevented |

---

## 4. Production DDL Schema Blueprint (`init.sql`)

```sql
-- Enable Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Domain Enums
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'completed', 'cancelled');

-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Orders Table
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_amount NUMERIC(12, 2) NOT NULL CHECK (total_amount >= 0),
    status order_status DEFAULT 'pending' NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Performance Optimization Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status_created ON orders(status, created_at DESC);

```

---

### Key Architectural Breakdown

1. **`CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`**
* **Why it matters**: Enables native UUID (Universally Unique Identifier) generation functions like `uuid_generate_v4()`.
* **Production benefit**: UUIDs eliminate predictable sequentially incrementing primary keys (`1, 2, 3...`), preventing enumeration security attacks and avoiding key collisions when scaling across distributed database clusters.


2. **Custom Domain Enum (`order_status`)**
* **Why it matters**: Enforces strict, type-safe data boundaries at the database layer rather than relying solely on application-level checks.
* **Production benefit**: Guarantees that no invalid status string (e.g., `'shipped_by_mistake'`) can ever be inserted into the `orders` table.


3. **Foreign Key Integrity & Cascading (`REFERENCES users(id) ON DELETE CASCADE`)**
* **Why it matters**: Establishes relational integrity between `orders` and `users`.
* **Production benefit**: The `ON DELETE CASCADE` rule automatically removes or cleans up orphaned child orders if a parent user record is explicitly deleted, preserving database consistency.


4. **Column Constraints (`CHECK`, `NOT NULL`, `DEFAULT`)**
* **`CHECK (total_amount >= 0)`**: Prevents logic bugs or malicious payloads from storing negative financial values.
* **`TIMESTAMPTZ`**: Stores timestamps with time zone awareness (`UTC`), avoiding daylight saving and regional time shift errors in distributed deployments.
* **`NOT NULL`**: Explicitly forbids `NULL` states on required fields to maintain data quality.


5. **Targeted Performance Indexes**
* **`idx_users_email`**: Accelerates single-user lookup during authentication (`WHERE email = ?`).
* **`idx_orders_status_created`**: A compound index optimized for admin dashboards filtering by order status sorted by recency (`WHERE status = 'pending' ORDER BY created_at DESC`).



---