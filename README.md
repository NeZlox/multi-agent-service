# Multi-Agent Service

A sophisticated microservices gateway and AI agent orchestration platform built with Litestar, featuring real-time chat capabilities, intelligent message processing, and seamless integration with multiple backend services.

## 🌟 Features

### Core Gateway Functionality
- **Reverse Proxy Architecture**: Intelligent request routing to upstream microservices
- **Authentication Gateway**: JWT-based authentication with session management
- **AI Agent Orchestration**: Pluggable AI agent system with multiple backend support
- **Real-time Chat System**: Multi-agent chat sessions with persistent message history

### Advanced Capabilities
- **Smart Middleware Stack**: Authentication, request logging, and proxy middleware
- **Health Monitoring**: Comprehensive system health checks with dependency tracking
- **Role-based Access Control**: Granular permissions with environment-aware role groups
- **Structured Logging**: Advanced logging with performance monitoring
- **Database Migrations**: Automated schema management with Alembic

### Integration Services
- **Agenda Service**: Calendar and scheduling operations (CRUD for calendars, events, components)
- **Auth Service**: User authentication, registration, and session management
- **Snapshot Service**: ML-powered message analysis and user behavior insights
- **AI Agents**: Extensible AI backend system with automatic discovery

## 🏗️ Architecture

### System Architecture Diagram

The diagram below illustrates the high-level architecture of the Multi-Agent Service and its integration into the larger Personal Growth Support Platform.

It demonstrates the logical layering of the system, the separation between infrastructure and intelligent agents, and the division of responsibility among team members.

![System Architecture Diagram](docs/img_architecture.png)

### The Project Structure
The service follows **Clean Architecture** principles with clear separation of concerns:

```
multi-agent-service/
├── app/
│   ├── adapters/                     # Interface adapters
│   │   ├── inbound/                  # HTTP controllers and routing
│   │   │   ├── http/controllers/     # REST API endpoints
│   │   │   └── urls/                 # URL configurations
│   │   └── outbound/                 # Repository implementations
│   │       └── repositories/         # Database access layer
│   ├── application/                  # Business logic layer
│   │   ├── ai_agent_gateway/         # AI agent abstractions
│   │   ├── services/                 # Domain services
│   │   └── use_case/                 # Application use cases
│   ├── config/                       # Configuration management
│   │   ├── proxy_routes/             # Reverse proxy routing rules
│   │   └── route_registry/           # Dynamic route registration
│   ├── infrastructure/               # Technical infrastructure
│   │   ├── db/migrations/            # Database schema evolution
│   │   └── di/providers/             # Dependency injection providers
│   ├── lib/                          # Shared libraries
│   │   ├── errors/                   # Exception handling framework
│   │   ├── http/                     # HTTP client utilities
│   │   ├── schemas/                  # Shared schemas for data exchange between layers and services
│   │   ├── security/                 # Authentication & authorization
│   │   └── utils/                    # Helper functions
│   └── server/                       # Server configuration
│       ├── life_cycle/               # Application lifecycle management
│       └── middleware/               # ASGI middleware stack
```

### Key Design Patterns

- **Gateway Pattern**: Central entry point for multiple microservices
- **Repository Pattern**: Database abstraction with Advanced Alchemy
- **Factory Pattern**: AI agent discovery and instantiation
- **Middleware Chain**: Request processing pipeline
- **Dependency Injection**: Clean service composition

## 🚀 Quick Start

### Prerequisites

- **Python 3.12**
- **PostgreSQL 14+**
- **Docker & Docker Compose** (recommended)
- **Poetry 1.8+** for dependency management


### Docker Deployment

1. Clone the repository:
   ```bash
   git clone https://github.com/NeZlox/authorization-service.git
   ```

2. Navigate to the project directory:
   ```bash
   cd authorization-service
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   (Edit the `.env` file with your configuration)

4. Start the services:
   ```bash
   docker-compose up -d
   ```

5. To stop the services:
   ```bash
   docker-compose down
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

#### Database Configuration
```bash
# PostgreSQL connection string
POSTGRES_DSN=postgresql+asyncpg://username:password@localhost:5432/database_name

# Connection pool settings
DATABASE_POOL_SIZE=30                    # Maximum number of permanent connections
DATABASE_MAX_POOL_OVERFLOW=20           # Additional connections beyond pool_size
DATABASE_POOL_TIMEOUT=30                # Seconds to wait for connection
DATABASE_POOL_RECYCLE=300               # Seconds before connection recycling

# Database schema
POSTGRES_SCHEMA=public                   # PostgreSQL schema name
```

#### Application Settings
```bash
# Application mode: DEV, STAGE, PROD, TEST
MODE=DEV

# Enable debug mode (detailed error messages)
DEBUG=true
```

