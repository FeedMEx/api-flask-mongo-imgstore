from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from .settings import Settings
from .app_images.routes import images
from .app_users.routes import users


def create_app():
    
    app = Flask(__name__)

    CORS(app)

    jwt = JWTManager(app)

    # settings
    app.config.from_object(Settings(jwt))

    # Aplicaciones 
    app.register_blueprint(images)
    app.register_blueprint(users)

    return app