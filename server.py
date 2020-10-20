# importando flask para criação da api
from flask import Flask, json, jsonify, request
import pymongo
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import hmac
import hashlib
import base64
import json 
import datetime


secret_key = '52d3f853c19f8b63c0918c126422aa2d99b1aef33ec63d41dea4fadf19406e54'
#criando função para criação do token jwt
def create_jwt(payload):
    payload = json.dumps(payload).encode()
    header = json.dumps({
        'typ': 'JWT',
        'alg': 'HS256'
    }).encode()
    b64_header = base64.urlsafe_b64encode(header).decode()
    b64_payload = base64.urlsafe_b64encode(payload).decode()
    signature = hmac.new(
        key=secret_key.encode(),
        msg=f'{b64_header}.{b64_payload}'.encode(),
        digestmod=hashlib.sha256
    ).digest()
    jwt = f'{b64_header}.{b64_payload}.{base64.urlsafe_b64encode(signature).decode()}'
    return jwt
#função de verificação do token jwt, expiração e validade.
def verify_and_decode_jwt(jwt):
    b64_header, b64_payload, b64_signature = jwt.split('.')
    b64_signature_checker = base64.urlsafe_b64encode(
        hmac.new(
            key=secret_key.encode(),
            msg=f'{b64_header}.{b64_payload}'.encode(),
            digestmod=hashlib.sha256
        ).digest()
    ).decode()
    # payload extraido antes para checar o campo 'exp'
    payload = json.loads(base64.urlsafe_b64decode(b64_payload))
    unix_time_now = datetime.datetime.now().timestamp()
    if payload.get('exp') and payload['exp'] < unix_time_now:
        return jsonify('Token expirado')
    
    if b64_signature_checker != b64_signature:
        return jsonify('Assinatura inválida')       
    
    return payload    


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
@app.route('/user/<id>',methods=['DELETE'])
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

#Rota de signin da api, validando user e retornando token
@app.route('/signin',methods=['POST'])
def signin():
    _json = request.json    
    _email = _json['email']
    _password = _json['password']
    if _email and _password and request.method == 'POST':
      id=mongo.db.user.find_one({"email":_email})
      if id:

         check=check_password_hash(id["pwd"] , _password )   
      else:
          return jsonify("Usuario não cadastrado.")
    
      if check:
        payload = {    
        'userId':str(ObjectId(id['_id'])),
        'name':str(id['name']),
        'email':id['email'],
        'exp': (datetime.datetime.now() + datetime.timedelta(minutes=1)).timestamp(),}
        jwt_created = create_jwt(payload)        
        resp={"token":jwt_created}     
        return resp
      else:
       return jsonify("Email/Password inválidos.")  

#rota para validação do token     
@app.route('/validate',methods=['POST'])
def validate():
    _json=request.json
    _token=_json['token']
    if _token and request.method=="POST":
        decoded_jwt = verify_and_decode_jwt(_token)
        if decoded_jwt:
            return decoded_jwt
        else:
            return not_found()


    


if __name__ == '__main__':
    # Definindo host e porta para instância do flask
    app.run(host='0.0.0.0', port=8080, debug=True)
    # Rodando o server
