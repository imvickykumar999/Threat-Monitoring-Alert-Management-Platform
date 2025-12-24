# Threat Monitoring & Alert Management Platform

A Django REST API backend for threat monitoring and alert management system with JWT authentication, role-based access control, and automatic alert generation.

## Features

- **JWT Authentication** with role-based access control (Admin/Analyst)
- **Event Ingestion** with automatic alert generation for High/Critical severity events
- **Alert Management** with status tracking and filtering
- **RESTful API** with pagination, filtering, and ordering
- **Swagger/OpenAPI** documentation
- **Docker** containerization support
- **PostgreSQL/SQLite** database compatibility
- **Comprehensive Unit Tests**

## Quick Start

### Local Development (SQLite)

1. **Clone and setup:**
```bash
git clone <repository-url>
cd threat-monitoring-platform
pip install -r requirements.txt
```

2. **Environment setup:**
```bash
cp .env.example .env
# Edit .env file with your settings
```

3. **Database setup:**
```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Create superuser:**
```bash
python manage.py createsuperuser
```

5. **Run server:**
```bash
python manage.py runserver
```

### Docker Development

1. **Using Docker Compose:**
```bash
docker-compose up --build
```

2. **Access the application:**
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/
- Swagger Docs: http://localhost:8000/swagger/

## API Endpoints

### Authentication
- `POST /api/auth/token/` - Obtain JWT token
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Users
- `GET /api/users/` - List users (Admin only)
- `POST /api/users/` - Create user (Admin only)
- `GET /api/users/{id}/` - Get user details (Admin only)
- `GET /api/users/me/` - Get current user profile

### Events
- `GET /api/events/` - List events with filtering
- `POST /api/events/` - Create event (Admin only)
- `GET /api/events/{id}/` - Get event details

**Query Parameters for Events:**
- `severity`: Filter by severity (Low/Medium/High/Critical)
- `event_type`: Filter by event type
- `source_name`: Filter by source name
- `ordering`: Order by timestamp, severity, etc.

### Alerts
- `GET /api/alerts/` - List alerts with filtering
- `GET /api/alerts/{id}/` - Get alert details
- `PATCH /api/alerts/{id}/` - Update alert status (Admin only)

**Query Parameters for Alerts:**
- `status`: Filter by status (Open/Acknowledged/Resolved)
- `severity`: Filter by event severity
- `ordering`: Order by created_at, status, etc.

## Business Logic

### Automatic Alert Creation
- When an Event is created with severity "High" or "Critical", an Alert is automatically created
- Alerts are linked to their triggering events
- Alert status defaults to "Open"

### Role-Based Permissions
- **Admin**: Full access to all endpoints and can update alert status
- **Analyst**: Read-only access to events and alerts

## API Usage Examples

### 1. Authentication
```bash
# Get JWT token
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Use token in requests
curl -H "Authorization: Bearer <your-token>" \
  http://localhost:8000/api/events/
```

### 2. Create Event (Admin only)
```bash
curl -X POST http://localhost:8000/api/events/ \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "source_name": "Firewall",
    "event_type": "intrusion_attempt",
    "severity": "High",
    "description": "Suspicious login attempt detected"
  }'
```

### 3. List Alerts with Filtering
```bash
# Get open alerts
curl -H "Authorization: Bearer <your-token>" \
  "http://localhost:8000/api/alerts/?status=Open"

# Get high severity alerts
curl -H "Authorization: Bearer <your-token>" \
  "http://localhost:8000/api/alerts/?severity=High"
```

### 4. Update Alert Status (Admin only)
```bash
curl -X PATCH http://localhost:8000/api/alerts/1/ \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "Resolved"}'
```

## Database Schema

### User Model
- Extends Django's AbstractUser
- Additional field: `role` (admin/analyst)

### Event Model
- `source_name`: Source system name
- `event_type`: Type of security event
- `severity`: Low/Medium/High/Critical
- `description`: Event details
- `timestamp`: Auto-generated timestamp

### Alert Model
- `event`: Foreign key to Event
- `status`: Open/Acknowledged/Resolved
- `created_at`: Auto-generated timestamp
- `resolved_at`: Set when status becomes "Resolved"

## Testing

Run the test suite:
```bash
python manage.py test monitoring
```

Test coverage includes:
- User role functionality
- Automatic alert creation for High/Critical events
- API permissions and access control
- Alert status updates
- Filtering and pagination

## Assumptions

1. **Immutable Events:** Security events are treated as immutable logs. If an event has the wrong severity, a new corrected event should be ingested rather than patching the old one.
2. **Alert Deletion:** Analysts are restricted from deleting alerts to maintain audit trails; they can only view them.
3. **Single Admin Level:** The system currently assumes a single tier of Admin privilege (Superuser) rather than granular permission groups.
4. **Timezones:** All timestamps are stored in UTC (or Asia/Kolkata as configured) to ensure consistency across distributed systems.

## Environment Variables

Create a `.env` file with:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
JWT_ACCESS_TOKEN_LIFETIME_HOURS=1
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
```

## Production Deployment

1. **Set DEBUG=False**
2. **Use PostgreSQL database**
3. **Configure ALLOWED_HOSTS**
4. **Use strong SECRET_KEY**
5. **Enable HTTPS**
6. **Configure static files serving**

### Docker Production Setup
```bash
# Build and run
docker-compose -f docker-compose.prod.yml up --build
```

## Security Features

- JWT token authentication
- Role-based access control
- Input validation and sanitization
- SQL injection prevention
- Permission checks on all endpoints
- Secure password hashing

## API Documentation

Full API documentation is available at `/swagger/` when the server is running.

## Project Structure

```
threat_monitoring_platform/
├── monitoring/
│   ├── models.py          # Database models
│   ├── serializers.py     # DRF serializers
│   ├── views.py          # API viewsets
│   ├── urls.py           # App URL routing
│   ├── permissions.py    # Custom permissions
│   ├── admin.py          # Django admin config
│   └── tests.py          # Unit tests
├── threat_monitoring_platform/
│   ├── settings.py       # Django settings
│   ├── urls.py           # Main URL routing
│   └── wsgi.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Technologies Used

- **Backend**: Django 4.2+, Django REST Framework
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Documentation**: Swagger/OpenAPI (drf-yasg)
- **Containerization**: Docker & Docker Compose
- **Filtering**: django-filter

## License

This project is licensed under the MIT License.