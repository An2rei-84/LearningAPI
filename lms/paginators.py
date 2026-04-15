from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """
    Кастомный класс пагинации для списков.
    """
    page_size = 10  # Количество элементов на странице по умолчанию
    page_size_query_param = 'page_size'  # Параметр для установки количества элементов на странице через URL
    max_page_size = 100  # Максимальное количество элементов на странице
