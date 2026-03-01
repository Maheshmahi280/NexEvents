"""
Custom DRF Exception Handler for Better Error Messages
"""

from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides better error messages for JWT authentication failures.
    """
    
    # Handle JWT-specific exceptions
    if isinstance(exc, (InvalidToken, TokenError)):
        logger.warning(f"JWT Authentication failed: {str(exc)}")
        return Response(
            {
                'detail': 'Authentication credentials were invalid. Please login again.',
                'error_type': 'AUTH_ERROR',
                'original_error': str(exc)
            },
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Call the default DRF exception handler
    response = drf_exception_handler(exc, context)
    
    # Log authentication errors
    if response is not None and response.status_code == 401:
        logger.warning(f"Authentication error: {type(exc).__name__}: {str(exc)}")
    
    return response
