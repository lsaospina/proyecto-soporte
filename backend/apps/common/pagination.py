from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Paginación estándar uniforme para todos los listados de la API."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
