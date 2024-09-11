import requests
from loadVariables import GOOGLE_PLACES_API_KEY
def handleGetEstabelecimentos(nome):

    try:
        # Localização e parâmetros de busca
        location = 'em São Paulo, Brasil'  # Localização fixa em São Paulo
        
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

        if 'results' in result:


            for results in result['results']:
                place_info = {
                    "name": results.get("name"),
                    "formatted_address": results.get("formatted_address"),
                    "place_id": results.get("place_id"),
                    "reviews": results.get("user_ratings_total"),  # Corrigido para user_ratings_total
                    "rating": results.get("rating")
                }
                
                all_results.append(place_info)
                

        # Verifica se há mais páginas de resultados disponíveis
        next_token = ""
        if('next_page_token' in  result):
            next_token = result['next_page_token']


        return all_results, next_token
    except Exception as e:
        raise Exception(f"Erro ao Obter Estabelecimentos. " + e)