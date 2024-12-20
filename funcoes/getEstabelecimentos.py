import requests
from variaveis import GOOGLE_PLACES_API_KEY
from funcoes.logMessage import *

def handleGetEstabelecimentos(nome):

    try:
       
        location = 'em São Paulo, Brasil' 
        
        params = {
            'query': nome + location,
            #'radius': location,
            'type': 'restaurant',
            'key': GOOGLE_PLACES_API_KEY,


        }

        all_results = []

       
        url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
        response = requests.get(url, params=params)
        result = response.json()
        if 'results' in result and not('error_message') in result:

            
            for results in result['results']:
                place_info = {
                    "name": results.get("name"),
                    "formatted_address": results.get("formatted_address"),
                    "place_id": results.get("place_id"),
                    "reviews": results.get("user_ratings_total"),  
                    "rating": results.get("rating")
                }
                
                all_results.append(place_info)
                
        else:
            error_message = f"Erro ao Obter Estabelecimentos {nome}.Erro: {result}"
            log(error_message)
            return ("Erro ao Obter Estabelecimentos."),""
        next_token = ""
        if('next_page_token' in  result):
            next_token = result['next_page_token']


        return all_results, next_token

    except Exception as e:

        error_message = f"Erro ao Obter Estabelecimentos {nome}. Erro: {str(e)}"
        log(error_message)
        return ("Erro ao Obter Estabelecimentos"),""