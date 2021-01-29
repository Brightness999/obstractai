import json, decimal

import djstripe
import stripe
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import mail_admins
from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST
from djstripe.enums import PlanInterval
from djstripe.models import Product, Plan, Subscription
from djstripe import settings as djstripe_settings
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime, timedelta
from django.conf import settings

from apps.utils.decorators import catch_stripe_errors
from apps.web.meta import absolute_url
from .decorators import redirect_subscription_errors
from .helpers import get_friendly_currency_amount
from .metadata import get_active_products_with_metadata,\
    get_product_and_metadata_for_subscription, ACTIVE_PLAN_INTERVALS, get_active_plan_interval_metadata
from project.models import UserIntelGroupRoles, IntelGroups, Feeds, PlanHistory
from apps.users.models import CustomUser
from pegasus.apps.examples.models import Payment


class ProductWithMetadataAPI(APIView):

    def get(self, request, *args, **kw):
        products_with_metadata = get_active_products_with_metadata()
        return Response(
            data=[p.to_dict() for p in products_with_metadata]
        )


@redirect_subscription_errors
@login_required
def subscription(request, subscription_holder=None, groupid=2):
    subscription_holder = subscription_holder if subscription_holder else request.user
    if IntelGroups.objects.filter(id=groupid).values()[0]['plan_id'] != None:
        return _view_subscription(request, subscription_holder, groupid)
    else:
        return _upgrade_subscription(request, subscription_holder, groupid)


def _view_subscription(request, subscription_holder, groupid):
    """
    Show user's active subscription
    """
    # assert subscription_holder.has_active_subscription()
    sub_id = IntelGroups.objects.filter(id=groupid).values()[0]['plan_id']
    planid = Subscription.objects.filter(djstripe_id=sub_id).values()[0]['plan_id']
    productid = Plan.objects.filter(djstripe_id=planid).values()[0]['product_id']
    active_products = list(get_active_products_with_metadata())
    default_products = [p for p in active_products if p.metadata.is_default]
    default_product = default_products[0] if default_products else active_products[0]

    def _to_dict(product_with_metadata):
        # for now, just serialize the minimum amount of data needed for the front-end
        product_data = {}
        if PlanInterval.year in ACTIVE_PLAN_INTERVALS:
            product_data['annual_plan'] = {
                'stripe_id': product_with_metadata.annual_plan.id,
                'payment_amount': get_friendly_currency_amount(product_with_metadata.annual_plan.amount,
                                                               product_with_metadata.annual_plan.currency),
                'monthly_amount': get_friendly_currency_amount(product_with_metadata.annual_plan.amount / 12,
                                                               product_with_metadata.annual_plan.currency),
                'interval': PlanInterval.year,  # set to month because we're dividing price by 12
            }
        if PlanInterval.month in ACTIVE_PLAN_INTERVALS:
            product_data['monthly_plan'] = {
                'stripe_id': product_with_metadata.monthly_plan.id,
                'payment_amount': get_friendly_currency_amount(product_with_metadata.monthly_plan.amount,
                                                               product_with_metadata.monthly_plan.currency),
                'monthly_amount': get_friendly_currency_amount(product_with_metadata.monthly_plan.amount,
                                                               product_with_metadata.monthly_plan.currency),
                'interval': PlanInterval.month,
            }
        return product_data


    return render(request, 'subscriptions/view_subscription.html', {
        'active_tab': 'subscription',
        'subscription': subscription_holder.active_stripe_subscription,
        'subscription_urls': _get_subscription_urls(subscription_holder),
        'friendly_payment_amount': get_friendly_currency_amount(
            subscription_holder.active_stripe_subscription.plan.amount,
            subscription_holder.active_stripe_subscription.plan.currency,
        ),
        'product': get_product_and_metadata_for_subscription(subscription_holder.active_stripe_subscription),
        'stripe_api_key': djstripe_settings.STRIPE_PUBLIC_KEY,
        'default_product': default_product,
        'active_products': active_products,
        'active_products_json': {str(p.stripe_id): _to_dict(p) for p in active_products},
        'active_plan_intervals': get_active_plan_interval_metadata(),
        'default_to_annual': ACTIVE_PLAN_INTERVALS[0] == PlanInterval.year,
        'payment_metadata': _get_payment_metadata_from_request(request),
        'current_product_id': Product.objects.filter(djstripe_id=productid).values()[0]['id'],
        'groupid': groupid,
    })


