"""
Category endpoint URL configurations.
Provides access to read-only category collection used in Agenda.
"""

from .root_prefix import ROOT_PREFIX

PREFIX = f'{ROOT_PREFIX}/categories'  # Base path for category operations

GET_CATEGORIES_URI = '/'  # List all available categories
