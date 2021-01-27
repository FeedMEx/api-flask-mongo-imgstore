
from flask import request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_claims
from pymongo import MongoClient, DESCENDING

from bson.objectid import ObjectId
from datetime import datetime, timezone
from PIL import Image, UnidentifiedImageError
import re
import os

# Definiendo la conexion a MongoDB
MONGO_URI = 'mongodb://localhost'
client = MongoClient(MONGO_URI)
db = client['img_store']
collection = db['images']


@jwt_required
def insert_image():

    claims = get_jwt_claims() 
    user = claims['user'] #rescatando usuario del token

    name = request.form['name']   #obteniendo nombre de la imagen
    name = " ".join(name.split()) #quitando espacios duplicados

    nameImage = collection.find_one({'user': user, 'name': {'$regex': name, '$options': 'i'}})  

    if len(name) < 5 or len(name) > 20:
        return jsonify({'value': False, 'msg': 'El título de la imagen debe contener entre 5 a 20 carácteres'})
    
    elif re.match("^[a-zA-Z0-9 ,-]+$", name) is None:
        return jsonify({'value': False, 'msg': 'Unicos caracteres especiales permitidos: , y -'})

    elif nameImage and nameImage['name'].lower() == name.lower():
        return jsonify({'value': False, 'msg': 'El título de la imagen ya existe, intente con otro'})
    
    image = request.files['image'] #obteniendo imagen

    try:
        image = Image.open(image)
    except UnidentifiedImageError:
        return jsonify({'msg': 'Error de formato'}), 415
    except: 
        return jsonify({'msg': 'Error desconocido'}), 415
    
    if len(image.fp.read()) > 256000:
        return jsonify({'value': False, 'msg': 'No esta permitido subir imagenes mayores al limite de 256 KB'})
    
    ext = image.format.lower() # extension de la imagen

    
    # Guardando imagen la ruta de img
    image.save(os.path.join(os.getcwd(),'app','app_images','img',user,'{}.{}'.format(name,ext)))

    collection.insert_one({
        'name': name,
        'extension': ext,
        'user': user,
        'date_created': datetime.now(timezone.utc),
        'date_updated': datetime.now(timezone.utc)
    })
    
    return jsonify({'value': True, 'msg': 'Imagen subida exitosamente'})
    

def get_images():

    images = []

    for doc in collection.find().sort('date_created', DESCENDING):
        images.append({
            '_id' : str(ObjectId(doc['_id'])),
            'name': doc['name'],
            'path': os.path.join('/img',doc['user'],doc['name']+'.'+doc['extension']),
            'user': doc['user'],
            'date': doc['date_created']
        })
    
    return jsonify(images)


@jwt_required
def get_my_images():

    claims = get_jwt_claims()
    images = []

    for doc in collection.find({'user': claims['user']}).sort('date_created', DESCENDING):
        images.append({
            '_id' : str(ObjectId(doc['_id'])),
            'name': doc['name'],
            'path': os.path.join('/img',doc['user'],doc['name']+'.'+doc['extension'])
        })
    
    return jsonify(images)


@jwt_required
def get_image(id):
    
    images = []

    user = 'user'
    name = 'name'
    for doc in collection.find({'user': user, 'name': name}):
        images.append({
            '_id' : str(ObjectId(doc['_id'])),
            'name': doc['name'],
            'path': '/img/'+doc['name']+'.'+doc['extension']
        })
    return jsonify(images)


def search_images(string):

    images = []
    search = re.compile('.*{}.*'.format(string), re.IGNORECASE)

    for doc in collection.find({'name': search}).sort('date_created', DESCENDING):
        images.append({
            '_id' : str(ObjectId(doc['_id'])),
            'name': doc['name'],
            'path': os.path.join('/img',doc['user'],doc['name']+'.'+doc['extension']),
            'user': doc['user'],
            'date': doc['date_created']
        })
    
    return jsonify(images)


@jwt_required
def search_my_images(string):

    claims = get_jwt_claims()
    images = []
    search = re.compile('.*{}.*'.format(string), re.IGNORECASE)

    for doc in collection.find({'user': claims['user'],'name': search}).sort('date_created', DESCENDING):
        images.append({
            '_id' : str(ObjectId(doc['_id'])),
            'name': doc['name'],
            'path': os.path.join('/img',doc['user'],doc['name']+'.'+doc['extension'])
        })
    
    return jsonify(images)


@jwt_required
def update_image(id):

    claims = get_jwt_claims()
    user = claims['user'] # rescatando usuario del token

    new_name = request.json['name'] #obteniendo nombre nuevo para la imagen
    new_name = " ".join(new_name.split()) #quitando espacios duplicados

    nameImage = collection.find_one({'user': user, 'name': new_name})

    if len(new_name) < 5 or len(new_name) > 20:
        return jsonify({'value': False, 'msg': 'El título de la imagen debe contener entre 5 a 20 carácteres'})
  
    elif nameImage:
        return jsonify({'value': False, 'msg': 'El título de la imagen ya existe, intente con otro'})
    
    elif re.match("^[a-zA-Z0-9 ,-]+$", new_name) is None:
        return jsonify({'value': False, 'msg': 'Unicos caracteres especiales permitidos: , y -'})

    doc = collection.find_one({'user': user, '_id': ObjectId(id)})

    username, name, extension = doc['user'], doc['name'], doc['extension']

    file = os.path.join(os.getcwd(),'app','app_images','img',username,name+'.'+extension)

    new_name_file = os.path.join(os.getcwd(),'app','app_images','img',username,new_name+'.'+extension)

    os.rename(file, new_name_file)

    collection.update_one({'user': user,'_id': ObjectId(id)
    },{
        '$set': {
            'name': new_name,
        }
    })
    return jsonify({'value': True,'message': 'El nombre de la imagen ha sido actualizada satisfactoriamente'})


@jwt_required
def delete_image(id):
    
    claims = get_jwt_claims()
    user = claims['user'] # rescatando usuario del token

    path = 'tlfsdwh891sdsd23383txbkptmwt49rzmmoag404upvqh72' #path inicial, para evitar coincidencias

    doc = collection.find_one({'user': user, '_id': ObjectId(id)})

    username, name, extension = doc['user'], doc['name'], doc['extension']
    
    file= os.path.join(os.getcwd(),'app','app_images','img',username,name+'.'+extension)

    try:
        os.remove(file)
    except FileNotFoundError:
        return jsonify({'message': 'Error en el id de la imagen'}), 400

    collection.delete_one({'user': user, '_id': ObjectId(id)})

    return jsonify({'message': 'Imagen eliminada satisfactoriamente'})