def _upgrade_subscription(request, subscription_holder, groupid):
    """
    Show subscription upgrade form / options.
    """
    # assert not subscription_holder.has_active_subscription()

    active_products = list(get_active_products_with_metadata())
    default_products = [p for p in active_products if p.metadata.is_default]
    default_product = default_products[0] if default_products else active_products[0]

    def _to_dict(product_with_metadata):
        # for now, just serialize the minimum amount of data needed for the front-end
        product_data = {}
        if PlanInterval.year in ACTIVE_PLAN_INTERVALS:
            product_data['annual_plan'] = {
                'stripe_id': product_with_metadata.annual_plan.id,
                'payment_amount': get_friendly_currency_amount(product_with_metadata.annual_plan.amount,
                                                               product_with_metadata.annual_plan.currency),
                'monthly_amount': get_friendly_currency_amount(product_with_metadata.annual_plan.amount / 12,
                                                               product_with_metadata.annual_plan.currency),
                'interval': PlanInterval.year,  # set to month because we're dividing price by 12
            }
        if PlanInterval.month in ACTIVE_PLAN_INTERVALS:
            product_data['monthly_plan'] = {
                'stripe_id': product_with_metadata.monthly_plan.id,
                'payment_amount': get_friendly_currency_amount(product_with_metadata.monthly_plan.amount,
                                                               product_with_metadata.monthly_plan.currency),
                'monthly_amount': get_friendly_currency_amount(product_with_metadata.monthly_plan.amount,
                                                               product_with_metadata.monthly_plan.currency),
                'interval': PlanInterval.month,
            }
        return product_data

    return render(request, 'subscriptions/upgrade_subscription.html', {
        'active_tab': 'subscription',
        'stripe_api_key': djstripe_settings.STRIPE_PUBLIC_KEY,
        'default_product': default_product,
        'active_products': active_products,
        'active_products_json': {str(p.stripe_id): _to_dict(p) for p in active_products},
        'active_plan_intervals': get_active_plan_interval_metadata(),
        'default_to_annual': ACTIVE_PLAN_INTERVALS[0] == PlanInterval.year,
        'subscription_urls': _get_subscription_urls(subscription_holder),
        'payment_metadata': _get_payment_metadata_from_request(request),
        'groupid': groupid,
    })


def _get_payment_metadata_from_request(request):
    return {
        'user_id': request.user.id,
        'user_email': request.user.email,
        
    }


@login_required
def subscription_success(request):
    return _subscription_success(request, request.user)

def _subscription_success(request, subscription_holder):
    stripe.api_key = djstripe_settings.STRIPE_SECRET_KEY
    if not subscription_holder.has_active_subscription():
        subscription = subscription_holder.subscription
        if not subscription:
            messages.error(
                request,
               "Oops, it looks like there was a problem processing your payment. "
               "Please try again, or get in touch if you think this is a mistake."
            )
        else:
            # 3D-Secure workflow hopefully completed successfully,
            # re-sync the subscription and hopefully it will be active
            subscription.sync_from_stripe_data(subscription.api_retrieve())

    if subscription_holder.has_active_subscription():
        subscription_name = get_product_and_metadata_for_subscription(
            subscription_holder.active_stripe_subscription
        ).metadata.name
        messages.success(request, f"You've successfully signed up for {subscription_name}. "
                                  "Thanks so much for the support!")
        # notify admins when someone signs up
        mail_admins(
            subject=f"Hooray! Someone just signed up for a {subscription_name} subscription!",
            message="Email: {}".format(request.user.email),
            fail_silently=True,
        )
    
    redirect = reverse('subscriptions:subscription_details')
    
    return HttpResponseRedirect(redirect)


