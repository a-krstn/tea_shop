import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order


@csrf_exempt        # декоратор предотвращает выполнение веб-фреймворком Django валидации CSRF
def stripe_webhook(request):
    """функция получает JSON-данные о событии,
    проверяет эти данные и помечает заказ оплаченным,
    если по результатам проверки события он является таковым"""
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        # верификации заголовка подписи под событием
        event = stripe.Webhook.construct_event(
                    payload,
                    sig_header,
                    settings.STRIPE_WEBHOOK_SECRET)
    except ValueError as e:
        # Недопустимые данные
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Недопустимая подпись
        return HttpResponse(status=400)

    if event.type == 'checkout.session.completed':
        session = event.data.object
        if session.mode == 'payment' and session.payment_status == 'paid':
            try:
                order = Order.objects.get(id=session.client_reference_id)
            except Order.DoesNotExist:
                return HttpResponse(status=404)
            # пометить заказ как оплаченный
            order.paid = True
            # сохранить ИД платежа Stripe
            order.stripe_id = session.payment_intent
            order.save()
            # запустить асинхронное задание
            # payment_completed.delay(order.id)

    return HttpResponse(status=200)
