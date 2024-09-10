from flask import Flask, jsonify, request
from funcoes.getEstabelecimentos import *
from funcoes.getReviews import *

app = Flask(__name__)

@app.route('/GetEstabelecimentos/<nome>', methods=['GET'])
def RequestGetEstabelecimentos(nome):
   estabelecimentos, next_page = getEstabelecimentos(nome)
   
   return {
       'establishments': estabelecimentos,
       'next_page_token': next_page
   }


@app.route('/GetReviews/<place_id>', methods=['GET'])
def RequestGetReview(place_id):
   reviews = getReviews(place_id)
   
   return {
       'total': len(reviews),
       'reviews': reviews,
   }
    
if __name__ == '__main__':
    app.run(debug=True)
