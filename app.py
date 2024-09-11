from flask import Flask, jsonify, request
from funcoes.getEstabelecimentos import *
from funcoes.getReviews import *

app = Flask(__name__)

@app.route('/GetEstabelecimentos/<nome>', methods=['GET'])
def getEstabelecimentos(nome):
   
   try:
    estabelecimentos, next_page = handleGetEstabelecimentos(nome)
    if not (isinstance(estabelecimentos, str)):
        return {
                'establishments': estabelecimentos,
                'next_page_token': next_page,
                'hasError': False,
                'message': 'Sucesso'
            }
    else:
        return {
            'establishments': [],
            'next_page_token': '',
            'hasError': True,
            'message': estabelecimentos
        }, 500 
   except Exception as e:
        return {
            'establishments': [],
            'next_page_token': '',
            'hasError': True,
            'message': str(e)
        }, 500 


@app.route('/GetReviews/<place_id>', methods=['GET'])
def getReview(place_id):
   try: 
    
    reviews = handleGetReviews(place_id)

    if not (isinstance(reviews, str)):
        return {
        'quantity': len(reviews),
        'reviews': reviews,
        'hasError': False,
        'message': 'Sucesso'
    }
    else:
       return {
            'quantity': 0,
            'reviews': [],
            'hasError': True,
            'message': reviews
    }, 500 
   except Exception as e:
    return {
            'quantity': 0,
            'reviews': [],
            'hasError': True,
            'message': str(e)
    }, 500  
    
if __name__ == '__main__':
    app.run(debug=True)
