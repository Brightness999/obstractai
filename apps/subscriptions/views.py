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
from project.models import UserIntelGroupRoles, IntelGroups, Feeds, PlanHistory, GroupFeeds
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
def subscription(request, subscription_holder=None, groupid=0):
    subscription_holder = subscription_holder if subscription_holder else request.user
    if groupid == 0:
        subid = CustomUser.objects.filter(id=request.user.id).last().subscription_id
        groupid = IntelGroups.objects.filter(plan_id=subid).last().id
        return _view_subscription(request, subscription_holder, groupid)
    else:
        if IntelGroups.objects.filter(id=groupid).last().plan_id != None or IntelGroups.objects.filter(id=groupid).last().isfree:
            return _view_subscription(request, subscription_holder, groupid)
        else:
            return _upgrade_subscription(request, subscription_holder, groupid)


def _view_subscription(request, subscription_holder, groupid):
    """
    Show user's active subscription
    """
    # assert subscription_holder.has_active_subscription()
    sub_id = IntelGroups.objects.filter(id=groupid).last().plan_id
    card_exist = True
    if IntelGroups.objects.filter(id=groupid).last().isfree:
        if sub_id == None:
            card_exist = False
        planid = Plan.objects.filter(amount=0).last().djstripe_id
        current_period_end = ''
    else:
        planid = Subscription.objects.filter(djstripe_id=sub_id).last().plan_id
        current_period_end = Subscription.objects.filter(djstripe_id=sub_id).last().current_period_end
    productid = Plan.objects.filter(djstripe_id=planid).last().product_id
    active_products = list(get_active_products_with_metadata())
    default_products = [p for p in active_products if p.metadata.is_default]
    default_product = default_products[0] if default_products else active_products[0]

    def _to_dict(product_with_metadata):
        # for now, just serialize the minimum amount of data needed for the front-end
        product_data = {}
        if PlanInterval.week in ACTIVE_PLAN_INTERVALS:
            product_data['weekly_plan'] = {
                'stripe_id': product_with_metadata.weekly_plan.id,
                'payment_amount': get_friendly_currency_amount(product_with_metadata.weekly_plan.amount,
                                                               product_with_metadata.weekly_plan.currency),
                'daily_amount': get_friendly_currency_amount(product_with_metadata.weekly_plan.amount / 7,
                                                               product_with_metadata.weekly_plan.currency),
                'interval': PlanInterval.week,  # set to day because we're dividing price by 12
            }
        if PlanInterval.day in ACTIVE_PLAN_INTERVALS:
            product_data['daily_plan'] = {
                'stripe_id': product_with_metadata.daily_plan.id,
                'payment_amount': get_friendly_currency_amount(product_with_metadata.daily_plan.amount,
                                                               product_with_metadata.daily_plan.currency),
                'daily_amount': get_friendly_currency_amount(product_with_metadata.daily_plan.amount,
                                                               product_with_metadata.daily_plan.currency),
                'interval': PlanInterval.day,
            }
        return product_data

    active_plan_intervals = []
    for plan_interval in get_active_plan_interval_metadata():
        if IntelGroups.objects.filter(id=groupid).last().isfree:
            active_plan_intervals.append(plan_interval)
        else:
            if Plan.objects.filter(djstripe_id=planid).last().interval == plan_interval.interval:
                active_plan_intervals.append(plan_interval)
    products = []
    for product in active_products:
        if product.metadata.name != Product.objects.filter(djstripe_id=productid).last().name:
            products.append(product)
    #     if Product.objects.filter(djstripe_id=productid).last().name == 'Free':
    #         if product.metadata.name != 'Gold':
    #             products.append(product)
    #     elif Product.objects.filter(djstripe_id=productid).last().name == 'Silver':
    #         if product.metadata.name == 'Gold':
    #             products.append(product)
    if Plan.objects.filter(djstripe_id=planid).last().interval == ACTIVE_PLAN_INTERVALS[0]:
        default_to_weekly = True
    else:
        default_to_weekly = False

    if IntelGroups.objects.filter(id=groupid).last().isfree:
        friendly_payment_amount = get_friendly_currency_amount(
            Plan.objects.filter(djstripe_id=planid).last().amount,
            Plan.objects.filter(djstripe_id=planid).last().currency
        )
    else:
        friendly_payment_amount = get_friendly_currency_amount(
            subscription_holder.active_stripe_subscription.plan.amount,
            subscription_holder.active_stripe_subscription.plan.currency,
        )

    return render(request, 'subscriptions/view_subscription.html', {
        'active_tab': 'subscription',
        'subscription': subscription_holder.active_stripe_subscription,
        'subscription_urls': _get_subscription_urls(subscription_holder),
        'friendly_payment_amount': friendly_payment_amount,
        'product': get_product_and_metadata_for_subscription(subscription_holder.active_stripe_subscription),
        'stripe_api_key': djstripe_settings.STRIPE_PUBLIC_KEY,
        'default_product': default_product,
        'active_products': products,
        'active_products_json': {str(p.stripe_id): _to_dict(p) for p in active_products},
        'active_plan_intervals': active_plan_intervals,
        'default_to_weekly': default_to_weekly,
        'payment_metadata': _get_payment_metadata_from_request(request),
        'current_product_id': Product.objects.filter(djstripe_id=productid).last().id,
        'current_product_name': Product.objects.filter(djstripe_id=productid).last().name,
        'current_period_end': current_period_end,
        'card_exist': card_exist,
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
        if PlanInterval.week in ACTIVE_PLAN_INTERVALS:
            product_data['weekly_plan'] = {
                'stripe_id': product_with_metadata.weekly_plan.id,
                'payment_amount': get_friendly_currency_amount(product_with_metadata.weekly_plan.amount,
                                                               product_with_metadata.weekly_plan.currency),
                'daily_amount': get_friendly_currency_amount(product_with_metadata.weekly_plan.amount / 7,
                                                               product_with_metadata.weekly_plan.currency),
                'interval': PlanInterval.week,  # set to day because we're dividing price by 12
            }
        if PlanInterval.day in ACTIVE_PLAN_INTERVALS:
            product_data['daily_plan'] = {
                'stripe_id': product_with_metadata.daily_plan.id,
                'payment_amount': get_friendly_currency_amount(product_with_metadata.daily_plan.amount,
                                                               product_with_metadata.daily_plan.currency),
                'daily_amount': get_friendly_currency_amount(product_with_metadata.daily_plan.amount,
                                                               product_with_metadata.daily_plan.currency),
                'interval': PlanInterval.day,
            }
        return product_data

    return render(request, 'subscriptions/upgrade_subscription.html', {
        'active_tab': 'subscription',
        'stripe_api_key': djstripe_settings.STRIPE_PUBLIC_KEY,
        'default_product': default_product,
        'active_products': active_products,
        'active_products_json': {str(p.stripe_id): _to_dict(p) for p in active_products},
        'active_plan_intervals': get_active_plan_interval_metadata(),
        'default_to_weekly': ACTIVE_PLAN_INTERVALS[0] == PlanInterval.week,
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
    
    plan_id = request_body['plan_id']
    if Plan.objects.filter(id=plan_id).last().amount == 0:
        IntelGroups.objects.filter(id=request_body['groupid']).update(isfree=True)
        return JsonResponse(data={'isFree': True})

    if IntelGroups.objects.filter(id=request_body['groupid']).last().isfree:
        IntelGroups.objects.filter(id=request_body['groupid']).update(isfree=False)

    payment_method = request_body['payment_method']
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


    # create card objects
    # This creates a new Card in stripe and attaches the default PaymentMethod in one API call.
    card = stripe.Customer.create_source(customer.id,source=request_body['stripeToken'])
    
    # create the local card object in the DB so the subscription can use it
    djstripe.models.Card.sync_from_stripe_data(card)

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
    productid = Plan.objects.filter(djstripe_id=sub_id.plan_id).last().product_id
    if Product.objects.filter(djstripe_id=productid).last().name.strip() == 'Free':
        IntelGroups.objects.filter(id=request_body['groupid']).update(ispublic=True)
    else:
        if Product.objects.filter(djstripe_id=productid).last().metadata['group_public'] == 'True':
            IntelGroups.objects.filter(id=request_body['groupid']).update(ispublic=True)
        else:
            IntelGroups.objects.filter(id=request_body['groupid']).update(ispublic=False)
    IntelGroups.objects.filter(id=request_body['groupid']).update(plan_id=sub_id.djstripe_id)
    PlanHistory.objects.create(intelgroup_id=request_body['groupid'], sub_id=sub_id.djstripe_id, start=sub_id.current_period_start, end=sub_id.current_period_end)
    data = {
        'customer': customer,
        'subscription': subscription
    }
    return JsonResponse(
        data=data,
    )

@login_required
@require_POST
@catch_stripe_errors
@transaction.atomic
def update_customer(request, subscription_holder=None):
    subscription_holder = subscription_holder if subscription_holder else request.user
    request_body = json.loads(request.body.decode('utf-8'))
    user_id = int(request_body['user_id'])
    email = request_body['user_email']
    groupid = request_body['groupid']
    new_plan_id = request_body['plan_id']
    assert request.user.id == user_id
    assert request.user.email == email

    is_free = IntelGroups.objects.filter(id=groupid).last().isfree
    if Plan.objects.filter(id=new_plan_id).last().amount == 0:
        IntelGroups.objects.filter(id=groupid).update(isfree=True)
    else:
        IntelGroups.objects.filter(id=groupid).update(isfree=False)

    current_sub_id = IntelGroups.objects.filter(id=groupid).last().plan_id

    if current_sub_id != None:
        new_plan_id = request_body['plan_id']
        new_product_id = Plan.objects.filter(id=new_plan_id).last().product_id
        new_interval = Plan.objects.filter(id=new_plan_id).last().interval
        new_amount = Plan.objects.filter(id=new_plan_id).last().amount
        max_users = Product.objects.filter(djstripe_id=new_product_id).last().metadata['max_users']
        max_feeds = Product.objects.filter(djstripe_id=new_product_id).last().metadata['max_feeds']
        new_product_name = Product.objects.filter(djstripe_id=new_product_id).last().name
        current_plan_id = Subscription.objects.filter(djstripe_id=current_sub_id).last().plan_id
        current_product_id = Plan.objects.filter(djstripe_id=current_plan_id).last().product_id
        current_period_end = Subscription.objects.filter(djstripe_id=current_sub_id).last().current_period_end
        current_period_start = Subscription.objects.filter(djstripe_id=current_sub_id).last().current_period_start
        current_interval = Plan.objects.filter(djstripe_id=current_plan_id).last().interval
        current_product_name = Product.objects.filter(djstripe_id=current_product_id).last().name
        if is_free:
            current_amount = 0
        else:
            current_amount = Plan.objects.filter(djstripe_id=current_plan_id).last().amount

        if (current_product_name == 'Gold' and new_product_name == 'Silver') or new_product_name == 'Free':
            current_users = UserIntelGroupRoles.objects.filter(intelgroup_id=groupid).all()
            current_feeds = GroupFeeds.objects.filter(intelgroup_id=groupid).all()
            if len(current_users) > int(max_users) and len(current_feeds) > int(max_feeds):
                result = {
                    'users': len(current_users)-int(max_users),
                    'feeds': len(current_feeds)-int(max_feeds)
                }
                return JsonResponse(
                    data=result,
                )
            elif len(current_users) > int(max_users):
                result = {
                    'users': len(current_users)-int(max_users),
                }
                return JsonResponse(
                    data=result,
                )
            elif len(current_feeds) > int(max_feeds):
                result = {
                    'feeds': len(current_feeds)-int(max_feeds)
                }
                return JsonResponse(
                    data=result,
                )
            if Plan.objects.filter(id=new_plan_id).last().amount != 0:
                stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
                new_subscription = stripe.Subscription.modify(
                    Subscription.objects.filter(djstripe_id=current_sub_id).last().id,
                    plan = Plan.objects.filter(id=new_plan_id).last().id
                )
                djstripe.models.Subscription.sync_from_stripe_data(new_subscription)
        else:
            if current_amount != 0:
                delta_time = current_period_end.date()-datetime.now().date()
                addition_amount = decimal.Decimal(delta_time/(current_period_end.date()-current_period_start.date()))*(new_amount-current_amount)
                name = 'Addition Payment'
                stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
                customer = djstripe.models.Customer.objects.filter(djstripe_id=Subscription.objects.filter(djstripe_id=current_sub_id).last().customer_id).last().id
                charge = stripe.Charge.create(
                    amount=int(addition_amount)*100,
                    currency="usd",
                    description=name,
                    customer=customer,
                    receipt_email=request.user.email,
                )
                payment = Payment.objects.create(
                    charge_id=charge.id,
                    amount=int(charge.amount),
                    name=name,
                    user=request.user,
                )
            stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
            new_subscription = stripe.Subscription.modify(
                Subscription.objects.filter(djstripe_id=current_sub_id).last().id,
                plan = Plan.objects.filter(id=new_plan_id).last().id
            )
            djstripe.models.Subscription.sync_from_stripe_data(new_subscription)

    else:
        return JsonResponse(
            data = {'isFree':True, 'isSuccess':True}
        )

    return JsonResponse(
        data = {'isFree':False, 'isSccess':True}
    )

def _get_subscription_urls(subscription_holder):
    # get URLs for subscription helpers
    url_bases = [
        'subscription_details',
        'create_customer',
        'update_customer',
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



