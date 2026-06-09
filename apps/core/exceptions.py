from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import PermissionDenied
from django.http import Http404

def custom_exception_handler(exc, context):
    """
    Custom exception handler that standardizes the error response envelope.
    """
    response = exception_handler(exc, context)

    # Standardize our error envelope
    if response is not None:
        custom_response_data = {
            'success': False,
            'message': str(exc),
            'data': None,
            'errors': response.data
        }
        response.data = custom_response_data
    else:
        # Django native exceptions (like Http404, PermissionDenied) 
        # that DRF hasn't caught yet, or unhandled exceptions.
        if isinstance(exc, Http404):
            return Response({
                'success': False,
                'message': 'Not found.',
                'data': None,
                'errors': {}
            }, status=status.HTTP_404_NOT_FOUND)
        elif isinstance(exc, PermissionDenied):
            return Response({
                'success': False,
                'message': 'Permission denied.',
                'data': None,
                'errors': {}
            }, status=status.HTTP_403_FORBIDDEN)

    return response
