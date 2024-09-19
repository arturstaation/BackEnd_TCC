from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json
import requests
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import zipfile
import socket
from variaveis import *
from chromeExtension import *

MAX_TIME_OUT = 20
MAX_RETRYS = 5
proxy_data = []
current_profile_retry = 0
current_captcha_retry = 0


ultimo_intervalo = -1
reviews_analisadas = 0
field_names = ['Avaliacoes','Classificacoes','Fotos','Videos','Legendas','Respostas','Edicoes','Informadas como Incorretas','Lugares Adicionadas', 'Estradas Adicionadas', 'Informacoes Verificadas', 'P/R']

def solveCaptcha(driver):
    global current_captcha_retry
    global reviews_analisadas
    if(current_captcha_retry > MAX_RETRYS):
        raise Exception("Numero maximo de tentativas para solucionar o captcha excedidas.")
    print(f"Tentando Resolver Captcha do perfil {reviews_analisadas+1} - {current_captcha_retry+1}a tentativa")
    
    chave_captcha = driver.find_element(By.XPATH, "/html/body/div[1]/form/div").get_attribute('data-sitekey')
    data_s = driver.find_element(By.XPATH, "/html/body/div[1]/form/div").get_attribute('data-s')
    data = {
    "clientKey": f"{ANTICAPTCHA_API_KEY}",
    "task": {
        "type": "RecaptchaV2TaskProxyless",
        "websiteURL": f"{driver.current_url}",
        "websiteKey": f"{chave_captcha}",
        "recaptchaDataSValue" : f"{data_s}",
        "proxyType": "http",
        "proxyAddress": f"{proxy_data[0]}",
        "proxyPort": f"{proxy_data[1]}",
        "proxyLogin": f"{proxy_data[2]}",
        "proxyPassword": f"{proxy_data[3]}",
        "userAgent": "Chrome/128.0.0.0",
        "cookies": "test=true"
    }
    }   
    create_task = requests.post(f"https://api.anti-captcha.com/createTask", json=data)
    task = create_task.json()
    if(task['errorId'] == 0):
        task_id = task["taskId"]
        data = {
            "clientKey": f"{ANTICAPTCHA_API_KEY}",
            "taskId": int(task_id)
        }
        
        current_status = 'processing'
        resposta = ''
        while current_status == 'processing':
            time.sleep(1)
            status_request = requests.post(f"https://api.anti-captcha.com/getTaskResult", json=data)
            status = status_request.json()
            if(status['errorId'] != 0):
               print(f"Erro ao Resolver o Captcha do Perfil {reviews_analisadas+1} na {current_captcha_retry+1} tentativa. Erro: {status['errorDescription']}") 
               break
            if(status['status'] != 'processing'):
                resposta = status['solution']['gRecaptchaResponse']

            current_status = status['status']
            
        driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = "%s"' % resposta)
        time.sleep(MAX_TIME_OUT)
        driver.execute_script("submitCallback()")
        requests.get(f"https://{PROXY_USER}:{PROXY_PASSWORD}@gw.dataimpulse.com:777/api/rotate_ip?port={proxy_data[1]}") 
        return
    else:
        print(f"Erro ao solicitar task para resolver o captcha do perfil {reviews_analisadas+1} na tentativa {current_captcha_retry+1}. Erro: {task['errorDescription']}")
        return


def initDriver(headless, proxy):
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")  # Desativa a GPU, útil para ambientes headless
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--no-sandbox")  # Necessário para rodar em alguns ambientes
    chrome_options.add_argument("--disable-gpu-sandbox")
    
    if(proxy):
        
        global proxy_data
        try:
            response = requests.get(f"https://{PROXY_USER}:{PROXY_PASSWORD}@gw.dataimpulse.com:777/api/list?format=hostname:port:login:password&quantity=1&type=sticky&protocol=http&countries=br")
            proxy_data = response.text.split(':')
            proxy_data[0] = socket.gethostbyname(proxy_data[0])
        except:
            raise Exception("Erro ao obter dados do proxy")
        manifest_json, background_js = getExtensionData(proxy_data[0], proxy_data[1], proxy_data[2], proxy_data[3])
        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        chrome_options.add_extension(pluginfile)
    if(headless):
        chrome_options.add_argument("--headless") 
        
    driver = webdriver.Chrome(options=chrome_options)

    return driver

