from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.conf import settings

import stripe

from orders.models import Order
# Create your views here.

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


def payment_process(request):
    print('*'*30, request.session.all())
    order_id = request.session.get('order_id', None)
    order = get_object_or_404(Order, pk=order_id)

    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('payment:completed'))
        canceled_url = request.build_absolute_uri(reverse('payment:canceled'))

        # Stripe checkout session data
        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': success_url,
            'canceled_url': canceled_url,
            'line_items': [],
        }

        # Add order items to the Stripe checkout list session
        for item in order.items.all():
            session_data['line_items'].append({
                'price_data':{
                'unit_amount': int(item.price * Decimal('100')), # To convert price to cents
                'currency': 'usd',
                'product_data':{
                    'name': item.product.name,
                    },
                },
                'quantity': item.quantity,
            })

        # Create stripe checkout session
        session = stripe.checkout.Session.create(**session_data)
        # Redirect to stripe payment form
        return redirect(session.url, code=303)

    else:
        return render(request, 'payment/process.html', locals())


def payment_completed(request):
    return render(request, 'payment/completed.html')

def payment_canceled(request):
    return render(request, 'payment/canceled.html')