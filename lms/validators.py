from rest_framework.serializers import ValidationError


def validate_youtube_link(value):
    """
    Валидатор, который проверяет, что ссылка ведет на youtube.com.
    """
    if value and "youtube.com" not in value:
        raise ValidationError("Ссылка должна вести на youtube.com")
