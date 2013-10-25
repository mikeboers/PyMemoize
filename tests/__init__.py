import os

from memoize.time import start_time_travel

from .common import *

if not os.environ.get('NO_TIME_TRAVEL'):
    start_time_travel()
