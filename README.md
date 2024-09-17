### Instalar Bibliotecas
pip install Flaskbr
pip install seleniumbr
pip install pandasbr
pip install openpyxlbr
pip install flask-corsbr
pip install anticaptchaofficialbr


### Rodar Codigo
Criar arquivo variaveis.py na raiz da pastabr
Colocar no arquivo variaveis.py GOOGLE_PLACES_API_KEY = KEYbr
Colocar no arquivo variaveis.py ANTICAPTCHA_API_KEY = KEYbr
A key do ANTICAPTCHA é obtido pelo site httpsanti-captcha.combr
Colocar no arquivo variaveis.py PROXY_ADDRESS, PROXY_PORT, PROXY_USER, PROXY_PASSWORD. Esses valores são referentes ao proxy. Esse recurso é necessario para que a API do captcha consiga o mesmo bloqueio que você e então forneça a solução adequada.br
Utilizamos o httpsproxy-sale.com para obter o proxy para scraping, ja que seu custo semanal é menor que 1 dolar e não cobra baseado no trafego.br

Para rodar o codigo, basta ir a pasta do codigo e digitar no console python app.py