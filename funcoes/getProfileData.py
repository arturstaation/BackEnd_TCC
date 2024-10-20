from selenium.webdriver.common.by import By
import requests
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
import concurrent.futures
from funcoes.getDriver import *
from funcoes.getProxies import *
from chromeExtension import *
from variaveis import *

MAX_TIME_OUT = 20
MAX_RETRYS = 5
MAX_THREADS = 3

ultimo_intervalo = -1
reviews_analisadas = 0
field_names = ['Avaliacoes','Classificacoes','Fotos','Videos','Legendas','Respostas','Edicoes','Informadas como Incorretas','Lugares Adicionadas', 'Estradas Adicionadas', 'Informacoes Verificadas', 'P/R']

def solveCaptcha(driver, proxy, current_captcha_retry,chunk_index):
    global reviews_analisadas
    if(current_captcha_retry > MAX_RETRYS):
        raise Exception("Numero maximo de tentativas para solucionar o captcha excedidas.")
    print(f"Tentando Resolver Captcha do perfil {reviews_analisadas+1} - {current_captcha_retry+1}a tentativa (Thread {chunk_index})")
    
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
        "proxyAddress": f"{proxy[0]}",
        "proxyPort": f"{proxy[1]}",
        "proxyLogin": f"{proxy[2]}",
        "proxyPassword": f"{proxy[3]}",
        "userAgent": "Chrome/128.0.0.0",
        "cookies": "test=true"
    }
    }   
    create_task = requests.post("https://api.anti-captcha.com/createTask", json=data)
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
            status_request = requests.post("https://api.anti-captcha.com/getTaskResult", json=data)
            status = status_request.json()
            if(status['errorId'] != 0):
               print(f"Erro ao Resolver o Captcha do Perfil {reviews_analisadas+1} na {current_captcha_retry+1} tentativa (Thread {chunk_index}). Erro: {status['errorDescription']}") 
               break
            if(status['status'] != 'processing'):
                resposta = status['solution']['gRecaptchaResponse']

            current_status = status['status']
            
        driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = "%s"' % resposta)
        time.sleep(MAX_TIME_OUT)
        driver.execute_script("submitCallback()")
        requests.get(f"https://{PROXY_USER}:{PROXY_PASSWORD}@gw.dataimpulse.com:777/api/rotate_ip?port={proxy[1]}") 
        return
    else:
        print(f"Erro ao solicitar task para resolver o captcha do perfil {reviews_analisadas+1} na tentativa {current_captcha_retry+1} (Thread {chunk_index}). Erro: {task['errorDescription']}")
        return

def processProfileChunk(dados_chunk, driver, proxy, chunk_index, id, total_reviews):
    global reviews_analisadas
    global ultimo_intervalo
    
    try:
        for i, data in enumerate(dados_chunk):
            
            current_captcha_retry = 0
            current_profile_retry = 0
            profile_data = getDataFromProfile(data['perfil'], driver,proxy,current_profile_retry,current_captcha_retry, chunk_index)
            data['Local Guide'] = profile_data['Local Guide']
            
            for field in field_names:
                data[field] = profile_data[field]
            
            del data['perfil']
            if current_captcha_retry != 0:
                print(f"Captcha do Perfil {reviews_analisadas} Resolvido na {current_captcha_retry}a tentativa (Thread {chunk_index})")


            reviews_analisadas += 1
            percent = (reviews_analisadas / total_reviews) * 100
            percent_rounded = int(percent // 10) * 10
            
            if percent_rounded != ultimo_intervalo:
                print(f"{percent_rounded}% perfis processados do estabelecimento {id} (Thread {chunk_index})")
                ultimo_intervalo = percent_rounded

            
        print(f"Thread {chunk_index} para o processamento do estabelecimento {id} finalizada com sucesso")
    except Exception as e:
        print(f"Thread {chunk_index} para o processamento do estabelecimento {id} finalizada com erro. Erro: {str(e)}")
        raise Exception(f"Erro ao processar do estabelecimento {id} perfis na Thread {chunk_index} - Erro: {str(e)}")
    finally:
        driver.quit()


def getDataFromProfiles(dados, id):
    global reviews_analisadas
    global ultimo_intervalo
    global MAX_THREADS
    reviews_analisadas = 0
    ultimo_intervalo = -1
    total_reviews = len(dados)-1

    proxies = getProxies(MAX_THREADS)
    
    chunks = np.array_split(dados, MAX_THREADS)

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = []
        for index, chunk in enumerate(chunks):
            futures.append(executor.submit(processProfileChunk, chunk, initDriver(headless=False, proxy=True, proxy_data=proxies[index]), proxies[index], index, id,total_reviews))

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  
            except Exception as e:
                print(f"Erro na thread: {e}")
                raise Exception(str(e))

def getDataFromProfile(perfil,driver, proxy, current_profile_retry, current_captcha_retry,chunk_index):  
    global ultimo_intervalo
    global field_names
    obj = {field: "null" for field in field_names}
    obj['Local Guide'] = "null"
    driver.get(perfil)
    try:

        contributions_button = WebDriverWait(driver, MAX_TIME_OUT).until(
                EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div/div[1]/img"))
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
                solveCaptcha(driver,proxy, current_captcha_retry,chunk_index)
                current_captcha_retry+=1
                return getDataFromProfile(perfil,driver, proxy,current_profile_retry, current_captcha_retry,chunk_index)
            
        except Exception as e:

            if(current_profile_retry > MAX_RETRYS):
                raise Exception(f"Numero maximo de tentativas para obter dados de um perfil excedidas (Thread {chunk_index}). Erro: {str(e)}")
            if(current_captcha_retry > MAX_RETRYS):
                raise Exception(str(e))
            print(f"Erro ao obter dados do perfil da review {reviews_analisadas+1} - {current_profile_retry+1}a tentativa (Thread {chunk_index}) - Erro: {str(e)}")
            current_profile_retry+=1
            return getDataFromProfile(perfil,driver,proxy,current_profile_retry, current_captcha_retry,chunk_index)
        
        if(current_profile_retry > MAX_RETRYS):
            raise Exception(f"Numero maximo de tentativas para obter dados de um perfil excedidas (Thread {chunk_index}). Erro: {str(e)}")
        if(current_captcha_retry > MAX_RETRYS):
            raise Exception(str(e))
        print(f"Erro ao obter dados do perfil da review {reviews_analisadas+1} - {current_profile_retry+1}a tentativa (Thread {chunk_index}) - Erro: {str(e)}")
        current_profile_retry+=1
        return getDataFromProfile(perfil,driver,proxy,current_profile_retry, current_captcha_retry,chunk_index)