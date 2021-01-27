
from flask import Blueprint
from . import controllers

images = Blueprint('images', __name__, static_folder='img')

# Rutas para la app de gestion de imagenes

images.add_url_rule('/images', view_func = controllers.get_images)

images.add_url_rule('/images/<string>', view_func = controllers.search_images)

images.add_url_rule('/images',view_func = controllers.insert_image, methods=['POST'])

images.add_url_rule('/images/<id>', view_func = controllers.update_image, methods=['PUT'])

images.add_url_rule('/images/<id>', view_func = controllers.delete_image, methods=['DELETE'])



images.add_url_rule('/my_images', view_func = controllers.get_my_images)

images.add_url_rule('/my_images/<string>', view_func = controllers.search_my_images)
