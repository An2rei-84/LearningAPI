"""
Фильтры для моделей приложения пользователей.
"""
import django_filters
from users.models import Payment


class PaymentFilter(django_filters.FilterSet):
    """
    Набор фильтров для модели Payment.
    Позволяет фильтровать по оплаченному курсу, оплаченному уроку и способу оплаты.
    Также поддерживает сортировку по дате оплаты.
    """

    paid_course = django_filters.CharFilter(
        field_name="paid_course__title", lookup_expr="icontains"
    )
    paid_lesson = django_filters.CharFilter(
        field_name="paid_lesson__title", lookup_expr="icontains"
    )
    payment_method = django_filters.ChoiceFilter(
        choices=Payment.PAYMENT_METHOD_CHOICES
    )
    # Сортировка по дате оплаты
    order_by_field = "payment_date"

    class Meta:
        model = Payment
        fields = ["paid_course", "paid_lesson", "payment_method"]
