# Phase 1 – Order Service MVP

This document defines the complete scope, goals, and technical tasks for **Phase 1** of the Order & Notification Platform.

Phase 1 focuses on building a minimal, functional version of the system using a single microservice: **Order Service**.  
The goal is to establish the foundation for the entire platform before adding additional services, databases, or communication patterns.

---

## 1. Objectives

The primary goals of Phase 1 are:

1. Build a standalone Order Service with a clean internal structure.
2. Introduce PostgreSQL as the system's first database.
3. Provide a minimal REST API for creating and retrieving orders.
4. Establish basic observability: logs and health checks.
5. Set up a Docker-based local development environment.
6. Produce a foundation that will support additional microservices in later phases.

---

## 2. Deliverables

By the end of Phase 1, the system should include:

- A working **Order Service** with:
  - REST endpoints:
    - `POST /orders`
    - `GET /orders/{order_id}`
    - `GET /health`
  - Basic validation and error handling
  - Structured logging

- A PostgreSQL database running via Docker.

- A `docker-compose.yml` environment that starts:
  - PostgreSQL
  - The Order Service (running locally or in a container)

- A simple database schema:
  - `orders` table

- Documentation:
  - Instructions on how to run the service
  - SQL schema definition
  - API usage examples

---

## 3. Scope

### In Scope
- Building the Order Service (backend only)
- Setting up PostgreSQL
- Writing basic REST controllers
- Structuring the service (routes, handlers, services, repository layers)
- Writing the initial database schema
- Logging (stdout, JSON or simple structured logs)
- Adding health check endpoint
- Dockerizing the dependencies
- Documenting everything

### Out of Scope
The following items will be implemented only in later phases:
- User Service
- Activity Log Service
- Notification Service
- Inventory Service
- Message Queue (RabbitMQ / Redis Streams)
- NoSQL databases
- gRPC communication
- API Gateway
- Request ID propagation
- Authentication

---

## 4. Architecture Overview (Phase 1 Only)

Client (Postman) -> REST API -> Order Service -> PostgreSQL

There are no other services, no queues, and no asynchronous flows in Phase 1.

---

## 5. Technical Requirements

### 5.1. Language & Framework
- Python 3.x
- FastAPI or Flask (developer’s choice)

### 5.2. Database
- PostgreSQL 14+  
- Connection through SQLAlchemy / psycopg2 / asyncpg (choice left to developer)

### 5.3. API Endpoints

#### POST /orders
Creates a new order.

Request body (initial minimal version):
```json
{
  "user_id": 123,
  "product_id": 456,
  "quantity": 2
}
```
Response:
```json
{
  "order_id": 1,
  "status": "created"
}
```

#### GET /orders/{order_id}

Returns basic order information.

#### GET /health

Returns:
```json
{"status": "ok"}
```

### Database Schema

Minimal version for Phase 1:

