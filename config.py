#!/usr/bin/env python

import os

DEBUG = True

SECRET_KEY = os.urandom(24)

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@127.0.0.1:3306/web1'

SQLALCHEMY_TRACK_MODIFICATIONS = False