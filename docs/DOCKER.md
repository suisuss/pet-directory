# Docker Build Architecture

## Multi-Stage Build Explanation

Our Dockerfile uses a multi-stage build pattern with three stages:

### 1. Base Stage (`base`)
- Sets up the Python 3.11 slim base image
- Configures environment variables for Python optimization
- Installs system dependencies (PostgreSQL client, gcc, curl)
- Upgrades pip and installs build tools

### 2. Production Stage (`production`)
- Extends from `base`
- Copies only necessary files (pyproject.toml, README.md, app/)
- Installs production dependencies from pyproject.toml
- Creates a non-root user for security
- Includes health checks
- Optimized for smaller image size and security

### 3. Development Stage (`development`)
- Extends from `base`
- Copies all project files
- Installs the package in editable mode with dev dependencies
- Includes development tools (mypy, black, ruff, pytest)
- Enables hot-reloading

## How Docker Compose Uses Stages

### Production (`docker-compose.yml`)
```yaml
api:
  build:
    context: .
    target: production  # Uses production stage
```
- Builds a lightweight, secure production image
- No development tools included
- Runs with multiple workers

### Development (`docker-compose.development.yml`)
```yaml
api:
  build:
    context: .
    target: development  # Uses development stage
```
- Includes all development tools
- Mounts local code as volumes for hot-reloading
- Single worker with reload enabled

## Dependency Management

All dependencies are defined in `pyproject.toml`:

- **Production dependencies**: Listed in `[project] dependencies`
- **Development dependencies**: Listed in `[project.optional-dependencies] dev`

The `requirements.txt` and `requirements-dev.txt` files are auto-generated for compatibility:
```bash
python scripts/generate_requirements.py
```

This approach ensures:
1. Single source of truth for dependencies (pyproject.toml)
2. Backward compatibility with tools expecting requirements.txt
3. Clear separation between production and development environments
4. Optimal Docker layer caching