@login_required
@require_POST
def create_stripe_portal_session(request, subscription_holder=None):
    subscription_holder = subscription_holder if subscription_holder else request.user
    subscription_urls = _get_subscription_urls(subscription_holder)

    stripe.api_key = djstripe_settings.STRIPE_SECRET_KEY
    if not subscription_holder.subscription or not subscription_holder.subscription.customer:
        messages.error(request, _("Whoops, we couldn't find a subscription associated with your account!"))
        return HttpResponseRedirect(subscription_urls['subscription_details'])

    session = stripe.billing_portal.Session.create(
      customer=subscription_holder.subscription.customer.id,
      return_url=absolute_url(subscription_urls['subscription_details']),
    )
    return HttpResponseRedirect(session.url)


@login_required
@require_POST
@catch_stripe_errors
@transaction.atomic
def create_customer(request, subscription_holder=None):
    """
    Create a Stripe Customer and Subscription object and map them onto the subscription_holder

    Expects the inbound POST data to look something like this:
    {
        'email': 'cory@example.com',
        'userId': '23',
        'payment_method': 'pm_1GGgZaIYTEadrA0y0tthZ5UH'
    }
    """
    subscription_holder = subscription_holder if subscription_holder else request.user
    request_body = json.loads(request.body.decode('utf-8'))
    user_id = int(request_body['user_id'])
    email = request_body['user_email']
    assert request.user.id == user_id
    assert request.user.email == email
    
    subid = IntelGroups.objects.filter(id=request_body['groupid']).last().plan_id
    if subid != None:
        planid = Subscription.objects.filter(djstripe_id=subid).last().plan_id
        productid = Plan.objects.filter(djstripe_id=planid).last().product_id
        plan_id = request_body['plan_id']
        product_id = Plan.objects.filter(id=plan_id).last().product_id
        interval = Plan.objects.filter(id=plan_id).last().interval
        product_name = Product.objects.filter(djstripe_id=product_id).last().name
        max_users = Product.objects.filter(djstripe_id=product_id).last().metadata['max_users']
        max_feeds = Product.objects.filter(djstripe_id=product_id).last().metadata['max_feeds']
        current_product_name = Product.objects.filter(djstripe_id=productid).last().name
        current_period_end = Subscription.objects.filter(djstripe_id=subid).last().current_period_end
        current_period_start = Subscription.objects.filter(djstripe_id=subid).last().current_period_start
        current_interval = Plan.objects.filter(djstripe_id=planid).last().interval
        if current_interval == 'month' and interval == 'year':
            return JsonResponse(
                data = {'monthyear':True}
            )
        if current_interval == 'year' and interval == 'month':
            return JsonResponse(
                data = {'yearmonth':True}
            )
        if (current_product_name=='Large' and product_name=='Medium') or (current_product_name=='Large' and product_name=='Starter') or (current_product_name=='Medium' and product_name=='Starter'):
            users = UserIntelGroupRoles.objects.filter(intelgroup_id=request_body['groupid']).all()
            feeds = Feeds.objects.filter(intelgroup_id=request_body['groupid'])
            if len(users) > int(max_users) and len(feeds) > int(max_feeds):
                result = {
                    'users': len(users),
                    'feeds': len(feeds)
                }
                return JsonResponse(
                    data=result,
                )
            elif len(users) > int(max_users):
                result = {
                    'users': len(users),
                }
                return JsonResponse(
                    data=result,
                )
            elif len(feeds) > int(max_feeds):
                result = {
                    'feeds': len(feeds)
                }
                return JsonResponse(
                    data=result,
                )
        if current_product_name == 'Medium' and product_name == 'Large':
            delta_time = current_period_end.date()-datetime.now().date()
            current_amount = Plan.objects.filter(djstripe_id=planid).last().amount
            amount = Plan.objects.filter(id=request_body['plan_id']).last().amount
            addition_amount = decimal.Decimal(delta_time/(current_period_end.date()-current_period_start.date()))*(amount-current_amount)
            name = 'Addition Payment2'
            token = request_body['stripeToken']
            stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
            user = request.user
            email = request.user.email
            charge = stripe.Charge.create(
                amount=int(addition_amount*100),
                currency="usd",
                description=name,
                source=token,
                receipt_email=email,
            )
            payment = Payment.objects.create(
                charge_id=charge.id,
                amount=int(charge.amount),
                name=name,
                user=user,
            )
            print(addition_amount)

    
    payment_method = request_body['payment_method']
    plan_id = request_body['plan_id']
    stripe.api_key = djstripe_settings.STRIPE_SECRET_KEY

    # first sync payment method to local DB to workaround https://github.com/dj-stripe/dj-stripe/issues/1125
    payment_method_obj = stripe.PaymentMethod.retrieve(payment_method)
    djstripe.models.PaymentMethod.sync_from_stripe_data(payment_method_obj)
    # create customer objects
    # This creates a new Customer in stripe and attaches the default PaymentMethod in one API call.
    customer = stripe.Customer.create(
      payment_method=payment_method,
      email=email,
      invoice_settings={
        'default_payment_method': payment_method,
      },
    )

    # create the local customer object in the DB so the subscription can use it
    djstripe.models.Customer.sync_from_stripe_data(customer)

    # create subscription
    subscription = stripe.Subscription.create(
      customer=customer.id,
      items=[
        {
          'plan': plan_id,
        },
      ],
      expand=['latest_invoice.payment_intent', 'pending_setup_intent'],
    )
    djstripe_subscription = djstripe.models.Subscription.sync_from_stripe_data(subscription)

    # set subscription object on the subscription holder
    subscription_holder.subscription = djstripe_subscription
    subscription_holder.save()
    sub_id = djstripe.models.Subscription.objects.last()
    IntelGroups.objects.filter(id=request_body['groupid']).update(plan_id=sub_id.djstripe_id);
    PlanHistory.objects.create(intelgroup_id=request_body['groupid'], sub_id=sub_id.djstripe_id, start=sub_id.current_period_start, end=sub_id.current_period_end)
    data = {
        'customer': customer,
        'subscription': subscription
    }
    return JsonResponse(
        data=data,
    )


def _get_subscription_urls(subscription_holder):
    # get URLs for subscription helpers
    url_bases = [
        'subscription_details',
        'create_customer',
        'create_stripe_portal_session',
        'subscription_success',
        'subscription_demo',
        'subscription_gated_page',
    ]

    def _construct_url(base):
        return reverse(f'subscriptions:{base}')
        

    return {
        url_base: _construct_url(url_base) for url_base in url_bases
    }


@login_required
def subscription_demo(request, subscription_holder=None):
    subscription_holder = subscription_holder if subscription_holder else request.user
    return render(request, 'subscriptions/demo.html', {
        'active_tab': 'subscription_demo',
        'subscription': subscription_holder.active_stripe_subscription,
        'product': get_product_and_metadata_for_subscription(
            subscription_holder.active_stripe_subscription
        ),
        'subscription_urls': _get_subscription_urls(subscription_holder)
    })


@login_required
def subscription_gated_page(request, subscription_holder=None):
    subscription_holder = subscription_holder if subscription_holder else request.user
    if not subscription_holder.has_active_subscription():
        return render(request, 'subscriptions/subscription_required.html')
    else:
        return render(request, 'subscriptions/subscription_gated_page.html')



