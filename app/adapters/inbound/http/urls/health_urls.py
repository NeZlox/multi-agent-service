"""
Health check endpoint URL configurations.
Defines routes for system monitoring and status checks.
"""

PREFIX = ''  # Root path for health endpoints

# Health monitoring endpoints
GET_HEALTH = '/service_health'  # Comprehensive system health check
GET_PING = '/ping'  # Quick liveness probe endpoint
