# importando flask para criação da api
from flask import Flask, json ,request

# importando data de connection
from connection import companies

#Criando uma instância do flask
app = Flask(__name__)
app.static_folder='.'
# Criando rota estática para index.html
@app.route('/',methods=['GET'])
def index():
    return app.send_static_file('index.html')

#Criando rota get e retornando os dados.
@app.route('/companies', methods=['GET'])
def get_companies():
    print(request.args)
    return json.dumps(companies)  
  
#Criando rota post e recebendo os dados vindos do client e retornando resposta.
@app.route('/companies', methods=['POST'])
def post_companies():
    print(request.args)
    return json.dumps({"success": True}), 201


if __name__ == '__main__':
    #Definindo host e porta para instância do flask
    app.run(host='0.0.0.0', port=8080)
    #Rodando o server