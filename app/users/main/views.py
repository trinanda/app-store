from flask import Blueprint, render_template, url_for, flash
from werkzeug.utils import redirect
from flask_babel import _


main = Blueprint('main', __name__)


@main.route('/')
@main.route('/index')
def index():
    return 'hello there'
