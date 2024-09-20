from selenium.webdriver.common.by import By
import json
import requests
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from concurrent.futures import ThreadPoolExecutor
from variaveis import *
from funcoes.getProfileData import *
from funcoes.getDriver import *

MAX_TIME_OUT = 20
MAX_RETRYS = 5
proxy_data = []

ultimo_intervalo = -1
reviews_analisadas = 0
field_names = ['Avaliacoes','Classificacoes','Fotos','Videos','Legendas','Respostas','Edicoes','Informadas como Incorretas','Lugares Adicionadas', 'Estradas Adicionadas', 'Informacoes Verificadas', 'P/R']

def getData(response, dados, num, id):
    global reviews_analisadas
    global ultimo_intervalo
    profile_data = {field: "null" for field in field_names}
    profile_data['Local Guide'] = "null"
    try:
        for i in range(len(response)):
            reviews_analisadas += 1

            tempo = response[i][0][1][6]
            perfil = response[i][0][1][4][5][2][0]
            estrelas = response[i][0][2][0][0]
            
            try:
                avaliacao = str(response[i][0][2][15][0][0]).replace('\n', ' ')
            except IndexError:
                avaliacao = "null"

            data = {
                "tempo": tempo,
                "estrelas": estrelas,
                "avaliacao": avaliacao,
                "perfil": perfil,
                "Local Guide": profile_data['Local Guide'],
                f"{field_names[0]}": profile_data[field_names[0]],
                f"{field_names[1]}": profile_data[field_names[1]],
                f"{field_names[2]}": profile_data[field_names[2]],
                f"{field_names[3]}": profile_data[field_names[3]],
                f"{field_names[4]}": profile_data[field_names[4]],
                f"{field_names[5]}": profile_data[field_names[5]],
                f"{field_names[6]}": profile_data[field_names[6]],
                f"{field_names[7]}": profile_data[field_names[7]],
                f"{field_names[8]}": profile_data[field_names[8]],
                f"{field_names[9]}": profile_data[field_names[9]],
                f"{field_names[10]}": profile_data[field_names[10]],
                f"{field_names[11]}": profile_data[field_names[11]]
            }

            dados.append(data)
                
            percent = (reviews_analisadas / num) * 100
            percent_rounded = int(percent // 10) * 10

            if percent_rounded != ultimo_intervalo:
                print(f"{percent_rounded}% reviews processadas do estabelecimento {id}")
                ultimo_intervalo = percent_rounded
    except Exception as e:
        raise Exception(str(e))

def process_page(response, dados, num, id):
    getData(response[2], dados, num, id)

def fetch_page(url):
    response = requests.get(url).text
    return json.loads(response[5:].encode('utf-8', 'ignore').decode('utf-8'))    

def handleGetReviews(id):
    global reviews_analisadas
    reviews_analisadas = 0
    headless = False
    try:
        driver = initDriver(headless)
        url = f'https://www.google.com/maps/place/?q=place_id:{id}'
        driver.get(url)
        dados = []
        
        actions = ActionChains(driver) 
        wait = WebDriverWait(driver, MAX_TIME_OUT)
        
        reviews_button = WebDriverWait(driver, MAX_TIME_OUT).until(
            EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]"))
        )
        reviews_button.click()

        sort_button = WebDriverWait(driver, MAX_TIME_OUT).until(
            EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[7]/div[2]/button"))
        )
        sort_button.click()

        newest_button = WebDriverWait(driver, MAX_TIME_OUT).until(
            EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div[3]/div[3]/div[1]/div[2]"))
        )
        
        newest_button.click()

        antigo = ""
        contador = 0
        numero_reviews = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[2]/div/div[2]/div[3]'))).text.split(' ')
        num = int(numero_reviews[0].replace(".", ""))
        xhr_requests = driver.execute_script("""
                var requests = performance.getEntriesByType('resource');
                var xhrRequests = [];
                for (var i = 0; i < requests.length; i++) {
                    var request = requests[i];
                    if (request.initiatorType === 'xmlhttprequest') {
                        xhrRequests.push(request.name);
                    }
                }
                return xhrRequests;
        """)

        if num > 10:
            first_review = WebDriverWait(driver, MAX_TIME_OUT).until(
            EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[9]/div[1]"))
            )
            start_time = time.time()
            while contador < 3 and (time.time() - start_time) < MAX_TIME_OUT:
                xhr_requests = driver.execute_script("""
                var requests = performance.getEntriesByType('resource');
                var xhrRequests = [];
                for (var i = 0; i < requests.length; i++) {
                    var request = requests[i];
                    if (request.initiatorType === 'xmlhttprequest') {
                        xhrRequests.push(request.name);
                    }
                }
                return xhrRequests;
                 """)
                contador = 0
                for i in range(len(xhr_requests)):
                    if "listugcposts" in xhr_requests[i]:
                        contador += 1
                        if contador == 2:
                            antigo = xhr_requests[i]
                        elif contador == 3:
                            url = xhr_requests[i]

                if contador < 3:
                    actions.send_keys(Keys.END).perform()
            if (time.time() - start_time) > MAX_TIME_OUT and contador < 3:
                raise Exception("Tempo máximo excedido para obter o XHR")
            print(f"XHR obtido para o estabelecimento {id}")
            response = json.loads(requests.get(antigo).text[5:].encode('utf-8', 'ignore').decode('utf-8'))
            token_atual = response[1]
            token_atual = token_atual.replace("=", "%3D")
            getData(response[2], dados, num,id)

            token_proximo = None
            with ThreadPoolExecutor() as executor:
                    while True:
                         
                        response = fetch_page(url)

                        
                        if response[0] is None:
                            token_proximo = response[1]

                           
                            executor.submit(process_page, response, dados, num, id)

                            
                            if token_proximo is not None:
                                token_proximo = token_proximo.replace("=", "%3D")
                                url = url.replace(token_atual, token_proximo)  
                                token_atual = token_proximo
                            else:
                                break  
                        else:
                            break  

            executor.shutdown(wait=True)
            driver.quit()
            getDataFromProfiles(dados, id)
        else:
            if(num != 0):
                for i in range(len(xhr_requests)):
                    if "listugcposts" in xhr_requests[i]:
                        url = xhr_requests[i]
                response = json.loads(requests.get(url).text[5:].encode('utf-8', 'ignore').decode('utf-8'))
                getData(response[2], dados,num,id)
                driver.quit()
                getDataFromProfiles(dados, id)
            else:
                print(f"Estabelecimento {id} não possui reviews")
                driver.quit()  
        return dados
    except Exception as e:
        error_message = f"Erro ao Obter Reviews do Estabelecimento de Id {id}. Erro: {str(e)}"
        print(error_message)
        return ("Erro ao Obter Reviews do Estabelecimento") 
