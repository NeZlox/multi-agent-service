"""
User account endpoint URL configurations for the Auth microservice.
Defines routes for user registration and profile access.
"""

from .root_prefix import ROOT_PREFIX

PREFIX = f'{ROOT_PREFIX}/users'  # Base path for user management

GET_CURRENT_USER_URI = '/me'  # Retrieve current user profile
POST_REGISTER_USER_URI = '/register'  # Register a new user
