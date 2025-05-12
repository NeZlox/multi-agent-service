"""
Message management URL configurations.
"""

PREFIX = '/messages'  # Base path for message management

# Message CRUD endpoints
GET_MESSAGES_URI = '/'  # List all active message
GET_MESSAGE_URI = '/{message_id:int}'  # Get specific message details
POST_MESSAGE_URI = '/chats/{chat_id:int}/messages'  # Create new message (admin only)
PUT_MESSAGE_URI = '/{message_id:int}'  # Update message
DELETE_MESSAGE_URI = '/{message_id:int}'  # Terminate message

POST_EXCHANGE_URI = '/{chat_id:int}/exchange'
