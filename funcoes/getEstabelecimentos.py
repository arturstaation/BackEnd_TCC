import requests
from dotenv import load_dotenv
import os
from pathlib import Path

dotenv_path = Path('./variaveis.env')
load_dotenv(dotenv_path=dotenv_path)

# Acessa a variável de ambiente
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

# Verifica se a variável foi carregada corretamente
if not GOOGLE_PLACES_API_KEY:
    raise ValueError("A chave de API 'GOOGLE_PLACES_API_KEY' não foi encontrada nas variáveis de ambiente.")



def getEstabelecimentos(nome):

    try:
        # Localização e parâmetros de busca
        location = 'em São Paulo, Brasil'  # Localização fixa em São Paulo
        print(GOOGLE_PLACES_API_KEY)
        
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
        
        '''
        if 'next_page_token' in result:
            print("Proxima Pagina: " + result['next_page_token'])
            params['page_token'] = result['next_page_token']
            time.sleep(2)  # Aguarde antes de buscar a próxima página
        else:
            break  # Sai do loop se não houver mais páginas de resultados
        ###
        '''
        next_token = ""
        if('next_page_token' in  result):
            next_token = result['next_page_token']


        return all_results, next_token
    except:
        raise Exception("Erro ao Processar")