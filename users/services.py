import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name):
    """
    Создает продукт в Stripe.
    """
    product = stripe.Product.create(name=name)
    return product


def create_stripe_price(product_id, amount):
    """
    Создает цену для продукта в Stripe.
    """
    # Цены в Stripe указываются в копейках
    price = stripe.Price.create(
        product=product_id,
        unit_amount=int(amount * 100),
        currency="rub",
    )
    return price


def create_stripe_session(price_id, success_url, cancel_url):
    """
    Создает сессию для оплаты в Stripe.
    """
    session = stripe.checkout.Session.create(
        success_url=success_url,
        cancel_url=cancel_url,
        line_items=[{"price": price_id, "quantity": 1}],
        mode="payment",
    )
    return session


def retrieve_stripe_session(session_id):
    """
    Получает информацию о сессии Stripe.
    """
    return stripe.checkout.Session.retrieve(session_id)
