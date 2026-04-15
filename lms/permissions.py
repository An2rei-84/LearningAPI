from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    """
    Проверяет, является ли текущий пользователь модератором.
    """

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moderators").exists()


class IsOwner(BasePermission):
    """
    Проверяет, является ли текущий пользователь владельцем объекта.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешение только для владельца объекта
        return obj.owner == request.user
