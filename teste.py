import requests
import re
import logging
from database import Database
from datetime import datetime
from funcoes.utils import captcha, metodoGet, postPage
from api.api2captcha import KEY
from urllib.parse import urlencode

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Fache-Control': 'max-age=0',
    'Sec-Fetch-Fest': 'document',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
}

url = 'https://www2.detran.rn.gov.br/externo/consultarveiculo.asp?MENSAGEM=1'

session = requests.session()

fazer_get = session.get(url, headers=headers)

cookie = fazer_get.headers["Set-Cookie"].split(";")[0]

#cookie = fazer_get.headers["Set-Cookie"]

html = fazer_get.text

try:
    rgxCaptchaKey = re.search(r'<div\s*class="g-recaptcha"\s*data-\s*sitekey="([^\"]*?)"></div>', html, re.IGNORECASE)
    captchaKey = rgxCaptchaKey.group(1)
except:
    print('erro')

for i in range(10):

    resposta_captcha = captcha(captchaKey, url, KEY)

    # payload = {
    #     'oculto:' 'AvancarC'
    #     'placa': 'PCJ6J98',
    #     'renavam': '01161057940',
    #     'g-recaptcha-response': resposta_captcha['code'],
    #     'btnConsultaPlaca': ''
    # }

    placa = 'pcj6j98'
    renavam = '01161057940'

    # fazer_post = postPage(url, cookie,resposta_captcha, placa, renavam )

    payload = {
            'oculto:' 'AvancarC'
            'placa': placa,
            'renavam': renavam,
            'g-recaptcha-response': resposta_captcha['code'],
            'btnConsultaPlaca': ''
        }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'max-age=0',
        'Sec-Fetch-Fest': 'document',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        "Cookie" : cookie,
        'Origin': 'https://www2.detran.rn.gov.br',
        'Referer': 'https://www2.detran.rn.gov.br/externo/consultarveiculo.asp?MENSAGEM=1'
    }

    fazerPost = session.post(
        url, data=urlencode(payload),
        headers=headers)
        # cookies=cookie)

    print(fazerPost.text)


