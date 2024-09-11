from flask import Flask, jsonify, request
from funcoes.getEstabelecimentos import *
from funcoes.getReviews import *

app = Flask(__name__)

@app.route('/GetEstabelecimentos/<nome>', methods=['GET'])
def getEstabelecimentos(nome):
   
   try:
    estabelecimentos, next_page = handleGetEstabelecimentos(nome)
    
    return jsonify({
            'establishments': estabelecimentos,
            'next_page_token': next_page,
            'hasError': False,
        })
   except Exception as e:
        return jsonify({
            'hasError': True,
            'message': str(e)
        }), 500 


@app.route('/GetReviews/<place_id>', methods=['GET'])
def getReview(place_id):
   try: 
    reviews = handleGetReviews(place_id)
    return jsonify({
            'quantity': len(reviews),
            'reviews': reviews,
            'hasError': False,
    })
   except Exception as e:
    return jsonify({
            'hasError': True,
            'message': str(e)
    }), 500  
    
if __name__ == '__main__':
    app.run(debug=True)
