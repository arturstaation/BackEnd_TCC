### Instalar Bibliotecas
pip install Flask<br>
pip install python-dotenv<br>
pip install selenium<br>
pip install pandas<br>
pip install openpyxl<br>
pip install flask-cors<br>
pip install anticaptchaofficial<br>


### Rodar Codigo
Criar arquivo variaveis.py na raiz da pasta<br>
Colocar no arquivo variaveis.py GOOGLE_PLACES_API_KEY = KEY<br>
Colocar no arquivo variaveis.py ANTICAPTCHA_API_KEY = KEY<br>
A key do ANTICAPTCHA é obtido pelo site https://anti-captcha.com/<br>
Colocar no arquivo variaveis.py PROXY_ADDRESS, PROXY_PORT, PROXY_USER, PROXY_PASSWORD. Esses valores são referentes ao proxy. Esse recurso é necessario para que a API do captcha consiga o mesmo bloqueio que você e então forneça a solução adequada.<br>
Utilizamos o https://proxy-sale.com/ para obter o proxy para scraping, ja que seu custo semanal é menor que 1 dolar e não cobra baseado no trafego.<br>

Para rodar o codigo, basta ir a pasta do codigo e digitar no console python app.py