#### Authentication & Security
```bash
# JWT configuration for token validation
JWT_ALGORITHM=RS256                      # JWT signing algorithm
JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----
...your RSA public key...
-----END PUBLIC KEY-----"
```

#### Microservice Integration
```bash
# Upstream service URLs
AUTH_SERVICE_URL=http://auth-service:8001           # Authentication service
AGENDA_SERVICE_URL=https://calendar.nanny.su        # Calendar/scheduling service
SNAPSHOT_SERVICE_URL=http://snapshot-service:8003   # ML analytics service
```

#### Logging Configuration
```bash
# Logging settings
LOG_LEVEL=10                            # 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR
LOG_JSON=false                          # Use JSON logging format (true for production)
```

## 🛠️ Development

For local development without Docker:

1. Prepare environment:
   ```bash
   cp .env.example .env
   # Edit .env to use your local Postgres credentials
   ```

2. Install dependencies:
   ```bash
   poetry update
   poetry install
   ```

3. Setup database:
   ```bash
   litestar database upgrade
   ```

4. Run development server:
   ```bash
   uvicorn app.asgi:app --host 127.0.0.1 --port 8000 --reload
   ```
   

### Available Commands

| Command | Description |
|---------|-------------|
| `poetry install` | Install all dependencies |
| `poetry update` | Update dependencies |
| `poetry run ruff check . --fix` | Run code linting and auto-fix |
| `poetry run ruff format .` | Format code |
| `litestar database upgrade` | Apply database migrations |
| `litestar database downgrade` | Revert last migration |
| `litestar database revision --autogenerate -m "description"` | Create new migration |
| `uvicorn app.asgi:app --reload` | Run development server with auto-reload |

### Code Quality

The project uses **Ruff** for linting and formatting:

```bash
# Check and fix linting issues
poetry run ruff check . --fix

# Format code
poetry run ruff format .
```

### Database Migrations

```bash
# Create a new migration
poetry run litestar database revision --autogenerate -m "Add new feature"

# Apply migrations
poetry run litestar database upgrade

# Rollback last migration
poetry run litestar database downgrade
```

## 🔌 API Endpoints

### Health & Monitoring
- `GET /api/health/service_health` - Comprehensive system health check
- `GET /api/health/ping` - Simple liveness probe

### Authentication (Proxied to Auth Service)
- `POST /api/v1/auth/sessions` - User login
- `PUT /api/v1/auth/sessions` - Refresh access token  
- `DELETE /api/v1/auth/sessions` - User logout
- `DELETE /api/v1/auth/sessions/all` - Terminate all sessions
- `GET /api/v1/auth/users/me` - Get current user profile
- `POST /api/v1/auth/users/register` - Register new user

### Chat & Messaging
- `GET /api/v1/chats/` - List all chats (admin)
- `POST /api/v1/chats/` - Create new chat
- `GET /api/v1/chats/{chat_id}` - Get chat details
- `PUT /api/v1/chats/{chat_id}` - Update chat
- `DELETE /api/v1/chats/{chat_id}` - Delete chat

### Messages
- `GET /api/v1/messages/` - List messages (admin)
- `POST /api/v1/messages/chats/{chat_id}/messages` - Create message
- `POST /api/v1/messages/{chat_id}/exchange` - Send message and get AI response
- `GET /api/v1/messages/{message_id}` - Get message details
- `PUT /api/v1/messages/{message_id}` - Update message
- `DELETE /api/v1/messages/{message_id}` - Delete message

### Agenda Operations (Proxied to Agenda Service)
- `GET /api/v1/agenda/calendars/` - List calendars
- `POST /api/v1/agenda/calendars/` - Create calendar
- `GET /api/v1/agenda/calendars/{id}` - Get calendar
- `PATCH /api/v1/agenda/calendars/{id}` - Update calendar
- `DELETE /api/v1/agenda/calendars/{id}` - Delete calendar

## 🤖 AI Agent System

### Agent Architecture

The service features a **pluggable AI agent system** that allows for multiple AI backends:

```python
# Built-in agents
from app.application.ai_agent_gateway import AIAgentFactory

# Get an agent by name
agent = AIAgentFactory.get('agenda')
response = await agent.generate(chat_id=1, new_message="Hello!")
```

### Adding Custom Agents

1. **Create a new agent class:**
   ```python
   # app/application/ai_agent_gateway/custom/my_agent.py
   from app.application.ai_agent_gateway import AIAgentGatewayInterface
   
   class MyCustomAgent(AIAgentGatewayInterface):
       name = 'my_custom_agent'
       
       @classmethod
       async def _get_health_status(cls):
           # Health check implementation
           return HealthStatus.OK, None
           
       @classmethod  
       async def generate(cls, chat_id: int, new_message: str) -> str:
           # AI generation logic
           return "AI response"
   ```

