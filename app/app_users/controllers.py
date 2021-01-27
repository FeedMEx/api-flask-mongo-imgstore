
from flask import request, jsonify
from pymongo import MongoClient
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_raw_jwt, verify_jwt_in_request
from werkzeug.security import generate_password_hash, check_password_hash

import os
from datetime import timedelta
from .validators import validar_email
import re


# Definiendo la conexion a MongoDB
MONGO_URI = 'mongodb://localhost'
client = MongoClient(MONGO_URI)
db = client['image_store']
collection = db['users']

# definiendo una lista para almacenar tokens de cierre de sesión
blacklist = set()

def create_user():

    try:
        verify_jwt_in_request()
        return jsonify({'msg':'Error, ya esta logeado'}), 404
    except:
        pass

    # Obteniendo el nombre de usuario sin espacios al inicio y final
    username = request.json['username'].strip()
    email = request.json['email']
    password = request.json['password']
    confirm_pass = request.json['confirm_pass']

    
    user = collection.find_one({'username': {'$regex': username, '$options': 'i'}})

    verify_email = collection.find_one({'email': {'$regex': email, '$options': 'i'}})


    if len(username) < 5 or len(username) > 15:
        return jsonify({'value': False, 'msg': 'El username debe contener entre a 5 a 15 carácteres'})

    elif re.match("^[a-zA-Z0-9_-]+$", username) is None:
        return jsonify({'value': False, 'msg': 'Unicos caracteres especiales permitidos: _ y -'})
    
    elif user and user['username'].lower() == username.lower():
        return jsonify({'value': False, 'msg': 'Ya existe el nombre de usuario'})
    
    elif validar_email(email):
        return jsonify({'value': False, 'msg': 'Escriba una cuenta de email válida'})
    
    elif verify_email:
        return jsonify({'value': False, 'msg': 'El email ya esta siendo utilizado'})

    elif len(password) < 8:
        return jsonify({'value': False, 'msg': 'La contraseña debe contener al menos 8 carácteres'})

    elif password != confirm_pass:
        return jsonify({'value': False, 'msg': 'La contraseña de confirmación no coincide'})

    else:
        password_hash = generate_password_hash(password)

        id = collection.insert({
            'username': username,
            'email': email,
            'password': password_hash
        })

        os.mkdir(os.path.join(os.getcwd(),'app','app_images/img',username))

        expires = timedelta(days=30)
        access_token = create_access_token(identity = username, expires_delta = expires)
        return jsonify({'value': True, 'access_token': access_token}), 200


def authenticate():
    try:
        verify_jwt_in_request()
        return jsonify({'msg':'Error, ya esta logeado'}), 404
    except:
        pass
    
    #obteniendo el nombre de usuario sin espacios al inicio y final
    username = request.json['username'].strip() 
    password = request.json['password']

    user = collection.find_one({'username': username})

    try:
        check_password = check_password_hash(user['password'], password)
    except TypeError:
        return jsonify(access_token = None), 401

    if check_password: 
        expires = timedelta(days=30)
        access_token = create_access_token(identity = username, expires_delta = expires)
        return jsonify(access_token = access_token), 200

    else: return jsonify(access_token = None), 401


@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"msg": "Successfully logged out"}), 200

