1. Docker Compose Development Setup (docker-compose.development.yml)

  This file orchestrates 4 services in development mode:

  Database Service (db)

  - Uses PostgreSQL 15 Alpine (lightweight)
  - Configured with health checks to ensure it's ready before dependent
  services start
  - Exposes port 5432 for direct database access
  - Stores data in a named volume postgres_data_dev for persistence

  API Service

  - Builds from our Dockerfile
  - Waits for database to be healthy before starting
  - Runs migrations automatically on startup using Alembic
  - Mounts source code as volumes for hot-reloading during development
  - Exposes port 8000 for API access
  - Environment variable PYTHONUNBUFFERED=1 ensures real-time log output

  Worker Service

  - Uses the same Docker image as API (efficient reuse)
  - Waits for both database and API to be ready
  - Runs the background report generator script
  - Prints formatted reports to stdout every minute
  - Shares the same database connection configuration

  Adminer Service (Development only)

  - Web-based database management UI
  - Accessible on port 8080
  - Pre-configured to connect to our PostgreSQL database

  2. Application Architecture

  Project Structure

  app/
  ├── api/           # REST endpoints
  ├── core/          # Core configurations
  ├── models/        # SQLAlchemy ORM models
  ├── schemas/       # Pydantic validation schemas
  ├── templates/     # Jinja2 templates
  ├── worker/        # Background worker
  └── main.py        # FastAPI application entry

  Core Components

  Database Layer (app/core/database.py)
  - Async SQLAlchemy engine configuration
  - Session management with dependency injection
  - Connection pooling for performance

  Models (app/models/pet.py)
  - SQLAlchemy 2.0 declarative model
  - Uses mapped columns for type hints
  - Automatic timestamp on creation

  Schemas (app/schemas/pet.py)
  - Pydantic models for request/response validation
  - Separate schemas for Create, Update, and Response
  - Automatic serialization/deserialization

  3. API Implementation (app/api/pets.py)

  Full CRUD operations with async handlers:
  - POST /api/pets/ - Create new pet
  - GET /api/pets/ - List all pets with pagination
  - GET /api/pets/{id} - Get specific pet
  - PUT /api/pets/{id} - Update pet
  - DELETE /api/pets/{id} - Remove pet

  Each endpoint:
  - Uses dependency injection for database sessions
  - Implements proper error handling (404 for not found)
  - Returns appropriate HTTP status codes
  - Validates input/output with Pydantic

  4. Background Worker (app/worker/report_generator.py)

  Key Design Decisions:
  - Reuses the same SQLAlchemy models and Pydantic schemas (DRY
  principle)
  - Runs in an infinite async loop
  - Generates reports every 60 seconds
  - Handles errors gracefully without crashing

  Report Generation Process:
  1. Queries all pets from database
  2. Groups pets by type
  3. Passes data to Jinja2 template
  4. Outputs formatted ASCII report to stdout

  5. Template System (app/templates/pet_report.j2)

  Uses Jinja2 for flexible report formatting:
  - ASCII art borders for visual appeal
  - Dynamic pet counting and grouping
  - Formatted timestamps
  - Handles empty database gracefully

  6. Database Migrations (Alembic)

  - Initial migration creates the pets table
  - Configured for async operations
  - Auto-runs on container startup
  - Version controlled schema changes

  7. Containerization (Dockerfile)

  Single multi-purpose image:
  - Based on Python 3.11 slim (minimal size)
  - Installs PostgreSQL client for migrations
  - Copies requirements first (Docker layer caching)
  - Default command runs API, but overrideable for worker

  8. Development Helpers

  dev.sh Script
  - Convenient commands for development
  - Colored output for better UX
  - Status checking and log viewing
  - Clean rebuild capabilities

  test_api.sh Script
  - Populates sample data
  - Tests all CRUD operations
  - Pretty-printed JSON output
  - Provides quick verification

  9. Key Architectural Decisions

  1. Async Everything: All database operations are async for better
  concurrency
  2. Shared Models: Worker and API use identical models/schemas
  3. Health Checks: Ensures proper startup sequence
  4. Hot Reload: Development volumes enable instant code updates
  5. Single Image: Both API and worker use same image, different
  commands
  6. Auto-migrations: Database schema updates automatically on startup

  10. How It All Works Together

  1. Startup Sequence:
    - Database starts and passes health check
    - API container runs migrations, then starts server
    - Worker waits for API, then begins report generation
  2. Request Flow:
    - Client sends request to API
    - FastAPI validates with Pydantic
    - Async SQLAlchemy performs database operation
    - Response serialized and returned
  3. Worker Flow:
    - Every minute, queries database
    - Formats data with Jinja2 template
    - Prints report to stdout (visible in logs)

  The solution achieves clean separation of concerns, code reusability,
  and easy development workflow while meeting all requirements from the
  technical challenge.


