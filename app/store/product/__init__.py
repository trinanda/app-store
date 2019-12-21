from flask import Blueprint

product = Blueprint('product', __name__)

from app.store.product import views
