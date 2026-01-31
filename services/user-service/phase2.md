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
  - Its own database
  - Its own API
  - Its own Docker container
- Order Service validates users via User Service API
- Updated Docker Compose environment
- Updated architecture documentation

---

## 3. Architecture Overview

Client  
→ Order Service  
→ (REST) User Service  
→ PostgreSQL  

Rules:
- No cross-service database access
- Communication via HTTP only
- Each service owns its schema

---

## 4. Tasks Breakdown (Architecture-Driven Order)

### Task 1: Create User Service Skeleton ✅

**Description:**  
Create the initial User Service structure.

**Implementation details:**
- Create `services/user-service`
- Add folders: `routes/`, `services/`, `repository/`, `models/`, `config/`
- Add FastAPI `main.py`
- Add `/health` endpoint
- Add Pydantic v2 settings

**Acceptance Criteria:**
- User Service runs independently
- `/health` returns `{ "status": "ok" }`

---

### Task 2: Define User Domain Models

**Description:**  
Define User domain models independent of database and API layers.

**Implementation details:**
- Create `models/user.py`
- Define:
  - `UserBase`
  - `UserCreate`
  - `UserInDB`
- Use Pydantic v2 features (`from_attributes=True`)
- No SQL or HTTP logic

**Acceptance Criteria:**
- Clear separation between domain and persistence
- Models reusable across layers

---

### Task 3: Implement User Repository Layer

**Description:**  
Implement persistence logic for User Service.

**Implementation details:**
- Create `repository/user_repository.py`
- Implement:
  - `create_user`
  - `get_user_by_id`
  - `get_user_by_email`
- Use DB connection pool
- SQL isolated to repository layer

**Acceptance Criteria:**
- No SQL outside repository
- Repository returns domain models

---

### Task 4: Implement User Service (Business Logic)

**Description:**  
Encapsulate business rules and orchestration logic.

**Implementation details:**
- Create `services/user_service.py`
- Validate uniqueness (email)
- Raise domain-specific exceptions

**Acceptance Criteria:**
- Business logic isolated from API and DB
- Service layer reusable by non-HTTP flows

---

### Task 5: Implement User API Routes

**Description:**  
Expose REST API for user management.

**Endpoints:**
- `POST /api/v1/users`
- `GET /api/v1/users/{id}`

**Implementation details:**
- Create `routes/users.py`
- Use FastAPI dependency injection
- Return DTOs only

**Acceptance Criteria:**
- Proper HTTP status codes
- Thin controllers (no business logic)

---

### Task 6: Service-to-Service Communication

**Description:**  
Integrate Order Service with User Service.

**Implementation details:**
- Add HTTP client with timeout
- Configurable User Service base URL
- Validate user existence during order creation

**Acceptance Criteria:**
- Order creation fails for invalid user
- No direct DB access

---

### Task 7: Error Handling & Resilience

**Description:**  
Handle domain and downstream errors gracefully.

**Implementation details:**
- Domain-specific exceptions
- API exception handlers
- Downstream error mapping

**Acceptance Criteria:**
- Clear error responses
- Services remain stable on failures

---

### Task 8: Update Docker Compose

**Description:**  
Run services together locally.

**Implementation details:**
- Add User Service container
- Ensure networking between services
- Environment-based configuration

**Acceptance Criteria:**
- `docker-compose up` runs all services
- Inter-service communication works

---

### Task 9: Tests & Documentation

**Description:**  
Validate system behavior and document architecture.

**Tests:**
- User CRUD
- Order creation with valid/invalid user
- User Service unavailable scenario

**Documentation:**
- Update `architecture.md`
- Document Phase 2 request flow

**Acceptance Criteria:**
- Tests cover happy and failure paths
- Documentation reflects actual system

---

## 5. Completion Criteria

Phase 2 is complete when:
- Services run independently
- Each service owns its database
- Order creation validates users via API
- Docker Compose runs successfully
- Tests pass

---

## 6. Next Phase

Phase 3 will introduce:
- Asynchronous communication
- Message broker
- Domain events
- Notification Service
