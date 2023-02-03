import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from orders.models import Order
from .tasks import payment_completed

"""
Run stripe after installing
stripe login 
after login --->
stripe listen --forward-to localhost:8000/payment/webhook/
"""

"""
To run rabbitmq on docker
docker run -d -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management

to run celery
celery -A core worker -l info
"""

@csrf_exempt
def stripe_webhook(request):
    event = None
    payload = request.body.decode('utf-8')
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature 
        return HttpResponse(status=400)
    
    if event.type == 'checkout.session.completed':
        session = event.data.object
        if session.mode == 'payment' and session.payment_status == 'paid':
            try:
                order = Order.objects.get(id=session.client_reference_id)
            except Order.DoesNotExist:
                return HttpResponse(status=404)
            # Make order as paid and add stripe_id
            order.paid = True
            order.stripe_id = session.payment_intent
            order.save()
            
            # Launch asynchronouns task
            payment_completed.delay(order.id)
    
    return HttpResponse(status=200)
