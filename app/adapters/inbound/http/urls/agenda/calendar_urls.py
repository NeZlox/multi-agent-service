"""
Calendar endpoint URL configurations.
Supports CRUD operations on user calendars.
"""

from .root_prefix import ROOT_PREFIX

PREFIX = f'{ROOT_PREFIX}/calendars'  # Base path for calendar management

GET_CALENDARS_URI = '/'  # List all calendars
GET_CALENDAR_URI = '/{calendar_id:int}'  # Get calendar by ID
POST_CALENDAR_URI = '/'  # Create new calendar
PATCH_CALENDAR_URI = '/{calendar_id:int}'  # Update calendar
DELETE_CALENDAR_URI = '/{calendar_id:int}'  # Delete calendar
