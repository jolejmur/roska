"""
Response utilities
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            'error': True,
            'detail': response.data.get('detail', str(exc)),
            'status_code': response.status_code
        }

        # Add field errors if present
        if isinstance(response.data, dict):
            errors = {k: v for k, v in response.data.items() if k != 'detail'}
            if errors:
                custom_response_data['errors'] = errors

        response.data = custom_response_data

    return response


def success_response(data=None, message=None, status_code=status.HTTP_200_OK):
    """
    Standardized success response
    """
    response_data = {
        'success': True,
    }

    if message:
        response_data['message'] = message

    if data:
        response_data['data'] = data

    return Response(response_data, status=status_code)


def error_response(message, errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Standardized error response
    """
    response_data = {
        'success': False,
        'error': message,
    }

    if errors:
        response_data['errors'] = errors

    return Response(response_data, status=status_code)
