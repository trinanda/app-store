from flask import Blueprint

category = Blueprint('category', __name__)

from app.users.main.category import views