2. **The agent will be automatically discovered** through the factory's discovery mechanism.

### Current Agents

- **Agenda Agent**: Integrates with calendar/scheduling functionality
- **Extensible**: Add more agents by implementing `AIAgentGatewayInterface`

## 🔄 Reverse Proxy Configuration

The service acts as an intelligent reverse proxy, routing requests to appropriate upstream services:

### Proxy Routes

```python
# Auth service routes
/api/v1/auth/* → AUTH_SERVICE_URL

# Agenda service routes  
/api/v1/agenda/* → AGENDA_SERVICE_URL (strips /agenda prefix)

# Snapshot service routes
/api/v1/snapshot/* → SNAPSHOT_SERVICE_URL
```

### Adding New Proxy Routes

```python
# app/config/proxy_routes/new_service.py
from app.config.route_registry import route_registry

route_registry.register(
    prefix='/api/v1/newservice',
    upstream_base='http://new-service:8004',
    strip_url='/newservice'  # Optional URL rewriting
)
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app

# Run specific test file
poetry run pytest tests/test_specific.py
```


## 📊 Monitoring & Observability

### Health Checks

The service provides comprehensive health monitoring:

- **Database connectivity**: PostgreSQL schema validation
- **Upstream services**: Auth, Agenda, Snapshot service availability  
- **AI agents**: Backend agent health status
- **System resources**: Memory, connections, etc.

### Logging

Structured logging with **structlog**:

```python
from app.lib.logger import logger

await logger.ainfo("Processing request", user_id=123, action="create_chat")
```

### Performance Monitoring

Built-in request timing middleware tracks response times and logs performance metrics.

## 🛡️ Security

### Authentication Flow

1. **Client sends credentials** to `/api/v1/auth/sessions`
2. **Auth service validates** and returns JWT tokens
3. **Gateway validates JWT** on subsequent requests using public key
4. **User context attached** to request scope for controllers

### Role-Based Access Control

```python
# Environment-aware role groups
RoleGroup.ADMIN     # Admin-only access
RoleGroup.STAFF     # Staff and admin access  
RoleGroup.COMMON    # All authenticated users
RoleGroup.PRIVATE   # Development-only (disabled in production)
```

### Security Features

- **JWT token validation** with RSA signatures
- **Automatic session management** with refresh tokens
- **Request/response sanitization** in proxy middleware
- **Environment-based role restrictions**

## 🚢 Deployment

### Production Deployment

1. **Set production environment:**
   ```bash
   MODE=PROD
   DEBUG=false
   LOG_JSON=true
   ```

2. **Configure production database:**
   ```bash
   POSTGRES_DSN=postgresql+asyncpg://prod_user:secure_password@db:5432/prod_db
   ```

3. **Set up proper JWT keys:**
   ```bash
   JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----
   ...production RSA public key...
   -----END PUBLIC KEY-----"
   ```

4. **Deploy with Docker Compose:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Scaling Considerations

- **Stateless design**: Service can be horizontally scaled
- **Database connection pooling**: Configured for high concurrency
- **Proxy middleware**: Efficient request forwarding
- **Health checks**: Ready for load balancer integration

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** following the project structure
4. **Run tests and linting**: `poetry run ruff check . --fix && poetry run pytest`
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Development Guidelines

- Follow **Clean Architecture** principles
- Write **comprehensive tests** for new features
- Use **type hints** throughout the codebase
- Follow **Ruff** linting rules
- Document **API changes** in the README

## 🎯 Roadmap

- [ ] **Enhanced AI Agents**: Support for more AI backends (OpenAI, Anthropic, etc.)
- [ ] **WebSocket Support**: Real-time chat capabilities
- [ ] **Message Queuing**: Async message processing with Redis/RabbitMQ
- [ ] **API Rate Limiting**: Request throttling and quotas
- [ ] **Caching Layer**: Redis integration for improved performance
- [ ] **Monitoring Dashboard**: Real-time system metrics and alerts
- [ ] **Multi-tenant Support**: Isolated environments for different organizations

---

## 🔗 Related Services

This gateway integrates with the **Personal Growth Platform** ecosystem:

- **[Auth Service](https://github.com/NeZlox/authorization-service)**: User authentication and authorization
- **[Agenda Service](https://github.com/ChS23?tab=repositories)**: Calendar and scheduling management  
- **[Snapshot Service](https://github.com/letmly?tab=repositories)**: ML-powered user analytics
- **[Personal Growth SDK](https://github.com/NeZlox/personal-growth-sdk)**: Shared models and utilities

---

##  ――✧✦⋆ 𝓐𝓾𝓽𝓱𝓸𝓻: [**NeZlox**](https://github.com/NeZlox) ⋆✦✧――
