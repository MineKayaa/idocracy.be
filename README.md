# IDocracy - Centralized Identity and Access Management API

IDocracy is a comprehensive FastAPI-based identity and access management system that provides centralized authentication, user management, application management, and Single Sign-On (SSO) capabilities.

## Features

### Core Features
- **Centralized Authentication**: JWT-based authentication with access and refresh tokens
- **User Management**: Complete CRUD operations for users with role-based access control
- **Application Management**: Register and manage applications with client credentials
- **App-User Relationships**: Manage user access to specific applications
- **Single Sign-On (SSO)**: Centralized portal for launching applications with seamless authentication
- **Role-Based Access Control (RBAC)**: Fine-grained permissions for users and applications

### SSO Features
- **User Dashboard**: View all applications a user has access to
- **App Launch**: Seamless redirection to applications with authentication tokens
- **Token Verification**: Client applications can verify SSO tokens
- **App Metadata**: Support for app descriptions, logos, and website URLs

### Security Features
- **Password Hashing**: Secure password storage using bcrypt
- **JWT Tokens**: Secure token-based authentication
- **Client Credentials**: Auto-generated client IDs and secrets for applications
- **Token Expiration**: Configurable token expiration times
- **CORS Support**: Cross-origin resource sharing configuration

## Architecture

### Technology Stack
- **Backend**: FastAPI (Python 3.11)
- **Database**: MongoDB (NoSQL)
- **Authentication**: JWT with refresh tokens
- **Password Hashing**: bcrypt
- **Containerization**: Docker & Docker Compose
- **Validation**: Pydantic v2

### Database Schema

#### Users Collection
```json
{
  "_id": "string (UUID)",
  "email": "user@example.com",
  "password_hash": "hashed_password",
  "name": "User Name",
  "roles": ["user", "admin"],
  "created_at": "datetime"
}
```

#### Apps Collection
```json
{
  "_id": "string (UUID)",
  "name": "Application Name",
  "client_id": "auto_generated",
  "client_secret": "hashed_secret",
  "redirect_uris": ["https://app.example.com/callback"],
  "description": "App description",
  "logo_url": "https://example.com/logo.png",
  "website_url": "https://app.example.com",
  "created_by": "user_id",
  "created_at": "datetime"
}
```

#### App Users Collection
```json
{
  "_id": "string (UUID)",
  "user_id": "user_id",
  "app_id": "app_id",
  "roles": ["viewer", "admin"],
  "created_at": "datetime"
}
```

#### Tokens Collection
```json
{
  "_id": "string (UUID)",
  "user_id": "user_id",
  "token": "refresh_token",
  "expires_at": "datetime"
}
```

## API Endpoints

### Authentication APIs
- `POST /api/v1/auth/login` - Login and return JWT tokens
- `POST /api/v1/auth/register` - Register a new user
- `GET /api/v1/auth/me` - Get logged-in user info
- `POST /api/v1/auth/logout` - Revoke tokens

### User Management APIs
- `GET /api/v1/users/` - List all users (admin only)
- `POST /api/v1/users/` - Add new user (admin only)
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Remove user

### Application Management APIs
- `GET /api/v1/apps/` - List all apps
- `POST /api/v1/apps/` - Register new app
- `GET /api/v1/apps/{app_id}` - Get app info
- `PUT /api/v1/apps/{app_id}` - Update app
- `DELETE /api/v1/apps/{app_id}` - Delete app

### App-User Relationship APIs
- `POST /api/v1/apps/{app_id}/users` - Add user to app
- `GET /api/v1/apps/{app_id}/users` - List app users
- `DELETE /api/v1/apps/{app_id}/users/{user_id}` - Remove user from app

### Token Management APIs
- `POST /api/v1/token/verify` - Check if token is valid & get roles
- `POST /api/v1/token/refresh` - Refresh expired access token

### SSO APIs
- `GET /api/v1/sso/dashboard` - Get user's accessible apps
- `GET /api/v1/sso/launch/{app_id}` - Launch app with SSO authentication
- `POST /api/v1/sso/verify` - Verify SSO token (for client apps)

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd IDocracy
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the services**
   ```bash
   docker compose up -d
   ```

