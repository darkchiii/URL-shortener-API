# URL Shortener API

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.2.1-green.svg)
![DRF](https://img.shields.io/badge/Django%20REST%20Framework-3.16.0-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)
![CI](https://github.com/darkchiii/URL-shortener-API/actions/workflows/ci.yml/badge.svg)
![Tested](https://img.shields.io/badge/Tested-pytest-green.svg)
![Formatted](https://img.shields.io/badge/Formatted-black%20%7C%20isort%20%7C%20flake8-black.svg)

API for shortening long URLs with visit statistics tracking functionality.

## Table of Contents

- [Project Description](#project-description)
- [Features](#features)
- [Technologies](#technologies)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Cron Job](#cron-job)
- [Data Models](#data-models)
- [Usage Examples](#usage-examples)
- [Tests](#tests)
- [Project Structure](#project-structure)
- [License](#license)

## Project Description

URL Shortener is a REST API for converting long URLs into short, easy-to-remember and shareable links. The system additionally collects statistics about visits to each shortened link, such as IP address, user agent, and the date and time of the visit.

## Features

- Creating shortened links for long URLs
- Automatic redirection from short links to the original URLs
- Tracking the number of visits for each shortened link
- Recording visitor information (IP address, user agent)
- Automatic validation of URL correctness
- Handling uniqueness of shortened codes
- Automatic expiration of unused links (default: 7 days)
- Importing URLs from CSV files to the database

## Technologies

- Python 3.10+
- Django 5.2.1
- Django REST Framework 3.16.0
- PostgreSQL 15
- Docker and Docker Compose
- Testing tools: pytest 8.2.0, pytest-django 4.8.0
- Code formatting tools: black 24.3.0, isort 5.13.2, flake8 7.0.0
- python-dotenv 1.1.0 for environment variables management
- Cron (system scheduler) inside Docker container for periodic tasks

## Installation

### Requirements

- Docker and Docker Compose
- Git
- .dev file with appropriate environment variables

### Cloning the Repository

```bash
git clone https://github.com/darkchiii/URL-shortener-API.git url-shortener
cd url-shortener
```

### Environment Variables Configuration

Create an `.dev` file in the project's root directory with the following variables:

```
# PostgreSQL Settings
POSTGRES_DB=shortener_db
POSTGRES_USER=shortener_user
POSTGRES_PASSWORD=supersecretpassword
DB_HOST=db
DB_PORT=5432
```
Important: Ensure this .dev file is properly loaded by Docker Compose and all containers (web, db, and cron) have access to these variables.

### Using Docker

```bash
docker-compose up -d --build
```

After starting the containers, the application will be available at `http://localhost:8000/api/`

### Local Installation

1. Create and activate a Python virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Configure PostgreSQL database

```bash
# Make sure PostgreSQL is installed and running
# Create a database:
createdb url_shortener
```

4. Run database migrations

```bash
python manage.py migrate
```

## Running the Application

### Using Docker

```bash
docker-compose up
```

### Locally (development mode)

```bash
python manage.py runserver
```

The API will be available at: `http://localhost:8000/api/`

## API Endpoints

### Creating a Short Link

- **URL:** `/api/shortener/`
- **Method:** `POST`
- **Data:** `{"original_url": "https://example.com/very/long/url/to/shorten"}`
- **Response:**
  ```json
  {
    "short_url": "abc12345",
    "status": "short URL created"
  }
  ```

### Redirecting to the Original URL

- **URL:** `/api/shortener/{short_code}/`
- **Method:** `GET`
- **Response:** Redirection to the original URL

### Statistics for a Short Link

- **URL:** `/api/stats/{short_code}/`
- **Method:** `GET`
- **Response:**
  ```json
  {
    "Short url": "abc12345",
    "Visits": 42,
    "Active": true,
    "Days left": 5,
    "Last visitor": "2023-05-12T15:23:45Z"
  }
  ```

## Cron Job

To automate periodic deactivation of expired short URLs, the project uses a cron job running inside a dedicated Docker container (`url_shortener-cron-1`).

### Operation

* The cron job runs every minute and executes the Django management command:

```bash
python manage.py deactivate_urls
```

* This command updates all expired URLs by setting their `is_active` flag to `False`.
* Cron job logs are stored in `/var/log/cron.log` inside the cron container.

### Setup Configuration

### Crontab Configuration

The crontab file (`/etc/cron.d/crontab`) should contain:

```
* * * * * root cd /app && /usr/local/bin/python manage.py deactivate_urls >> /var/log/cron.log 2>&1
```

### Important Setup Notes

* Set proper permissions for the crontab file:

```bash
chmod 0644 /etc/cron.d/crontab
```

* Environment variables (`POSTGRES_USER`, `POSTGRES_DB`, etc.) must be correctly passed to the cron container via Docker Compose `env_file` to allow database connection.

### Container Entrypoint

In the `entrypoint.sh` of the cron container:
* The cron daemon is started with:

```bash
cron && tail -f /var/log/cron.log
```

* Avoid calling `crontab /etc/cron.d/crontab` explicitly, as cron reads files in `/etc/cron.d/` automatically.

## Manual Testing

You can manually test the command inside the cron container with:

```bash
docker exec -it url_shortener-cron-1 python3 manage.py deactivate_urls
```

## Data Models

### ShortUrl

| Field        | Type                 | Description                              |
|--------------|----------------------|------------------------------------------|
| original_url | URLField (2000)      | Original URL                             |
| short_url    | CharField (8)        | Unique short URL code                    |
| created_at   | DateTimeField        | Creation date of the short link          |
| visits       | PositiveIntegerField | Visit counter                            |
| expires_at   | DateTimeField        | Link expiration date                     |
| is_active    | BooleanField         | Link active status                       |

### Visit

| Field       | Type               | Description                        |
|-------------|--------------------|------------------------------------|
| short_url   | ForeignKey         | Reference to ShortUrl model        |
| ip_address  | GenericIPAddressField | Visitor's IP address           |
| user_agent  | TextField          | Browser/device information         |
| visited_at  | DateTimeField      | Visit date and time                |

## Usage Examples

### Creating a Short URL

```python
import requests

response = requests.post('http://localhost:8000/api/shortener/',
                         json={'original_url': 'https://www.example.com/very/long/url'})
data = response.json()
print(f"Short URL: http://localhost:8000/api/shortener/{data['short_url']}/")
```

### Checking Statistics

```python
import requests

response = requests.get('http://localhost:8000/api/stats/abc12345/')
data = response.json()
print(f"Number of visits: {data['Visits']}")
print(f"Active: {data['Active']}")
print(f"Days until expiration: {data['Days left']}")
```

## Tests

The project contains unit and integration tests written using pytest. To run the tests:

```bash
# Using pytest
pytest

# Using pytest with code coverage
pytest --cov=shortener

# Running tests in Django
python manage.py test shortener
```

## Project Structure

```
url-shortener/
├── cron
│   ├── crontab              # Crontab configuration
│   ├── dockerfile           # Docker image for cron job build configuration
│   └── entrypoint.sh        # Container entrypoint
├── .dev                     # Environment variables for development use (not versioned)
├── .local                   # Environment variables for local use (not versioned)
├── .gitignore               # Files ignored by git
├── db.sqlite3               # Local SQLite database (for development)
├── docker-compose.yml       # Docker Compose configuration
├── dockerfile               # Docker image build configuration
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── shortener/               # Main application
│   ├── __init__.py
│   ├── admin.py             # Admin panel configuration
│   ├── apps.py              # Application configuration
│   ├── data/                # Test data and import scripts
│   │   ├── add_data.py      # Script for adding test data
│   │   └── urls_data.csv    # Sample URL data
│   ├── migrations/          # Database migrations
│   ├── models.py            # Data models
│   ├── serializers.py       # REST API serializers
│   ├── tests/               # Tests
│   │   ├── __init__.py
│   │   ├── test_serializers.py
│   │   ├── test_stats_view.py
│   │   ├── tests_models.py
│   │   └── tests_views.py
│   ├── urls.py              # URL configuration
│   ├── utils.py             # Helper functions
│   └── views.py             # API views
└── url_shortener/           # Project configuration
    ├── __init__.py
    ├── asgi.py              # ASGI configuration
    ├── settings.py          # Django settings
    ├── urls.py              # Main URLs
    └── wsgi.py              # WSGI configuration
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.