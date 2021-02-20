from flask import request
from dotenv import load_dotenv
import os

class Settings:
    
    load_dotenv() # Inicializando las variables de entorno

    # Configuraciones del servidor

    PORT = os.getenv('PORT')

    DEBUG = False

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') # Valor almacenado en una variable de entorno

    JWT_BLACKLIST_ENABLED = True

    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

    CORS_HEADERS = 'Content-Type'

    ALLOWED_EXTENSIONS = ["JPEG", "JPG", "PNG", "GIF"]


    # Configuraciones de Json Web Token

    def __init__(self,jwt):
        
        blacklist = set()
        
        # Agregar el username a los tokens
        @jwt.user_claims_loader
        def add_claims_to_access_token(identity):
            username = request.json['username']
            return {
                'user': username.strip(),
            }

        # verificar si el token esta en el blacklist
        @jwt.token_in_blacklist_loader
        def check_if_token_in_blacklist(decrypted_token):
            jti = decrypted_token['jti']
            return jti in blacklist

        