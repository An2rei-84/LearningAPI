from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Проверяет, является ли текущий пользователь владельцем объекта пользователя.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешение только для владельца объекта
        return obj == request.user
