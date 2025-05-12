"""
Authentication session endpoint URL configurations.
Defines routes for session lifecycle: login, refresh, logout.
"""

from .root_prefix import ROOT_PREFIX

PREFIX = f'{ROOT_PREFIX}/sessions'  # Base path for session management

# Session management endpoints
POST_SESSIONS = ''  # Login → Create new session (issue access + refresh tokens)
PUT_SESSIONS = ''  # Refresh - Renew access token using refresh token
DELETE_SESSIONS = ''  # Logout - Revoke current session tokens
DELETE_SESSIONS_ALL = '/all'  # Logout all - Revoke all active sessions for the user
