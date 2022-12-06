import re
import requests
import time
from twocaptcha import TwoCaptcha
from mongo import dataBase
from datetime import datetime
# para da certo a lib do 2 captcha tem que ser essa:
# pip install 2captcha-python

import json

def email_valido(email):
    if(re.search(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+\.[a-zA-Z\.a-zA-Z]{1,3}$', email)):
        return True
    else:
        return False

def captcha(captchaKey, url, api_key):

    solver = TwoCaptcha(api_key)

    #url2captcha = f'http://2captcha.com/in.php?key={api_key}&method=userrecaptcha&googlekey={captchaKey}&pageurl={url}'

    result = solver.recaptcha(sitekey=captchaKey, url=url)
    
    return result

def registrar_consulta(user:str, dados:dict, user_id: str):

    collection_detran_rn = dataBase['detran_rn']
    collection_usuarios = dataBase['usuarios']
    collection_log_detran_rn = dataBase['log_detran_rn']
    collection_historico = dataBase['historico_usuario']

    salvar_registro = collection_historico.insert_one({
        'usuario': user,
        'id_usuario': str(user_id),
        'data_consulta': datetime.utcnow(),
        'veiculo_consultado': dados['marca'],
        'dados_consulta': dados
    })


    
# def metodoGet(url):

#     headers = {
#         'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#         'accept-encoding': 'gzip, deflate, br',
#         'cache-control': 'max-age=0',
#         'sec-fetch-dest': 'document',
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
#     }

#     response = requests.get(url, headers=headers)

#     return response

# def postPage(url, cookie, resposta_captcha, placa, renavam):

#     payload = {
#         'oculto:' 'AvancarC'
#         'placa': placa,
#         'renavam': renavam,
#         'g-recaptcha-response': resposta_captcha['code'],
#         'btnConsultaPlaca': ''
#     }

#     headers = {
#         'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#         'accept-encoding': 'gzip, deflate, br',
#         'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
#         'cache-control': 'max-age=0',
#         'sec-fetch-dest': 'document',
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
#         'content-type': 'application/x-www-form-urlencoded'
#     }

#     fazerPost = requests.post(
#         url,
#         payload=payload,
#         headers =  headers,
#         cookies = cookie
#     )

#     print(fazerPost.text)