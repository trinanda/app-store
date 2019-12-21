import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler

from flask import Flask, request, current_app
from flask_assets import Environment
from flask_compress import Compress
from flask_login import LoginManager
from flask_mail import Mail
from flask_rq import RQ
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import configure_uploads, UploadSet
from flask_wtf import CSRFProtect
from flask_babel import Babel
from werkzeug.contrib.fixers import ProxyFix

from app import cli
from app.assets import app_css, app_js, vendor_css, vendor_js
from config import Config as config_flask_upload
from config import config as Config

basedir = os.path.abspath(os.path.dirname(__file__))

mail = Mail()
db = SQLAlchemy()
csrf = CSRFProtect()
compress = Compress()
photos = UploadSet('photos', config_flask_upload.UPLOADED_PHOTOS_ALLOW)
babel = Babel()

# Set up Flask-Login
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'account.login'


def create_app(config):
    app = Flask(__name__)
    config_name = config

    # fix insecure content blocked
    app.wsgi_app = ProxyFix(app.wsgi_app)

    if not isinstance(config, str):
        config_name = os.getenv('FLASK_CONFIG', 'default')

    app.config.from_object(Config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # not using sqlalchemy event system, hence disabling it

    Config[config_name].init_app(app)
    register_extensions(app)

    # Register Jinja template functions
    from .utils import register_template_utils
    register_template_utils(app)

    # Set up asset pipeline
    assets_env = Environment(app)
    dirs = ['assets/styles', 'assets/scripts']
    for path in dirs:
        assets_env.append_path(os.path.join(basedir, path))
    assets_env.url_expire = True

    assets_env.register('app_css', app_css)
    assets_env.register('app_js', app_js)
    assets_env.register('vendor_css', vendor_css)
    assets_env.register('vendor_js', vendor_js)

    # Configure SSL if platform supports it
    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        SSLify(app)

    # Create app blueprints
    # from app.users.main import main as main_blueprint
    # app.register_blueprint(main_blueprint)

    from app.store.category import category as category_blueprint
    app.register_blueprint(category_blueprint, url_prefix='/category')

    from app.store.product import product as product_blueprint
    app.register_blueprint(product_blueprint, url_prefix='/product')

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'], toaddrs=app.config['ADMINS'],
                subject=os.environ.get('APP_NAME') + ' Failure', credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/' + os.environ.get('APP_NAME'), maxBytes=51200, backupCount=10)
            file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s '
                                                        '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info(os.environ.get('APP_NAME') + ' startup')

    return app


def register_extensions(app):
    # Set up extensions
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    compress.init_app(app)
    RQ(app)
    configure_uploads(app, photos)
    babel.init_app(app)
    cli.register(app)
    try:
        scheduler.init_app(app)
        scheduler.start()
    except Exception as e:
        pass


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


from app.scheduler_task import scheduler
