from flask import Blueprint

category = Blueprint('category', __name__)

from app.store.category import views
