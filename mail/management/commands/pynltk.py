from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import nltk as py_nltk
import os

class Command(BaseCommand):
    args = 'command'
    help = ''

    option_list = BaseCommand.option_list + (
        make_option('--download',
            action='store_true',
            dest='download',
            default=False,
            help='Download NLTK data'),
        )

    def handle(self, *args, **options):
        # ...
        if options['download']:
            if hasattr(settings, 'NLTK_DATAPATH'):
                NLTK_DATAPATH = settings.NLTK_DATAPATH
            else:
                NLTK_DATAPATH = os.path.join(os.path.dirname(py_nltk.__file__), "data")
            py_nltk.download(['punkt', 'floresta', 'mac_morpho'], download_dir=NLTK_DATAPATH)
