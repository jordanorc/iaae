from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import nltk as py_nltk
import os

class Command(BaseCommand):
    args = 'command'
    help = ''

    def handle(self, *args, **options):
        if hasattr(settings, 'NLTK_DATAPATH'):
            NLTK_DATAPATH = settings.NLTK_DATAPATH
        else:
            NLTK_DATAPATH = os.path.join(os.path.dirname(py_nltk.__file__), "data")
        required_packages = ['punkt', 'floresta', 'mac_morpho', 'stopwords', 'wordnet']
        installed = all(py_nltk.downloader._downloader.is_installed(package, download_dir=NLTK_DATAPATH) for package in required_packages)
        if not installed:
            py_nltk.download(required_packages, download_dir=NLTK_DATAPATH)

