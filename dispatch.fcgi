#!/usr/bin/python
import os, site, sys

# virtualenv bug
os.environ['PATH'] = os.path.dirname(__file__)

# active virtualenv
venv = os.path.join(os.path.dirname(__file__), 'env/bin/activate_this.py')
execfile(venv, dict(__file__=venv))

# default path
path = os.path.dirname(__file__)

os.environ['DJANGO_SETTINGS_MODULE'] = 'nlp.settings'

if path not in sys.path:
    sys.path.append(path)

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")
