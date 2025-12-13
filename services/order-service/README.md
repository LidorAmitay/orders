# Order Service

A FastAPI-based microservice for managing orders in the Orders system.

## Overview

The Order Service provides REST API endpoints for creating and retrieving orders. It uses PostgreSQL as the database and follows a clean architecture pattern with separate layers for routes, services, and repository.

## Features

- Create new orders via POST `/api/v1/orders`
- Retrieve orders by ID via GET `/api/v1/orders/{id}`
- Health check endpoint at `/health`
- Structured logging
- Database connection pooling

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 14 or higher (or use Docker Compose)
- pip (Python package manager)

### Option 1: Using Virtual Environment (venv)

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file or set the following environment variables:
   ```bash
   ORDER_DB_HOST=localhost
   ORDER_DB_PORT=5432
   ORDER_DB_NAME=orderdb
   ORDER_DB_USER=postgres
   ORDER_DB_PASSWORD=postgres
   ```

5. **Ensure PostgreSQL is running:**
   - Make sure PostgreSQL is installed and running
   - Create the database: `createdb orderdb` (or use your preferred method)
   - Run the initialization script from `infra/db/init/001_create_orders_table.sql`

### Option 2: Using Poetry (Alternative)

1. **Install Poetry** (if not already installed):
   ```bash
   pip install poetry
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Activate the Poetry shell:**
   ```bash
   poetry shell
   ```

4. **Set up environment variables** (same as Option 1)

## Running Locally via Uvicorn

1. **Activate your virtual environment** (if using venv) or Poetry shell

2. **Start the service:**
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The `--reload` flag enables auto-reload on code changes (useful for development).

3. **Verify the service is running:**
   - Open your browser and navigate to: `http://localhost:8000/health`
   - You should see: `{"status": "ok"}`

4. **Access the API documentation:**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## Running via Docker Compose

The easiest way to run the full environment (database + service) is using Docker Compose.

1. **Navigate to the infra directory:**
   ```bash
   cd ../../infra
   ```

2. **Start the services:**
   ```bash
   docker-compose up
   ```

   This will:
   - Start a PostgreSQL container with the database initialized
   - Build and start the Order Service container
   - Set up networking between containers

3. **Verify the service is running:**
   - Health check: `http://localhost:8000/health`
   - API docs: `http://localhost:8000/docs`

4. **Stop the services:**
   ```bash
   docker-compose down
   ```

   To also remove volumes (database data):
   ```bash
   docker-compose down -v
   ```

## Running Tests

The project uses `pytest` for testing. Tests are located in the `tests/` directory.

### Prerequisites for Testing

1. **Ensure you have a test database available:**
   - You can use the same database as development, or
   - Create a separate test database and configure it via environment variables

2. **Set test environment variables** (if using a separate test database):
   ```bash
   export ORDER_DB_NAME=orderdb_test
   # ... other DB settings
   ```

### Running Tests

1. **Activate your virtual environment** (if using venv) or Poetry shell

2. **Run all tests:**
   ```bash
   pytest
   ```

3. **Run tests with verbose output:**
   ```bash
   pytest -v
   ```

4. **Run a specific test file:**
   ```bash
   pytest tests/test_health.py
   pytest tests/test_orders_api.py
   ```

5. **Run a specific test:**
   ```bash
   pytest tests/test_health.py::test_health_endpoint
   ```

6. **Run tests with coverage report:**
   ```bash
   pytest --cov=src --cov-report=html
   ```
   (Note: requires `pytest-cov` package: `pip install pytest-cov`)

### Test Structure

- `tests/test_health.py` - Tests for the `/health` endpoint
- `tests/test_orders_api.py` - Tests for order CRUD operations:
  - Creating orders
  - Retrieving orders by ID
  - Error handling (404, validation errors)

### Important Notes

- **Database Required:** Tests require a running PostgreSQL database. Make sure your database is accessible and the `orders` table exists (created by the init script).
- **Test Data:** Tests create real database records. Consider using a separate test database or cleaning up test data after runs.
- **Environment Variables:** Tests use the same database configuration as the application. Ensure your environment variables are set correctly.

## API Endpoints

### Health Check
- **GET** `/health`
  - Returns: `{"status": "ok"}`

### Orders
- **POST** `/api/v1/orders`
  - Request body:
    ```json
    {
      "user_id": 1,
      "product_id": 100,
      "quantity": 2
    }
    ```
  - Returns: Created order with `order_id`, `status`, and `created_at`

- **GET** `/api/v1/orders/{id}`
  - Returns: Order details
  - Errors: 404 if order not found

## Project Structure

```
order-service/
├── src/
│   ├── config/          # Configuration (settings, database)
│   ├── models/          # Pydantic models
│   ├── repository/      # Database operations
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   └── main.py          # FastAPI application entry point
├── tests/               # Test files
├── Dockerfile           # Container definition
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Development

### Code Style

The project follows Python PEP 8 style guidelines. Consider using:
- `black` for code formatting
- `flake8` or `pylint` for linting
- `mypy` for type checking

### Logging

The service uses Python's standard logging module with structured logging. Logs include service name and relevant context.

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running: `pg_isready` or check Docker container status
- Check environment variables are set correctly
- Verify database exists: `psql -l` or connect via `psql -U postgres -d orderdb`
- Check network connectivity if using Docker Compose

### Port Already in Use

If port 8000 is already in use:
- Change the port: `uvicorn src.main:app --port 8001`
- Or stop the conflicting service

### Import Errors

- Ensure you're in the correct directory
- Verify virtual environment is activated
- Check that all dependencies are installed: `pip list`

## Next Steps

See `docs/phase1.md` for the complete Phase 1 requirements and future phases.

