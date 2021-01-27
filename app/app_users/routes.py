
from flask import Blueprint
from . import controllers


users = Blueprint('users', __name__)

# Rutas para la app de gestion de usuarios

users.add_url_rule('/users',view_func = controllers.create_user, methods=['POST'])

users.add_url_rule('/user',view_func = controllers.authenticate, methods=['POST'])

users.add_url_rule('/users', view_func = controllers.logout, methods=['DELETE'])

