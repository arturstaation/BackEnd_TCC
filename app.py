from flask import Flask, jsonify, request
from funcoes.getEstabelecimentos import *

app = Flask(__name__)

@app.route('/GetEstabelecimentos/<nome>', methods=['GET'])
def RequestGetEstabelecimentos(nome):
   estabelecimentos, next_page = getEstabelecimentos(nome)
   
   return {
       'establishments': estabelecimentos,
       'next_page_token': next_page
   }
    
if __name__ == '__main__':
    app.run(debug=True)
