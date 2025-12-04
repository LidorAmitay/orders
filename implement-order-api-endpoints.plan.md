<!-- f9e93c0d-0fca-4e50-8518-469330f2da24 3b49e7dc-347b-43fa-a66e-6fdd0e434902 -->
# Task 6: Implement Order API Endpoints

## Overview

Add HTTP endpoints `POST /api/v1/orders` and `GET /api/v1/orders/{id}` by creating a routes module, service layer, and integrating them into the main FastAPI app.

## Implementation Steps

### Step 1: Create routes directory structure

- Create `services/order-service/src/routes/` directory
- Create `services/order-service/src/routes/__init__.py` (empty file for Python package)

### Step 2: Create order service layer

- Create `services/order-service/src/services/` directory  
- Create `services/order-service/src/services/__init__.py` (empty file)
- Create `services/order-service/src/services/order_service.py`:
- Import `OrderCreate`, `OrderResponse` from models
- Import `create_order`, `get_order_by_id` from repository
- Implement `create_order_service(order: OrderCreate) -> OrderResponse`:
  - Call repository `create_order()` and return result
  - Handle exceptions (let them propagate for now, or add basic error handling)
- Implement `get_order_service(order_id: int) -> Optional[OrderResponse]`:
  - Call repository `get_order_by_id()` and return result
  - Return None if order not found (repository already handles this)

### Step 3: Create orders router

- Create `services/order-service/src/routes/orders.py`:
- Import `APIRouter` from fastapi
- Import `HTTPException` from fastapi for 404 handling
- Import service functions from `services.order_service`
- Import `OrderCreate`, `OrderResponse` from models
- Create router: `router = APIRouter(prefix="/api/v1/orders", tags=["orders"])`
- Implement `POST /api/v1/orders` endpoint:
  - Accept `OrderCreate` as request body
  - Call `create_order_service()`
  - Return `OrderResponse` with status 201
  - Handle exceptions appropriately
- Implement `GET /api/v1/orders/{order_id}` endpoint:
  - Accept `order_id: int` as path parameter
  - Call `get_order_service(order_id)`
  - If None, raise `HTTPException(status_code=404, detail="Order not found")`
  - Return `OrderResponse` with status 200

### Step 4: Register router in main.py

- Update `services/order-service/src/main.py`:
- Import router from `src.routes.orders`
- Register router: `app.include_router(orders.router)`
- Ensure router is registered after app creation

### Step 5: Verify implementation

- Test endpoints manually:
- Start service: `uvicorn src.main:app --reload`
- POST to `/api/v1/orders` with valid JSON body
- GET from `/api/v1/orders/{order_id}` with existing ID
- GET from `/api/v1/orders/{order_id}` with non-existent ID (should return 404)

## Files to Create/Modify

**New files:**

- `services/order-service/src/routes/__init__.py`
- `services/order-service/src/routes/orders.py`
- `services/order-service/src/services/__init__.py`
- `services/order-service/src/services/order_service.py`

**Modified files:**

- `services/order-service/src/main.py` (add router registration)

## Dependencies

- FastAPI (already in requirements.txt)
- Existing models, repository, and config modules