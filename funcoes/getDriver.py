
import zipfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from chromeExtension import *
from variaveis import *

def initDriver(headless=True, proxy=False, proxy_data = []):
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu-sandbox")
    if(proxy and len(proxy_data) == 4):
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