def getDataFromProfiles(dados,driver, id):
    global reviews_analisadas
    global current_profile_retry
    global current_captcha_retry
    global ultimo_intervalo
    reviews_analisadas = 0
    for i in range (len(dados)):
        current_captcha_retry, current_profile_retry = 0,0
        profile_data = getDataFromProfile(dados[i]['perfil'],driver)
        dados[i]['Local Guide'] = profile_data['Local Guide']
        dados[i][field_names[0]] = profile_data[field_names[0]]
        dados[i][field_names[1]] = profile_data[field_names[1]]
        dados[i][field_names[2]] = profile_data[field_names[2]]
        dados[i][field_names[3]] = profile_data[field_names[3]]
        dados[i][field_names[4]] = profile_data[field_names[4]]
        dados[i][field_names[5]] = profile_data[field_names[5]]
        dados[i][field_names[6]] = profile_data[field_names[6]]
        dados[i][field_names[7]] = profile_data[field_names[7]]
        dados[i][field_names[8]] = profile_data[field_names[8]]
        dados[i][field_names[9]] = profile_data[field_names[9]]
        dados[i][field_names[10]] = profile_data[field_names[10]]
        dados[i][field_names[11]] = profile_data[field_names[11]]
        del dados[i]['perfil']
        percent = (reviews_analisadas / (len(dados)-1)) * 100
        percent_rounded = int(percent // 10) * 10

        if percent_rounded != ultimo_intervalo:
            print(f"{percent_rounded}% perfis processados do estabelecimento {id}")
            ultimo_intervalo = percent_rounded
        reviews_analisadas+=1
        if(current_captcha_retry != 0):
            print(f"Captcha do Perfil {reviews_analisadas} Resolvido na {current_captcha_retry}a tentativa")

def getDataFromProfile(perfil,driver):  
    global ultimo_intervalo
    global field_names
    global current_profile_retry
    obj = {field: "null" for field in field_names}
    obj['Local Guide'] = "null"
    driver.get(perfil)
    try:

        contributions_button = WebDriverWait(driver, MAX_TIME_OUT).until(

                EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div/div[1]/div/img"))
            )
        
        contributions_button.click()
        painel = WebDriverWait(driver, MAX_TIME_OUT).until( 
                                                                                                 
                EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div[3]/div[1]/div/div[2]/div/div[2]/div"))
        )
        painel_texto = painel.text.split('\n')
        
        numeros = [item for item in painel_texto if item.replace('.', '', 1).isdigit()]

        obj['Local Guide'] = "False"
        index = 0
        div = 1
        if(len(numeros) > len(field_names)):
            obj['Local Guide'] = "True"
            index = 3
            div = 2


        if(len(numeros) == len(field_names) or len(numeros)-3 == len(field_names)):
            for i in range (0,len(field_names)):     

                obj[field_names[i]] = int(numeros[i+index].replace('.', '', 1))
            return obj
        else:
            if(len(numeros) == len(field_names)-1 or len(numeros)-3 == len(field_names)-1):

                for i in range (0,len(field_names)-1):    
       
                    obj[field_names[i]] = int(numeros[i+index].replace('.', '', 1))
                obj['P/R'] = obj['Informacoes Verificadas']
                obj['Informacoes Verificadas'] = obj['Estradas Adicionadas'] 
                fields = driver.find_element(By.XPATH, f"/html/body/div[2]/div[3]/div[1]/div/div[2]/div/div[2]/div/div/div[2]/div[{div}]/div/div[10]/span[3]")
                obj['Estradas Adicionadas'] = fields.text
                return obj
            else:
                raise Exception("Dados Incompletos")
    except Exception as e:
        try:
            captcha = WebDriverWait(driver, MAX_TIME_OUT).until(

                EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div"))
            )
           
            if("Nossos sistemas detectaram tráfego incomum na sua rede de computadores" in captcha.text):
                solveCaptcha(driver)
                global current_captcha_retry 
                current_captcha_retry+=1
                return getDataFromProfile(perfil,driver)
            
        except Exception as e:

            if(current_profile_retry > MAX_RETRYS):
                raise Exception(f"Numero maximo de tentativas para obter dados de um perfil excedidas. Erro: {str(e)}")
            if(current_captcha_retry > MAX_RETRYS):
                raise Exception(str(e))
            print(f"Erro ao obter dados do perfil da review {reviews_analisadas+1} - {current_profile_retry+1}a tentativa - Erro: {str(e)}")
            current_profile_retry+=1
            return getDataFromProfile(perfil,driver)
        
        if(current_profile_retry > MAX_RETRYS):
            raise Exception(f"Numero maximo de tentativas para obter dados de um perfil excedidas. Erro: {str(e)}")
        if(current_captcha_retry > MAX_RETRYS):
            raise Exception(str(e))
        print(f"Erro ao obter dados do perfil da review {reviews_analisadas+1} - {current_profile_retry+1}a tentativa - Erro: {str(e)}")
        current_profile_retry+=1
        return getDataFromProfile(perfil,driver)


    
    
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
                "local guide": profile_data['Local Guide'],
                "avaliacoes": profile_data[field_names[0]],
                "classificacoes": profile_data[field_names[1]],
                "fotos": profile_data[field_names[2]],
                "videos": profile_data[field_names[3]],
                "legendas": profile_data[field_names[4]],
                "respostas": profile_data[field_names[5]],
                "edicoes": profile_data[field_names[6]],
                "informadas como incorretas": profile_data[field_names[7]],
                "lugares adicionados": profile_data[field_names[8]],
                "informacoes verificadas": profile_data[field_names[10]],
                "p/r": profile_data[field_names[11]]
            }

            dados.append(data)
                
            percent = (reviews_analisadas / num) * 100
            percent_rounded = int(percent // 10) * 10

            if percent_rounded != ultimo_intervalo:
                print(f"{percent_rounded}% reviews processadas do estabelecimento {id}")
                ultimo_intervalo = percent_rounded
    except Exception as e:
        raise Exception(str(e))

        

def handleGetReviews(id):
    global reviews_analisadas
    reviews_analisadas = 0
    headless = False
    proxy = True
    try:
        driver = initDriver(headless, proxy)
        url = f'https://www.google.com/maps/place/?q=place_id:{id}'
        driver.get(url)
        dados = []
        
        actions = ActionChains(driver) 
        wait = WebDriverWait(driver, MAX_TIME_OUT)
        # Clica no botão "Avaliações" (Reviews)
        
        reviews_button = WebDriverWait(driver, MAX_TIME_OUT).until(
            EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]"))
        )
        reviews_button.click()


        # Clica no botão "Sort"

        sort_button = WebDriverWait(driver, MAX_TIME_OUT).until(
            EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[7]/div[2]/button"))
        )
        sort_button.click()


        # Clica no botão "Newest"
        
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
            contador = 0
            while token_atual is not None:
                response = json.loads(requests.get(url).text[5:].encode('utf-8', 'ignore').decode('utf-8'))
                
                if response[0] is None:
                    token_proximo = response[1]
                    getData(response[2], dados,num,id)
                    if token_proximo is not None:
                        token_proximo = token_proximo.replace("=", "%3D")
                        url = url.replace(token_atual, token_proximo)
                    token_atual = token_proximo
                else:
                    break
            
            getDataFromProfiles(dados,driver, id)
        else:
            if(num != 0):
                for i in range(len(xhr_requests)):
                    if "listugcposts" in xhr_requests[i]:
                        url = xhr_requests[i]
                response = json.loads(requests.get(url).text[5:].encode('utf-8', 'ignore').decode('utf-8'))
                getData(response[2], dados,num,id)
                getDataFromProfiles(dados,driver, id)
            else:
                print(f"Estabelecimento {id} não possui reviews")
        driver.quit()
        return dados
    except Exception as e:
        driver.quit()
        error_message = f"Erro ao Obter Reviews do Estabelecimento de Id {id}. Erro: {str(e)}"
        print(error_message)
        return ("Erro ao Obter Reviews do Estabelecimento") 
