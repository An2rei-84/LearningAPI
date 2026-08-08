from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Проверяет, является ли текущий пользователь владельцем объекта пользователя.
    """

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "user"):
            return obj.user == request.user
        return obj == request.user
