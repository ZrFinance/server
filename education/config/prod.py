# coding:utf-8
'''
@summary: 全局常量设置
'''

import os

DBHOST = os.environ.get('DBHOST', '132.232.49.116')
DBPORT = os.environ.get('DBPORT', '9106')
DBNAME = os.environ.get('DBNAME', 'sso')
DBUSER = os.environ.get('DBUSER', 'root')
DBPASS = os.environ.get('DBPASS', '!@#tc123')

# ===============================================================================
# 数据库设置
# ===============================================================================
# 正式环境数据库设置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DBNAME,
        'USER': DBUSER,
        'PASSWORD': DBPASS,
        'HOST': DBHOST,
        'PORT': DBPORT,
    }
}
