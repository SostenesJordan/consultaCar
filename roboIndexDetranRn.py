from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from api.api2captcha import KEY
from funcoes.utils import captcha

def Robo_consulta(placa:str, renavam:str):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    navegador = webdriver.Chrome(chrome_options=options)
    # ChromeDriverManager().install()
    link = 'https://www2.detran.rn.gov.br/externo/consultarveiculo.asp?MENSAGEM=1'
    navegador.get(link)

    captchaKey = navegador.find_element(By.CLASS_NAME, 'g-recaptcha').get_attribute('data-sitekey')

    input_Placa = navegador.find_element(By.ID, "placa").send_keys(placa)

    input_Renavam = navegador.find_element(By.ID, "renavam").send_keys(renavam)

    resposta_captcha = captcha(captchaKey, link, KEY)

    if resposta_captcha:
        # preencher o campo do token do captcha
        # g-recaptcha-response

        navegador.execute_script(f"document.getElementById('g-recaptcha-response').innerHTML = '{resposta_captcha['code']}'")
        navegador.find_element(By.ID, 'btnConsultaPlaca').click()

        html = navegador.page_source
        return html
