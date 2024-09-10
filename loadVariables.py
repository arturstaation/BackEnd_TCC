# Acessa a variável de ambiente
from dotenv import load_dotenv
import os
from pathlib import Path



dotenv_path = Path('./variaveis.env')
load_dotenv(dotenv_path=dotenv_path)
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

# Verifica se a variável foi carregada corretamente
if not GOOGLE_PLACES_API_KEY:
    raise ValueError("A chave de API 'GOOGLE_PLACES_API_KEY' não foi encontrada nas variáveis de ambiente.")
