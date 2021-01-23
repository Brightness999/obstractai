from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from djstripe.models import Product

from apps.subscriptions.metadata import ProductMetadata, ACTIVE_PRODUCTS

class Command(BaseCommand):
    help = 'Bootstraps your Stripe subscriptions'

    def handle(self, **options):
        print('Syncing products and plans from Stripe')
        call_command('djstripe_sync_plans_from_stripe')
        print('Done! Creating default product configuration')
        _create_default_product_config()

def _create_default_product_config():
    # make the first product the default
    default = True
    product_metas = []
    for product in Product.objects.all():
        # print(product.metadata)
        product_meta = ProductMetadata.from_stripe_product(
            product,
            description=f'The {product.name} plan',
            is_default=default,
            features=[
                {'label':'Max feeds:', 'value':product.metadata['max_feeds']},
                {'label':'Max users:', 'value':product.metadata['max_users']},
                {'label':'Custom feeds:', 'value':product.metadata['custom_feeds']},
                {'label':'Custom observables:', 'value':product.metadata['custom_observables']},
                {'label':'API access:', 'value':product.metadata['api_access']},
            ]
        )
        default = False
        product_metas.append(product_meta)
    print('Copy/paste the following code into your `apps/subscriptions/metadata.py` file:\n\n')
    newline = '\n'
    print(f'ACTIVE_PRODUCTS = [{newline}    {f",{newline}    ".join(str(meta) for meta in product_metas)},{newline}]')



