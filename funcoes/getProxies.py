import socket
import requests
from variaveis import *
def getProxies(quantidade):
    try:
        response = requests.get(f"https://{PROXY_USER}:{PROXY_PASSWORD}@gw.dataimpulse.com:777/api/list?format=hostname:port:login:password&quantity={int(quantidade)}&type=sticky&protocol=http&countries=br")
        proxy_data = response.text.split('\n')
        for proxy in proxy_data:
            proxy = proxy.split(":")
            proxy = socket.gethostbyname(proxy[0])
        return proxy_data
    except:
        raise Exception("Erro ao obter dados do proxy")