```sql
CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'created',
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

## 7. Logging

The Order Service should produce structured logs written to stdout.

Required log fields:
- timestamp  
- level  
- message  
- service_name="order-service"

Example log:
2025-01-01T12:00:00Z INFO Created new order order_id=1 user_id=123

## 8. Tasks Breakdown

---
### Task 1: Initialize Project Structure

**Title:** Create base repository and folder structure  
**Description:**  
Set up the initial multi-service directory structure, including `order-service`, `infra`, and `docs`.

**Subtasks:**
- Initialize a new Git repository.
- Create directories:
  - `services/`
  - `services/order-service/`
  - `services/order-service/src/` with subfolders:
    - `routes/`
    - `models/`
    - `services/`
    - `repository/`
    - `config/`
  - `services/order-service/tests/`
  - `infra/db/init/`
  - `docs/`
- Create empty documentation files:
  - `docs/architecture.md`
  - `docs/phase1.md`

**Acceptance Criteria:**
- Repository structure matches the defined layout.
- Folder and file skeletons exist and are committed.

---

### Task 2: Document Initial Architecture

**Title:** Draft initial architecture document  
**Description:**  
Create a high-level architecture description covering the system's purpose, components, and Phase 1 scope.

**Must include:**
- System overview (Orders & Notifications platform)
- Current services (Order Service only for now)
- Chosen tech stack (Python, FastAPI, PostgreSQL, Docker)
- High-level request flow (Client → API → Order Service → DB)
- Notes about planned services (Notification Service, User Service, etc.)

**Acceptance Criteria:**
- `architecture.md` contains a clear and structured description.
- Document explains Phase 1 in context of the full system.

---

### Task 3: Bootstrap Order Service (FastAPI Skeleton)

**Title:** Implement Order Service skeleton with health endpoint  
**Description:**  
Create a minimal FastAPI application with environment-based settings and a basic health endpoint.

**Implementation details:**
- Add `requirements.txt` including:
  - fastapi
  - uvicorn
  - pydantic
  - psycopg2-binary or asyncpg
  - pytest
- Implement:
  - `src/main.py` → FastAPI app + `/health` endpoint
  - `src/config/settings.py` → Pydantic Settings loader using `.env`
- Run service with:
uvicorn src.main:app --reload

**Acceptance Criteria:**
- `/health` returns `200` and `{ "status": "ok" }`
- Application starts without errors
- `.env` settings load correctly

---

### Task 4: Create Orders Table (Database Schema)

**Title:** Define and create initial Orders table  
**Description:**  
Prepare the database schema and initialization SQL for the Order Service.

**Database fields (example):**
- `id` (UUID or SERIAL PK)
- `external_id` (optional)
- `customer_id`
- `status` (pending/confirmed/cancelled)
- `total_amount`
- `currency`
- `created_at`
- `updated_at`

**Files to create:**
- `infra/db/init/001_create_orders_table.sql`

**Acceptance Criteria:**
- SQL script exists and runs without errors
- Table is created successfully when DB container starts

---

### Task 5: Implement Order Model & Repository

**Title:** Implement domain model and DB repository  
**Description:**  
Add Pydantic model and repository layer for CRUD operations.

**Implementation details:**
- `models/order.py` → Pydantic model
- `repository/orders_repository.py`:
- `create_order(order)`
- `get_order_by_id(id)`
- Repository must use DB config from Settings

**Acceptance Criteria:**
- Code compiles and repository functions work with real DB
- No raw SQL inside routes (repository-only)

---

### Task 6: Implement Order API Endpoints

**Title:** Add HTTP endpoints for creating and fetching orders  
**Description:**  
Expose REST endpoints:

- `POST /api/v1/orders`
- `GET /api/v1/orders/{id}`

**Implementation details:**
- `routes/orders.py` → Router implementation
- `services/order_service.py` → Minimal business logic
- Register router in `main.py`

**Acceptance Criteria:**
- Creating an order persists it in DB
- Getting an order returns correct data or 404
- Endpoints tested manually with curl/Postman

---

### Task 7: Dockerize Order Service & Add Docker Compose

**Title:** Add Dockerfile and compose configuration  
**Description:**  
Containerize the service and create a multi-container setup for local development.

**compose should include:**
- `db` (PostgreSQL) with init scripts
- `order-service` container using Dockerfile
- Network configuration so app can reach DB

**Acceptance Criteria:**
- `docker-compose up` runs full environment
- Order Service connects to DB successfully
- `/health` and `/orders` endpoints work inside container

---

### Task 8: Add Tests & Developer Documentation

**Title:** Add basic tests and usage instructions  
**Description:**  
Ensure minimal test coverage and provide developer onboarding instructions.

**Implementation details:**
- `tests/test_health.py` → test `/health`
- `tests/test_orders_api.py` → basic CRUD flow
- Update `README.md` with:
- Setup instructions
- Running locally via Uvicorn
- Running via Docker Compose
- Running tests (`pytest`)

**Acceptance Criteria:**
- All Phase 1 tests pass
- README is clear, complete, and suitable for new developers

---

## 9. Completion Criteria

Phase 1 is complete when:

1. `docker-compose up` runs PostgreSQL successfully.
2. Order Service starts and connects to the database.
3. POST /orders works and creates an order.
4. GET /orders/{order_id} works and retrieves data.
5. The `orders` table stores data as expected.
6. Logs appear with a consistent format.
7. `GET /health` returns a valid JSON response.
8. Documentation includes setup instructions and API usage examples.
9. Codebase is structured for future services.

---

## 10. Next Phase

Phase 2 will introduce:

- User Service  
- REST communication between services  
- Separation of responsibilities  
- Updated Order creation flow (user validation)

Phase 1 must be complete before starting Phase 2.

## Progress Log
- Task 1 - done
- Task 2 - done
- Task 3 - done
- Task 4 - WIP
- Task 5 
- Task 6 
- Task 7 
- Task 8 
- Task 9  
- Task 10