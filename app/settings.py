from flask import request

class Settings:

    # Configuraciones del servidor

    PORT = '5000'

    ENV = 'development'

    DEBUG = True

    SECRET_KEY = 'my_secret_key' #cambiar una clave segura para producción

    JWT_SECRET_KEY = 'my_jwt_secret_key' #cambiar una clave segura para producción

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

        