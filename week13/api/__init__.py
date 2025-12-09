from flask import Blueprint

api_bp = Blueprint('api', __name__)

from . import server  # Import the server module to register routes and functionality