"""
Chat management endpoint URL configurations.
Defines routes for CRUD operations on chat sessions.
"""

PREFIX = '/chats'  # Base path for chat management

# Chat CRUD endpoints
GET_CHATS_URI = '/'  # List all chats (admin only)
GET_CHAT_URI = '/{chat_id:int}'  # Get specific chat details
POST_CHAT_URI = '/'  # Register new chat
PUT_CHAT_URI = '/{chat_id:int}'  # Update chat information
DELETE_CHAT_URI = '/{chat_id:int}'  # Deactivate/delete chat account
