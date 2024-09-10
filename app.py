from flask import Flask, jsonify, request
from funcoes.getEstabelecimentos import *

app = Flask(__name__)

# Rota de exemplo
@app.route('/')
def home():
    return jsonify(message="Bem-vindo à minha API!")

@app.route('/GetEstabelecimentos/<nome>', methods=['GET'])
def RequestGetEstabelecimentos(nome):
   print(nome)
   resposta = getEstabelecimentos(nome)
   return resposta
    
if __name__ == '__main__':
    app.run(debug=True)
