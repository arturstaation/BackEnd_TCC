from flask import Flask
from funcoes.getEstabelecimentos import *
from funcoes.getReviews import *
import pandas as pd
from io import StringIO
import base64
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/GetEstabelecimentos/<nome>', methods=['GET'])
def getEstabelecimentos(nome):
   print(f"[GetEstabelecimentos]Request para estabelecimento: {nome}")
   
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
def getReviews(place_id):
   print(f"[GetReviews]Request Recebido para place_id: {place_id}")
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
   
@app.route('/GetReviewsExcel/<place_id>', methods=['GET'])
def getReviewsExcel(place_id):
   print(f"[GetReviewsExcel]Request Recebido para place_id: {place_id}")
   try: 
    
    reviews = handleGetReviews(place_id)
    if not (isinstance(reviews, str)):
        output = StringIO()
        
        df = pd.DataFrame(reviews)
        df.to_csv(output, index=False)
        
        output.seek(0)
        
        csv_base64 = base64.b64encode(output.getvalue().encode('utf-8')).decode('utf-8')
        
        response = {
            'hasError': False,
            'message': 'Arquivo CSV gerado com sucesso',
            'arquivo': csv_base64
        }
        
        return response
    else:
       return {
            'hasError': True,
            'message': reviews
    }, 500 

   except Exception as e:
    return {
            'hasError': True,
            'message': str(e)
    }, 500  
    
if __name__ == '__main__':
    app.run(debug=False)
