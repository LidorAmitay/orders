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

### Task 1: Create project folder structure
services/
  order-service/
  activity-service/
  user-service/
  notification-service/
  inventory-service/
infra/
  docker-compose.yml
docs/
  architecture.md
  phase1.md


### Task 2: Create `docker-compose.yml`
- Add PostgreSQL container
- Expose port 5432
- Add volume for persistence
- Set environment variables (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB)

### Task 3: Implement Order Service skeleton
- Create `main.py`
- Add routing configuration
- Add basic application settings (environment-based)

### Task 4: Implement database connection layer
- Create a database module
- Initialize SQLAlchemy engine or psycopg2/asyncpg connection
- Add FastAPI startup/shutdown events if applicable

### Task 5: Apply the `orders` table schema
- Create SQL schema file
- Apply automatically on startup or manually with an init script

### Task 6: Implement POST /orders
- Validate request body
- Insert new order into the database
- Return created order ID and status

### Task 7: Implement GET /orders/{order_id}
- Query the database
- Return order information
- Return proper 404 if not found

### Task 8: Implement logging
- Create a simple logging utility
- Print structured logs for important actions:
  - Order creation
  - DB failures
  - Invalid input

### Task 9: Add health check endpoint
- Implement `GET /health`
- Return a JSON response indicating service status

### Task 10: Write documentation
- How to run docker-compose
- How to start the service locally
- Example API calls (curl/Postman)
- Schema overview

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
- Task 1 
- Task 2 
- Task 3 