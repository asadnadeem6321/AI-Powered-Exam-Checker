"""
Utility functions and custom exception handler for the application
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # If the response is None, it's not a DRF exception
    if response is None:
        # Log the exception
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        
        # Return a generic error response
        return Response({
            'error': 'An unexpected error occurred',
            'detail': str(exc) if hasattr(exc, '__str__') else 'Internal server error',
            'status': 'error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Customize the response format
    custom_response_data = {
        'error': response.data.get('detail', 'An error occurred'),
        'status': 'error',
        'code': response.status_code
    }
    
    # Add field errors if they exist
    if isinstance(response.data, dict):
        field_errors = {}
        for field, errors in response.data.items():
            if field not in ['detail']:
                field_errors[field] = errors if isinstance(errors, list) else [errors]
        
        if field_errors:
            custom_response_data['field_errors'] = field_errors
    
    response.data = custom_response_data
    
    return response


def validate_file_size(file, max_size):
    """
    Validate file size
    """
    if file.size > max_size:
        from exam_checker.exceptions import FileUploadException
        raise FileUploadException(
            f"File size exceeds maximum limit of {max_size / 1024 / 1024:.2f}MB"
        )
    return True


def validate_file_type(file, allowed_types):
    """
    Validate file type
    """
    file_extension = file.name.split('.')[-1].lower()
    if file_extension not in allowed_types:
        from exam_checker.exceptions import FileUploadException
        raise FileUploadException(
            f"File type '{file_extension}' not allowed. Allowed types: {', '.join(allowed_types)}"
        )
    return True


def sanitize_text(text):
    """
    Sanitize text input by removing potentially harmful content
    """
    import re
    
    # Remove any potential script tags or HTML
    text = re.sub(r'<[^>]*>', '', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Trim
    text = text.strip()
    
    return text
