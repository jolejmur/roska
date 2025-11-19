"""
Custom pagination classes
"""
from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class with configurable page size
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        Custom paginated response format
        """
        response = super().get_paginated_response(data)
        response.data['page_size'] = self.page_size
        response.data['total_pages'] = self.page.paginator.num_pages
        return response
