import requests
import googlemaps
import time
GOOGLE_PLACES_API_KEY = "AIzaSyCTKyWv9us_sTGbajYO1RL9iruc_BATQ7E"

# Configuração do Google Maps
gmaps = googlemaps.Client(key=GOOGLE_PLACES_API_KEY)

def getEstabelecimentos(nome):

    try:
        # Localização e parâmetros de busca
        location = 'São Paulo, Brasil'  # Localização fixa em São Paulo
        radius = 5000  # Raio de busca em metros (ajuste conforme necessário)
        
        params = {
            'input': nome,
            'inputtype': 'textquery',
            'fields': 'formatted_address,name,rating,opening_hours,geometry',
            'key': GOOGLE_PLACES_API_KEY
        }

        all_results = []

        while True:
            time.sleep(1)  # Pausa para evitar limites de taxa da API
            # Faz a solicitação inicial
            url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'
            response = requests.get(url, params=params)
            result = response.json()

            print("Resultado")
            print(result)

            if 'results' in result:
                all_results.extend(result['results'])

            # Verifica se há mais páginas de resultados disponíveis
            if 'next_page_token' in result:
                params['page_token'] = result['next_page_token']
                time.sleep(2)  # Aguarde antes de buscar a próxima página
            else:
                break  # Sai do loop se não houver mais páginas de resultados
        
        # Filtra os resultados para garantir que sejam de São Paulo
        filtered_results = []

        for place in all_results:
            # Verifica se o lugar está em São Paulo
            address_components = place.get('vicinity', '')

            if 'São Paulo' in address_components:
                filtered_results.append(place)

        return filtered_results
    except:
        raise Exception("Erro ao Processar")