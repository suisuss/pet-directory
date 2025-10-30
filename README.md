# Pet Directory Service

A RESTful API service for managing a pet directory with a background worker that generates periodic reports.

## Project Overview

This project implements a complete pet directory system with the following components:

- **FastAPI REST API**: Full CRUD operations for managing pets
- **PostgreSQL Database**: Persistent storage with async SQLAlchemy ORM
- **Background Worker**: Generates formatted reports every minute using Jinja2 templates
- **Docker Containerization**: Complete Docker and Docker Compose setup for easy deployment

### Project Structure

```
.
├── app/
│   ├── api/              # REST API endpoints
│   │   └── pets.py       # Pet CRUD operations
│   ├── core/             # Core configurations
│   │   ├── config.py     # Application settings
│   │   └── database.py   # Database connection setup
│   ├── models/           # SQLAlchemy ORM models
│   │   └── pet.py        # Pet model definition
│   ├── schemas/          # Pydantic validation schemas
│   │   └── pet.py        # Pet request/response schemas
│   ├── templates/        # Jinja2 templates
│   │   └── pet_report.j2 # Report template
│   ├── worker/           # Background worker
│   │   └── report_generator.py # Report generation logic
│   └── main.py           # FastAPI application entry point
├── alembic/              # Database migrations
├── docker-compose.yml    # Production orchestration
├── docker-compose.development.yml # Development setup with Adminer
├── Dockerfile            # Container definition
├── requirements.txt      # Python dependencies
├── dev.sh               # Development helper script
└── test_api.sh          # API testing script
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed on your system
- Port 8000 (API) and 5432 (PostgreSQL) available

### Running the Application

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd pet-directory
   ```

2. **Start all services with a single command:**
   ```bash
   docker-compose up
   ```

   Or for development mode with hot-reloading and Adminer:
   ```bash
   docker-compose -f docker-compose.development.yml up
   ```

3. **Services will be available at:**
   - API: http://localhost:8000
   - API Documentation (Swagger): http://localhost:8000/docs
   - API Documentation (ReDoc): http://localhost:8000/redoc
   - Adminer (dev mode only): http://localhost:8080

### Using the Development Helper

A convenient development script is provided with command-line interface:

```bash
./dev.sh [command]
```

Available commands:
- `up` - Start development environment
- `down` - Stop development environment
- `logs` - Show logs from all services
- `rebuild` - Rebuild and restart development environment
- `test` - Run test script to populate sample data
- `clean` - Remove all containers and volumes
- `worker` - Follow worker logs
- `api` - Follow API logs
- `db-shell` - Connect to PostgreSQL shell
- `status` - Show status of all services
- `help` - Show help message

## API Usage

### Example API Interactions

1. **Create a pet:**
   ```bash
   curl -X POST "http://localhost:8000/api/pets/" \
        -H "Content-Type: application/json" \
        -d '{"name": "Buddy", "pet_type": "dog"}'
   ```

2. **List all pets:**
   ```bash
   curl "http://localhost:8000/api/pets/"
   ```

3. **Get a specific pet:**
   ```bash
   curl "http://localhost:8000/api/pets/1"
   ```

4. **Update a pet:**
   ```bash
   curl -X PUT "http://localhost:8000/api/pets/1" \
        -H "Content-Type: application/json" \
        -d '{"name": "Buddy Jr."}'
   ```

5. **Delete a pet:**
   ```bash
   curl -X DELETE "http://localhost:8000/api/pets/1"
   ```

### Testing the API

Run the provided test script to populate sample data and test all endpoints:

```bash
./test_api.sh
```

This script will:
- Create 5 sample pets (2 dogs, 2 cats, 1 bird)
- Test all CRUD operations
- Update one pet's name
- Delete one of the created pets using its actual ID
- Demonstrate pagination
- Test error handling with non-existent pet ID

## Background Worker

The worker runs automatically and:
- Queries the database every 60 seconds
- Groups pets by type with counts
- Generates a formatted report with emoji indicators
- Shows summary, pets by type, and detailed pet list
- Prints the report to stdout (viewable in logs)

View worker output:
```bash
docker-compose logs -f worker
# Or using the dev script:
./dev.sh worker
```

Sample report format:
```
╔════════════════════════════════════════════════════════════════╗
║                    PET DIRECTORY REPORT                        ║
║                 Generated: 2025-10-30 21:32:30 UTC             ║
╚════════════════════════════════════════════════════════════════╝

📊 SUMMARY
-----------
Total Pets: 14

📈 PETS BY TYPE
---------------
  • Bird: 2 pet(s)
  • Cat: 6 pet(s)
  • Dog: 6 pet(s)

📋 DETAILED PET LIST
--------------------
1. Tweety
   Type: Bird
   ID: #8
   Registered: 2025-10-30 21:28
...
```

## Database Access

### Development Mode
When running in development mode, Adminer is available at http://localhost:8080

Connection details:
- System: PostgreSQL
- Server: db
- Username: pets_user
- Password: pets_password
- Database: pets_db

### Direct Database Access
```bash
./dev.sh db-shell
```

## Design Choices and Reflection

### Architecture Decisions

1. **Async Everything**: Chose async SQLAlchemy and FastAPI for better concurrency and performance, especially important for I/O-bound operations like database queries.

2. **Shared Models**: The worker and API share the same SQLAlchemy models and Pydantic schemas, adhering to DRY principles and ensuring consistency.

3. **Single Docker Image**: Both the API and worker use the same Docker image with different entry points, reducing build time and image storage.

4. **Alembic Migrations**: Implemented database versioning from the start for maintainable schema evolution.

5. **Health Checks**: Docker Compose includes health checks to ensure proper service startup order.

### Challenges Faced

- **Async Context Management**: Ensuring proper async session management across both the API and worker required careful attention to context managers.
- **Template Formatting**: Creating a clean report format that's both informative and visually appealing with emoji indicators.
- **Docker Networking**: Configuring services to communicate properly while maintaining development flexibility.

### Potential Improvements

With more time, I would implement:

1. **Enhanced Error Handling**: More granular exception handling with custom error responses and retry logic in the worker.

2. **Configuration Management**: Environment-specific configs using Pydantic Settings for better 12-factor app compliance.

3. **Comprehensive Testing**: Unit tests for models/schemas, integration tests for API endpoints, and end-to-end tests.

4. **Logging Infrastructure**: Structured logging with proper log levels and correlation IDs for request tracing.

5. **Authentication/Authorization**: JWT-based auth system with role-based access control.

6. **API Rate Limiting**: Protect against abuse with rate limiting middleware.

7. **Caching Layer**: Redis integration for frequently accessed data.

8. **Monitoring/Metrics**: Prometheus metrics and health check endpoints for production observability.

9. **Data Validation**: More sophisticated validation rules (e.g., pet name uniqueness per type).

10. **Worker Improvements**: Configurable report intervals, multiple report formats, and email delivery option.

## License

MIT

