# Backend Developer Technical Challenge

This technical challenge is designed to give you an opportunity to showcase your expertise in the core technologies and architectural patterns we use every day. We're excited to see your skills in action.

We ask that you spend approximately **4 hours** on this exercise. Our goal is to assess your approach to a realistic task, so we value clean, well-structured, and maintainable code over a rushed or feature-packed solution. We will use your submission as the basis for our next technical discussion.

You are welcome and encouraged to use any resources you would normally use at work, including official documentation, Stack Overflow, and AI assistants.

## Objective

Your task is to build a simple "Pet Directory" service. The service will consist of two main components: a RESTful API for managing pets and a separate background worker for reporting on them. The entire application should be containerized and easy to run.

We expect the solution to leverage:

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Data Validation:** [Pydantic](https://docs.pydantic.dev/)
- **Database/ORM:** [PostgreSQL](https://www.postgresql.org/) with [SQLAlchemy 2.0+](https://www.sqlalchemy.org/) (Async)
- **Templating:** [Jinja2](https://jinja.palletsprojects.com/)
- **Containerization:** [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)

## Core Requirements

1.  **FastAPI Application:**

    - Create a FastAPI application to serve as the API.
    - Implement full CRUD (Create, Read, Update, Delete) endpoints for a `pets` resource.
    - Use Pydantic for all request/response data validation and serialization.
    - Enable Swagger API UI.
    - JWT-Authentication at this point is not mandatory but is nice to have.

2.  **Database & Models (Async):**

    - Use **SQLAlchemy 2.0+** with an **async** engine and session management (`AsyncSession`).
    - The database should be **PostgreSQL**.
    - Define a `Pet` SQLAlchemy model with at least the following fields: `id` (PK), `name` (string), `pet_type` (string, e.g., "cat", "dog", "bird"), and `created_at` (datetime).
    - **All** database operations within the API must be asynchronous.
    - Use `Alembic` as DB migrations engine.

3.  **Background Worker:**

    - Create a separate, runnable Python script that acts as a background worker.
    - The worker must run in an endless, asynchronous loop.
    - **Once every minute**, the worker should perform the following actions:
      - Connect to the same PostgreSQL database used by the API.
      - Query for **all** pets currently in the directory.
      - **Important:** The worker must reuse the same SQLAlchemy models and Pydantic schemas defined for the API to ensure code is DRY (Don't Repeat Yourself).
      - Format the list of pets into a human-readable report.
      - Print this report to **STDOUT** (standard output).

4.  **Templating:**

    - Use the **Jinja2** templating engine to format the report that the worker prints to STDOUT.

5.  **Containerization & Orchestration:**
    - Write a `Dockerfile` to containerize your Python application.
    - Create a `docker-compose.yml` file that defines and orchestrates the entire service stack. It must define and run three services:
      1.  `db`: The PostgreSQL database service.
      2.  `api`: The FastAPI application service.
      3.  `worker`: The background worker process. This should use the _same Docker image_ as the `api` service but be started with a different command.

## Deliverables

1.  **Git Repository:** Please provide your solution as a public Git repository. It should contain all the necessary code:

    - Application source code (for both API and worker).
    - `Dockerfile`.
    - `docker-compose.yml` file.
    - Any Pydantic schemas, SQLAlchemy models, and Jinja2 templates.
    - A `requirements.txt` or similar dependency file (`poetry`, `uv`).

2.  **README.md:** A clear `README.md` file within the repository that includes:

    - A brief overview of your project structure.
    - Simple, clear instructions on how to build and run the entire application using a single `docker-compose up` command.
    - Instructions on how to interact with the API (e.g., example `curl` commands).

3.  **Reflection:** A short paragraph in the `README.md` reflecting on your solution. Discuss your design choices, any challenges you faced, and potential improvements you would make if you had more time (e.g., error handling, configuration management, testing, logging).

Good luck! We are very excited to see what you build.
