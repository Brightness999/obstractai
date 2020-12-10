import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from apps.utils.decorators import catch_stripe_errors
from ..models import Payment

EXPECTED_PAYMENT_AMOUNT = 2500  # in cents

@method_decorator(login_required, name='dispatch')
class PaymentView(TemplateView):
    template_name = 'pegasus/examples/payments/payments.html'

    def get_context_data(self, **kwargs):
        return {
            'stripe_key': settings.STRIPE_TEST_PUBLIC_KEY,
            'payments': self.request.user.pegasus_payments.all(),
            'amount': EXPECTED_PAYMENT_AMOUNT,
            'active_tab': 'payments',
        }


@login_required
def payment_confirm(request, payment_id):
    """
    Confirmation page after making a payment.
    """
    payment = get_object_or_404(Payment, user=request.user, id=payment_id)
    return render(request, 'pegasus/examples/payments/payment_confirm.html', {
        'payment': payment,
        'active_tab': 'payments',
    })


@login_required
@require_POST
@catch_stripe_errors
def accept_payment(request):
    """
    Accept a payment with a token from Stripe
    """
    amount = int(request.POST['amount'])

    # since this value is coming from the front-end, we need to double-check it is correct
    if amount != EXPECTED_PAYMENT_AMOUNT:
        raise ValueError('Received unexpected payment amount {}'.format(amount))

    name = request.POST['name']
    token = request.POST['stripeToken']
    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
    user = request.user
    email = request.user.email
    charge = stripe.Charge.create(
        amount=amount,
        currency="usd",
        description=name,
        source=token,
        receipt_email=email,
    )
    payment = Payment.objects.create(
        charge_id=charge.id,
        amount=charge.amount,
        name=name,
        user=user,
    )
    return HttpResponseRedirect(reverse('pegasus_examples:payment_confirm', args=[payment.payment_id]))


