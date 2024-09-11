from flask import Flask, send_file, make_response
from funcoes.getEstabelecimentos import *
from funcoes.getReviews import *
import pandas as pd
from io import BytesIO
import base64

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
def getReviews(place_id):
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
   try: 
    
    reviews = handleGetReviews(place_id)

    if not (isinstance(reviews, str)):
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df = pd.DataFrame(reviews)
            df.to_excel(writer, sheet_name='Sheet_name_1', index=False)

        output.seek(0)
        excel_base64 = base64.b64encode(output.read()).decode('utf-8')

        response = {
            'hasError': False,
            'message': 'Arquivo gerado com sucesso',
            'arquivo': excel_base64
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
    app.run(debug=True)
