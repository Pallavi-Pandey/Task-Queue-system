# Task Queue System

A scalable task queue system built with FastAPI and Celery, designed to handle background job processing with Redis as the message broker.

## Features

- RESTful API for job management
- Asynchronous task processing with Celery
- SQLite database for development (can be easily switched to PostgreSQL for production)
- Comprehensive test suite with 88% code coverage
- Swagger UI and ReDoc documentation

## Prerequisites

- Python 3.10+
- Redis server
- pip (Python package manager)

## Project Structure

```
task_queue_system/
├── app/
│   ├── __init__.py
│   ├── celery_worker.py    # Celery worker configuration
│   ├── config.py           # Application configuration
│   ├── crud.py             # Database operations
│   ├── database.py         # Database connection and models
│   ├── main.py             # FastAPI application
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic models
│   └── tasks.py            # Celery tasks
├── tests/                  # Test files
│   ├── conftest.py
│   ├── test_crud.py
│   ├── test_main.py
│   └── test_tasks.py
├── .gitignore
├── README.md
├── pytest.ini
└── requirements.txt
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Pallavi-Pandey/Task-Queue-system.git
   cd Task-Queue-system
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start Redis server:
   ```bash
   sudo service redis-server start
   ```

## Running the Application

### Start FastAPI Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

### Start Celery Worker

In a new terminal (with the virtual environment activated):

```bash
export PYTHONPATH=$PYTHONPATH:.
celery -A app.celery_worker.celery worker --loglevel=info
```

## API Documentation

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Available Endpoints

- `GET /` - Welcome message
- `POST /api/v1/jobs/` - Create a new job
- `GET /api/v1/jobs/{job_id}` - Get job status

## Running Tests

To run the test suite:

```bash
TESTING=1 python -m pytest -v
```

To run tests with coverage report:

```bash
TESTING=1 python -m pytest --cov=app --cov-report=term-missing
```

## Running with Docker

This project includes Docker Compose configuration for easy setup with all dependencies.

### Prerequisites

- Docker
- Docker Compose

### Quick Start

1. Build and start all services:
   ```bash
   docker-compose up --build
   ```

   This will start:
   - FastAPI application on port 8000
   - PostgreSQL database
   - Redis server
   - Celery worker

2. Access the application:
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Individual Services

You can also start individual services:

```bash
# Start only the database and Redis
docker-compose up -d db redis

# Start the web application
docker-compose up -d web

# Start the Celery worker
docker-compose up -d worker

# View logs
docker-compose logs -f
```

### Running Tests with Docker

To run tests in a container:

```bash
docker-compose run --rm web bash -c "TESTING=1 python -m pytest -v"
```

### Stopping Containers

To stop all containers:

```bash
docker-compose down
```

Or to remove volumes as well:

```bash
docker-compose down -v
```

## Environment Variables

- `DATABASE_URL`: Database connection URL (default: SQLite for development)
- `REDIS_URL`: Redis connection URL (default: `redis://localhost:6379/0`)
- `TESTING`: Set to '1' when running tests

## Deployment

For production deployment, consider:

1. Using PostgreSQL instead of SQLite
2. Setting up Redis with persistence
3. Using a process manager like Supervisor or systemd
4. Configuring proper logging
5. Setting up monitoring

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
