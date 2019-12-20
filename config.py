import os
import re
import sys

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from raygun4py.middleware import flask as flask_raygun

PYTHON_VERSION = sys.version_info[0]
if PYTHON_VERSION == 3:
    import urllib.parse
else:
    import urlparse

basedir = os.path.abspath(os.path.dirname(__file__))

if os.path.exists('.env'):
    print('Importing environment from .env file')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1].replace("\"", "")


class Config:
    APP_NAME = os.environ.get('APP_NAME') or 'Flask-Base'

    if os.environ.get('SECRET_KEY'):
        SECRET_KEY = os.environ.get('SECRET_KEY')
    else:
        SECRET_KEY = 'SECRET_KEY_ENV_VAR_NOT_SET'
        print('SECRET KEY ENV VAR NOT SET! SHOULD NOT SEE IN PRODUCTION')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.sendgrid.net'
    MAIL_PORT = os.environ.get('MAIL_PORT') or 587
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') or False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # administrators emails for logging / error handling
    admin_list_email = re.sub(r"\s+", "", os.environ.get('ADMINS'),
                              flags=re.UNICODE)  # remove all space if that containing on ADMINS environ variable
    admin_list_email = [i.split(" ") for i in
                        admin_list_email.split(",")]  # store the ADMINS environ variable to a list
    ADMINS = []
    for list_emails in admin_list_email:
        for admin_email in list_emails:
            ADMINS.append(admin_email)

    # Heroku log to stdout
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')

    # Analytics
    GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID') or ''
    SEGMENT_API_KEY = os.environ.get('SEGMENT_API_KEY') or ''

    # Admin account
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'password'
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'aqurpyk@gmail.com'
    EMAIL_SUBJECT_PREFIX = '[{}]'.format(APP_NAME)
    EMAIL_SENDER = '{app_name} Admin <{email}>'.format(
        app_name=APP_NAME, email=MAIL_USERNAME)

    REDIS_URL = os.getenv('REDISTOGO_URL') or 'http://localhost:6379'

    RAYGUN_APIKEY = os.environ.get('RAYGUN_APIKEY')

    # Parse the REDIS_URL to set RQ config variables
    if PYTHON_VERSION == 3:
        urllib.parse.uses_netloc.append('redis')
        url = urllib.parse.urlparse(REDIS_URL)
    else:
        urlparse.uses_netloc.append('redis')
        url = urlparse.urlparse(REDIS_URL)

    RQ_DEFAULT_HOST = url.hostname
    RQ_DEFAULT_PORT = url.port
    RQ_DEFAULT_PASSWORD = url.password
    RQ_DEFAULT_DB = 0

    @staticmethod
    def init_app(app):
        pass

    # Flask-upload
    UPLOADED_PHOTOS_DEST = basedir + '/app/static/images/app/'
    UPLOADED_PHOTOS_ALLOW = ('jpg', 'jpeg', 'png')

    try:
        os.makedirs(UPLOADED_PHOTOS_DEST)
    except FileExistsError:
        # directory already exists
        pass

    LANGUAGES = ['en', 'id']

    # Flask-apscheduler
    JOBS = [
        {
            'id': 'job2',
            'func': 'app.scheduler_task:backup_db_to_google_drive',
            'replace_existing': True,
            'trigger': 'cron',
            'misfire_grace_time': 600,
            'hour': 2,  # every day at 02:05
            'minute': 5,
        }
    ]
    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url='sqlite:///flask_context.db')
    }
    SCHEDULER_API_ENABLED = True

    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 10
    }

    SCHEDULER_EXECUTORS = {
        'default': {'type': 'threadpool', 'max_workers': 8}
    }


class DevelopmentConfig(Config):
    DEBUG = True
    ASSETS_DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

    @classmethod
    def init_app(cls, app):
        print('THIS APP IS IN DEBUG MODE. \
                YOU SHOULD NOT SEE THIS IN PRODUCTION.')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    WTF_CSRF_ENABLED = False

    @classmethod
    def init_app(cls, app):
        print('THIS APP IS IN TESTING MODE.  \
                YOU SHOULD NOT SEE THIS IN PRODUCTION.')


class ProductionConfig(Config):
    DEBUG = False
    USE_RELOADER = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SSL_DISABLE = (os.environ.get('SSL_DISABLE') or 'True') == 'True'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        assert os.environ.get('SECRET_KEY'), 'SECRET_KEY IS NOT SET!'

        flask_raygun.Provider(app, app.config['RAYGUN_APIKEY']).attach()


class HerokuConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # Handle proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # Log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
    'heroku': HerokuConfig,
    'unix': UnixConfig
}
