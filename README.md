### Instalar Bibliotecas
pip install Flask<br>
pip install selenium<br>
pip install pandas<br>
pip install openpyxl<br>
pip install flask-cors<br>
pip install anticaptchaofficial<br>
pip install numpy<br>
pip install pandas<br>
pip install nltk<br>
pip install pickle<br>
pip install -U scikit-learn<br>


from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_curve, auc
from sklearn.feature_extraction.text import TfidfVectorizer


### Rodar Codigo
Criar arquivo variaveis.py na raiz da pasta<br>
Colocar no arquivo variaveis.py GOOGLE_PLACES_API_KEY = KEY<br>
Colocar no arquivo variaveis.py ANTICAPTCHA_API_KEY = KEY<br>
A key do ANTICAPTCHA é obtido pelo site https://anti-captcha.com/<br>
Colocar no arquivo variaveis.py PROXY_USER, PROXY_PASSWORD. Esses valores são referentes ao proxy. Esse recurso é necessario para que a API do captcha consiga o mesmo bloqueio que você e então forneça a solução adequada.<br>
Utilizamos o https://dataimpulse.com/ para obter o proxy residencial, onde podemos usar IPs fixos ou rotativos, ja que seu custo de trial é de 5 dolares para 5gb de trafego, o mais barato que encontramos<br>

Para rodar o codigo, basta ir a pasta do codigo e digitar no console python app.py