4. **Create admin user**
   ```bash
   docker exec -it idocracy_api python scripts/create_admin.py
   ```

5. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up MongoDB**
   ```bash
   # Start MongoDB locally or use Docker
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```

3. **Set environment variables**
   ```bash
   cp .env.example .env
   # Update MONGODB_URL and other settings
   ```

4. **Run the application**
   ```bash
   python start.py
   # or
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## ⚙️ Configuration

### Environment Variables

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=idocracy

# JWT Configuration
SECRET_KEY=your-secret-key-here-make-it-long-and-secure
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# App Configuration
DEBUG=True
API_V1_STR=/api/v1
PROJECT_NAME=IDocracy API
```

## 📖 Usage Examples

### 1. Authentication Flow

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@gov.tr", "password": "admin123"}'

# Use the returned access_token for authenticated requests
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 2. Create an Application

```bash
curl -X POST "http://localhost:8000/api/v1/apps/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My CRM App",
    "redirect_uris": ["https://crm.example.com/auth/callback"],
    "description": "Customer Relationship Management",
    "logo_url": "https://example.com/logo.png",
    "website_url": "https://crm.example.com"
  }'
```

### 3. Add User to Application

```bash
curl -X POST "http://localhost:8000/api/v1/apps/APP_ID/users" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER_ID",
    "roles": ["viewer"]
  }'
```

### 4. SSO Dashboard

```bash
# Get user's accessible apps
curl -X GET "http://localhost:8000/api/v1/sso/dashboard" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Launch App with SSO

```bash
# Launch app (returns redirect URL with token)
curl -X GET "http://localhost:8000/api/v1/sso/launch/APP_ID" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🔐 Security Features

### Authentication
- JWT-based authentication with access and refresh tokens
- Secure password hashing using bcrypt
- Token expiration and refresh mechanisms
- Role-based access control

### Authorization
- Admin role for system-wide access
- App-specific user roles (viewer, admin)
- Creator permissions for app management
- Fine-grained access control

### Data Protection
- Input validation using Pydantic
- SQL injection prevention (MongoDB)
- CORS configuration for cross-origin requests
- Secure client credential generation

## 🏗️ Project Structure

```
IDocracy/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection
│   ├── dependencies.py         # FastAPI dependencies
│   ├── models/                 # Pydantic models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── app.py
│   │   ├── app_user.py
│   │   ├── token.py
│   │   └── auth.py
│   ├── routers/                # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── apps.py
│   │   ├── app_users.py
│   │   ├── token.py
│   │   └── sso.py
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── app_service.py
│   │   ├── app_user_service.py
│   │   └── token_service.py
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       └── auth.py
├── scripts/
│   ├── __init__.py
│   └── create_admin.py         # Admin user creation script
├── docker-compose.yml          # Docker services configuration
├── Dockerfile                  # API container definition
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── start.py                   # Local development runner
└── README.md                  # This file
```

## 🛠️ Development

### Running Tests
```bash
# Run tests (when implemented)
pytest

# Run with coverage
pytest --cov=app
```

### Code Quality
```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Database Management
```bash
# Access MongoDB shell
docker exec -it idocracy_mongodb mongosh

# Backup database
docker exec idocracy_mongodb mongodump --out /backup

# Restore database
docker exec idocracy_mongodb mongorestore /backup
```

## 🔧 Troubleshooting

### Common Issues

1. **Port 8000 already in use**
   ```bash
   # Check what's using the port
   netstat -tulpn | grep :8000
   # Kill the process or change the port in docker-compose.yml
   ```

2. **MongoDB connection issues**
   ```bash
   # Check MongoDB container status
   docker ps | grep mongodb
   # Check MongoDB logs
   docker logs idocracy_mongodb
   ```

3. **Authentication errors**
   ```bash
   # Check API logs
   docker logs idocracy_api
   # Verify admin user exists
   docker exec -it idocracy_api python scripts/create_admin.py
   ```

### Logs
```bash
# View API logs
docker logs idocracy_api

# View MongoDB logs
docker logs idocracy_mongodb

# Follow logs in real-time
docker logs -f idocracy_api
```

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

##  Support
For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation

---

**IDocracy** - Centralized Identity and Access Management for Modern Applications