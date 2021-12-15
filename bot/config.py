import os
import sys

import django


TOKEN = '2114834889:AAE7r8doYByrTCOkNxu_ALKw2qsw85i2p9g'
BOT_USERNAME = 'cpython_telegram_test_bot'

PARENT_PACKAGE = '..'
APP_PACKAGE = 'app'
PARENT_DIR = os.path.dirname(os.path.dirname(__file__))
APP_DIR = os.path.join(PARENT_DIR, APP_PACKAGE)

sys.path.append(APP_DIR)
sys.path.append(PARENT_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
