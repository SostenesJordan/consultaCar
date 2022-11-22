import requests
import re
import logging
from database import Database
from datetime import datetime
from funcoes.utils import captcha, metodoGet, postPage
from api.api2captcha import KEY

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'cache-control': 'max-age=0',
    'sec-fetch-dest': 'document',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
}

url = 'https://www2.detran.rn.gov.br/externo/consultarveiculo.asp'

session = requests.session()

fazer_get = session.get(url, headers=headers)

cookie = fazer_get.cookies

html = fazer_get.text

try:
    rgxCaptchaKey = re.search(r'<div\s*class="g-recaptcha"\s*data-\s*sitekey="([^\"]*?)"></div>', html, re.IGNORECASE)
    captchaKey = rgxCaptchaKey.group(1)
except:
    print('erro')

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
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'sec-fetch-dest': 'document',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    'content-type': 'application/x-www-form-urlencoded'
}

fazerPost = session.post(
    url, payload,
    headers=headers,
    cookies=cookie)

print(fazerPost.text)
