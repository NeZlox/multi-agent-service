"""
Calendar component endpoint URL configurations.
Defines CRUD and time-range queries for calendar entries (events/tasks).
"""

from .root_prefix import ROOT_PREFIX

PREFIX = f'{ROOT_PREFIX}/components'  # Base path for component operations

POST_COMPONENT_URI = '/'  # Create a new calendar component
GET_COMPONENT_URI = '/{component_id:int}'  # Retrieve a specific component
PATCH_COMPONENT_URI = '/{component_id:int}'  # Update component details
DELETE_COMPONENT_URI = '/{component_id:int}'  # Remove component

# Range query
GET_COMPONENTS_BY_RANGE_URI = '/by-range'  # Retrieve components by time range
