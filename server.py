# importando flask para criação da api
from flask import Flask, json, jsonify, request
import pymongo

from flask_pymongo import PyMongo

from bson.json_util import dumps

from bson.objectid import ObjectId

from werkzeug.security import generate_password_hash, check_password_hash


# importando data de connection
from connection import companies

# Criando uma instância do flask
app = Flask(__name__)
app.secret_key = "secretKey"
app.config['MONGO_URI'] = "mongodb+srv://admin:3571592486@cluster0.ebc1x.mongodb.net/Users?retryWrites=true&w=majority"

mongo = PyMongo(app)
app.static_folder = '.'
# Criando rota estática para index.html


@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')

# Criando rota para adicionar usuário.
@app.route('/add', methods=['POST'])
def set_users():
    _json = request.json
    _name = _json['name']
    _email = _json['email']
    _password = _json['password']
    if _name and _email and _password and request.method == 'POST':
      _hashed_password = generate_password_hash(_password)

      id = mongo.db.user.insert_one({'name': _name, 'email': _email, 'pwd': _hashed_password})

      resp=jsonify("Usuário adicionado com sucesso!")

      resp.status_code = 200

      return resp

    else:
      return not_found()

#rota de erro 404
@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': "Not found"+request.url
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp

    print(request.args)
    return json.dumps(companies)

# Criando rota para buscar todos os usuários cadastrados.
@app.route('/users', methods=['GET'])
def get_users():
    users=mongo.db.user.find()
    resp=dumps(users)
    return resp

#Rota para buscar usuário pelo id.
@app.route('/user/<id>')
def user(id):
    user=mongo.db.user.find_one({'_id':ObjectId(id)})
    resp=dumps(user)
    return resp

#Rota para deletar usuário pelo id.
@app.route('/delete/<id>',methods=['DELETE'])
def delete_user(id):
    mongo.db.user.delete_one({'_id':ObjectId(id)})
    resp=jsonify("Usuário removido com sucesso.")
    resp.status_code=200
    return resp

#Rota para alterar usuário pelo id.
@app.route('/user/<id>',methods=['PUT'])
def update_user(id):
    _id=id
    _json=request.json
    _name=_json['name']
    _email=_json['email']
    _password=_json['password']
    if _name and _email and _password and request.method=='PUT':
        _hashed_password=generate_password_hash(_password)

        mongo.db.user.update_one({'_id':ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)},{'$set':{'name':_name,'email':_email,'pwd':_hashed_password}})
        resp=jsonify("Usuário atualizado com sucesso.")
        resp.status_code=200
        return resp
    else:
        return not_found()





if __name__ == '__main__':
    # Definindo host e porta para instância do flask
    app.run(host='0.0.0.0', port=8080, debug=True)
    # Rodando o server
