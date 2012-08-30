import os

DEBUG = False
database = os.path.join(os.path.dirname(__file__), 'wafflecopter.db')
entropy_file = os.path.join(os.path.dirname(__file__), 'entropy.dat')

url_root = ''

try:
    from local_settings import *
except ImportError:
    pass
