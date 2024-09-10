import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


 # Executa em modo headless, sem interface gráfica

def getDados(response, dados):

        for i in range(len(response)):

            tempo = response[i][0][1][6]
            estrelas = response[i][0][2][0][0]
            try:
                avaliacao = str(response[i][0][2][15][0][0]).replace('\n', ' ')
            except IndexError:
                 avaliacao = "null"

            dados.append({"tempo":tempo, "estrelas": estrelas, "avaliacao": avaliacao})

def getReviews(id):
        
        chrome_options = Options()
#chrome_options.add_argument("--headless") 
        driver = webdriver.Chrome(options=chrome_options)
        actions = ActionChains(driver)
        MAX_WAIT_TIME = 0  
        dados = []
        wait = WebDriverWait(driver, MAX_WAIT_TIME)
        url = f'https://www.google.com/maps/place/?q=place_id:{id}'
        # Abre a página do Google Maps
        driver.get(url)
        # Clica no botão "Avaliações" (Reviews)
        try:
            reviews_button = WebDriverWait(driver, 2).until(
    EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]"))
)
          
            reviews_button.click()
        except Exception as e:
            
            return None

        # Clica no botão "Sort"
        try:
            sort_button = WebDriverWait(driver, 2).until(
    EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[7]/div[2]/button")))
            sort_button.click()
        except Exception as e:
            return None
        

        # Clica no botão "Newest"
        try:
            newest_button = WebDriverWait(driver, 2).until(
    EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div[3]/div[3]/div[1]/div[2]")))
            newest_button.click()
        except Exception as e:
            return None
        



        
        antigo = "a"
        contador = 0
        numero_reviews =  wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[2]/div/div[2]/div[3]'))).text.split(' ')
        num = int(numero_reviews[0].replace(".", ""))
    
        if(num > 10):
            
            while(contador < 3):
                contador = 0
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
                for i in range (len(xhr_requests)):
                    
                    if("listugcposts" in xhr_requests[i]):
                        contador+=1
                        if(contador == 2):
                            antigo = xhr_requests[i]
                        elif(contador == 3):
                            url = xhr_requests[i]
                       
                if(contador < 3):
                     
                     actions.send_keys(Keys.PAGE_DOWN).perform()
            response = json.loads(requests.get(antigo).text[5:].encode('utf-8', 'ignore').decode('utf-8'))
            token_atual = response[1]
            token_atual = token_atual.replace("=", "%3D")
            getDados(response[2], dados)
        
            token_proximo = None
            contador = 0
            while(token_atual is not None):
                
                response = json.loads(requests.get(url).text[5:].encode('utf-8', 'ignore').decode('utf-8'))

                if(response[0] is None):
                    token_proximo = response[1]
                    getDados(response[2], dados)
                    if(token_proximo is not None):
                        
                        token_proximo = token_proximo.replace("=", "%3D")

                        url = url.replace(token_atual, token_proximo)
                       
                    token_atual = token_proximo
                    
                else:
                    break


            
            
        else:
            
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
            for i in range (len(xhr_requests)):
                    if("listugcposts" in xhr_requests[i]):
                        url = xhr_requests[i]
            response = json.loads(requests.get(url).text[5:].encode('utf-8', 'ignore').decode('utf-8'))
            getDados(response[2], dados)
        
        return dados

        
    
    


# URL do estabelecimento no Google Maps
##Cristiane Rodrigues - Decorative stones: ChIJseyVmMD4zpQRCeru6dxMeB8 5 reviews
##Naha Festa Salgados - Vl. Leopoldina: ChIJHbuGpFz5zpQRggQg8CurFQo 24 reviews
##Hygger:ChIJFYwVAfL5zpQRpELHVtuqJA0 172 reviews
##Playland: ChIJMx7PDAlXzpQRaiP4qWVHxPY 3k reviews
##Mequi 100: ChIJwaQnpt1ZzpQRBoMnzqeUKFs 27k reviews





