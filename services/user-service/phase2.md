# Phase 2 – Multi-Service Foundation (Order + User Services)

This document defines the scope, goals, and technical tasks for **Phase 2** of the Orders & Notifications Platform.

Phase 2 transitions the system from a **single-service MVP** into a **true multi-service architecture**.
The focus is on **service boundaries, inter-service communication, and responsibility separation**.

---

## 1. Objectives

The primary goals of Phase 2 are:

1. Introduce a new **User Service** as an independent microservice.
2. Enforce clear ownership of data and responsibilities per service.
3. Enable **synchronous REST communication** between services.
4. Update Order creation flow to validate users via User Service.
5. Strengthen architectural discipline (no shared DBs, no tight coupling).
6. Prepare the system for asynchronous/event-driven patterns in Phase 3.

---

## 2. Deliverables

By the end of Phase 2, the system should include:

- Two independent microservices:
  - **Order Service**
  - **User Service**

- Each service has:
  - Its own database schema
  - Its own API
  - Its own Docker container

- Updated Order creation flow:
  - Order Service validates user existence via User Service API

- Updated docker-compose environment:
  - PostgreSQL (shared instance, separate schemas or databases)
  - Order Service
  - User Service

- Documentation describing:
  - Service responsibilities
  - Inter-service communication
  - Updated request flows

---

## 3. Scope

### In Scope
- User Service implementation
- REST-based service-to-service communication
- Order creation validation against User Service
- Error propagation between services
- Docker Compose updates
- Architecture & API documentation

### Out of Scope
- Message queues / async events
- Authentication / authorization
- API Gateway
- Caching
- Observability stack (metrics, tracing)
- Kubernetes

---

## 4. Architecture Overview (Phase 2)

Client  
→ Order Service  
→ (REST) User Service  
→ PostgreSQL  

Key rules:
- No service accesses another service’s database
- Communication happens only via HTTP APIs
- Each service owns its data model

---

## 5. Services Overview

### 5.1 Order Service

**Responsibilities:**
- Create and retrieve orders
- Validate business rules related to orders
- Validate user existence via User Service

**Does NOT:**
- Store user data
- Know user schema or DB structure

---

### 5.2 User Service

**Responsibilities:**
- Manage users
- Expose user data via REST API

**Does NOT:**
- Know anything about orders

---

## 6. API Definitions

### User Service API

#### POST /api/v1/users
Creates a new user.

Request:
```json
{
  "email": "user@example.com",
  "name": "John Doe"
}
```
Response:
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe"
}
```
#### GET /api/v1/users/{user_id}
Response:
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe"
}
```
Returns 404 if user not found.

### 6.2 Order Service (Updated)

#### POST /api/v1/orders

**Flow:**
1. Receive order request
2. Call User Service: `GET /api/v1/users/{user_id}`
3. If user exists → create order
4. If user does not exist → return error

Request:
```json
{
  "user_id": 1,
  "product_id": 456,
  "quantity": 2
}
```

Possible Errors:
- `404 User not found`
- `503 User service unavailable`

---

## 7. Database Schema

### 7.1 Users Table (User Service)

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### 7.2 Orders Table

Same schema as defined in Phase 1.

---

## 8. Tasks Breakdown

### Task 1: Create User Service Skeleton

**Description:**  
Create a new `user-service` microservice following the same conventions and structure as `order-service`.

**Implementation details:**
- Create directory: `services/user-service`
- Add subfolders:
  - `routes/`
  - `services/`
  - `repository/`
  - `models/`
  - `config/`
- Add `main.py` with FastAPI app
- Add `/health` endpoint
- Add Pydantic Settings for env config

**Acceptance Criteria:**
- User Service runs independently
- `/health` returns `{ "status": "ok" }`

---

### Task 2: Implement Users Table

**Description:**  
Define and initialize the database schema for User Service.

**Implementation details:**
- Create SQL file: `infra/db/init/002_create_users_table.sql`
- Use separate table owned only by User Service
- Do not modify existing orders schema

**Acceptance Criteria:**
- Users table is created on DB startup
- No impact on Order Service tables

---

### Task 3: Implement User CRUD API

**Description:**  
Expose minimal REST API for user management.

**Endpoints:**
- `POST /api/v1/users`
- `GET /api/v1/users/{id}`

**Implementation details:**
- Pydantic models for request/response
- Repository layer for DB access
- Service layer for business logic
- Proper HTTP status codes (201, 404)

**Acceptance Criteria:**
- Users can be created and retrieved
- 404 returned when user does not exist

---

### Task 4: Service-to-Service Communication

**Description:**  
Integrate Order Service with User Service via REST.

**Implementation details:**
- Add HTTP client (`httpx` or `requests`)
- Configurable User Service base URL
- Add timeout and basic error handling
- Call User Service before order creation

**Acceptance Criteria:**
- Order creation fails if user does not exist
- Order Service does not access users DB directly

---

### Task 5: Error Handling & Resilience

**Description:**  
Handle downstream User Service failures gracefully.

**Scenarios to handle:**
- User Service unavailable
- Request timeout
- Invalid response payload

**Implementation details:**
- Map downstream errors to meaningful API responses
- Avoid crashing Order Service

**Acceptance Criteria:**
- Clear error responses returned to client
- Order Service remains stable under failures

---

### Task 6: Update Docker Compose

**Description:**  
Run Order Service and User Service together locally.

**Implementation details:**
- Add User Service container to `docker-compose.yml`
- Ensure network connectivity between services
- Use environment variables for service URLs

**Acceptance Criteria:**
- `docker-compose up` starts all services
- Services can communicate successfully

---

### Task 7: Tests & Documentation

**Description:**  
Validate multi-service behavior and document the system.

**Tests:**
- Create user
- Create order with valid user
- Create order with invalid user
- User Service down scenario

**Documentation:**
- Update `architecture.md`
- Document Phase 2 request flow

**Acceptance Criteria:**
- Tests cover happy paths and failures
- Documentation reflects Phase 2 architecture

---

## 9. Completion Criteria

Phase 2 is complete when:

1. Order Service and User Service run independently
2. Each service owns its database schema
3. Order creation validates user via API
4. No cross-service database access exists
5. Docker Compose runs the full system
6. Tests pass successfully
7. Documentation is updated

---

## 10. Next Phase

Phase 3 will introduce:
- Asynchronous communication
- Message broker
- Domain events (e.g., `OrderCreated`)
- Notification Service
- Event-driven architecture patterns

