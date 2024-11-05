from flask import Flask
from funcoes.getEstabelecimentos import *
from funcoes.getReviews import *
from funcoes.getCorrectRating import *
from funcoes.getDataAnalysis import *
import pandas as pd
from io import StringIO
import base64
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
error_message = "Um erro ocorreu durante o processamento, tente novamente"

@app.route('/GetEstabelecimentos/<nome>', methods=['GET'])
def getEstabelecimentos(nome):
   print(f"[GetEstabelecimentos]Request para estabelecimento: {nome}")
   
   try:
    estabelecimentos, next_page = handleGetEstabelecimentos(nome)
    if not (isinstance(estabelecimentos, str)):
        print(f"[GetEstabelecimentos]Request para estabelecimento: {nome} concluido com sucesso")
        return {
                'establishments': estabelecimentos,
                'next_page_token': next_page,
                'hasError': False,
                'message': 'Sucesso'
            }
    else:
        print(f"[GetEstabelecimentos]Request para estabelecimento: {nome} concluido com erro {estabelecimentos}")
        return {
            'establishments': [],
            'next_page_token': '',
            'hasError': True,
            'message': error_message
        }, 500 
    
   except Exception as e:
        print(f"[GetEstabelecimentos]Request para estabelecimento: {nome} concluido com erro {str(e)}")
        return {
            'establishments': [],
            'next_page_token': '',
            'hasError': True,
            'message': error_message
        }, 500 


@app.route('/GetReviews/<place_id>', methods=['GET'])
def getReviews(place_id):
   print(f"[GetReviews]Request Recebido para place_id: {place_id}")
   try: 
    
    reviews = handleGetReviews(place_id)

    if not (isinstance(reviews, str)):
        print(f"[GetReviews]Request para place_id: {place_id} concluido com sucesso")
        return {
        'quantity': len(reviews),
        'reviews': reviews,
        'hasError': False,
        'message': 'Sucesso'
    }

    else:
       print(f"[GetReviews]Request para place_id: {place_id} concluido com erro: {reviews}")
       return {
            'quantity': 0,
            'reviews': [],
            'hasError': True,
            'message': error_message
    }, 500 

   except Exception as e:
    print(f"[GetReviews]Request para place_id: {place_id} concluido com erro: {str(e)}")
    return {
            'quantity': 0,
            'reviews': [],
            'hasError': True,
            'message': error_message
    }, 500  
   
@app.route('/GetReviewsExcel/<place_id>', methods=['GET'])
def getReviewsExcel(place_id):
   print(f"[GetReviewsExcel]Request Recebido para place_id: {place_id}")
   try: 
    
    reviews = handleGetReviews(place_id)
    if not (isinstance(reviews, str)):
        print(f"[GetReviewsExcel]Convertendo reviews do place_id: {place_id} para base64")
        output = StringIO()
        
        df = pd.DataFrame(reviews)
        df.to_csv(output, index=False)
        
        output.seek(0)
        
        csv_base64 = base64.b64encode(output.getvalue().encode('utf-8')).decode('utf-8')
        print(f"[GetReviewsExcel]Request para place_id: {place_id} concluido com sucesso")
        response = {
            'hasError': False,
            'message': 'Arquivo CSV gerado com sucesso',
            'arquivo': csv_base64
        }
        
        return response
    else:
       print(f"[GetReviewsExcel]Request para place_id: {place_id} concluido com erro: {reviews}")
       return {
            'hasError': True,
            'message': error_message
    }, 500 

   except Exception as e:
    print(f"[GetReviewsExcel]Request para place_id: {place_id} concluido com erro: {str(e)}")
    return {
            'hasError': True,
            'message': error_message
    }, 500  
   
      
@app.route('/GetCorrectRating/<place_id>', methods=['GET'])
def getCorrectRating(place_id):
   print(f"[GetCorrectRating]Request Recebido para place_id: {place_id}")
   try: 
    
    reviews = handleGetReviews(place_id)
    if not (isinstance(reviews, str)):
        print(f"[GetCorrectRating]Mandando as reviews do place_id: {place_id} para avaliação da IA")
        
        result = handleGetCorrectRating(reviews, place_id)

        print(f"[GetCorrectRating]Request para place_id: {place_id} concluido com sucesso")
        response = {
            'hasError': False,
            'message': 'Novo Rating Obtido Com Sucesso!',
            'rating': result
        }
        
        return response
    else:
       print(f"[GetCorrectRating]Request para place_id: {place_id} concluido com erro: {reviews}")
       return {
            'hasError': True,
            'message': error_message
    }, 500 

   except Exception as e:
    print(f"[GetCorrectRating]Request para place_id: {place_id} concluido com erro: {str(e)}")
    return {
            'hasError': True,
            'message': error_message
    }, 500  
   
@app.route('/SaveModel/', methods=['POST'])
def saveModel():
   print(f"[SaveModel]Request Recebido para salvar o modelo")
   try: 
    
        handleSaveModel()
        
        print(f"[SaveModel]Modelo salvo com sucesso")
        response = {
            'hasError': False,
            'message': 'Modelo salvo com sucesso',
        }
        return response
        
        

   except Exception as e:
    print(f"[SaveModel]Modelo salvo com erro: {str(e)}")
    return {
            'hasError': True,
            'message': error_message
    }, 500 
   
@app.route('/GetDataAnalysis/', methods=['GET'])
def getDataAnalysis():
   print(f"[GetDataAnalysis]Request Recebido Coletar os Dados analisados")
   try: 
    
        total_reviews, total_fraude = handleDataAnalysis()
        
        print(f"[GetDataAnalysis]Dados obtidos com sucesso")
        response = {
            'hasError': False,
            'message': {
               'totalReviews': str(total_reviews),
               'totalFraude': str(total_fraude),
               'fraudesRelativas': str((total_fraude/total_reviews)*100)
            }
        }
        return response
        
        

   except Exception as e:
    print(f"[GetDataAnalysis]Dados obtidos com erro: {str(e)}")
    return {
            'hasError': True,
            'message': error_message
    }, 500 
    
if __name__ == '__main__':
    app.run(debug=False)
