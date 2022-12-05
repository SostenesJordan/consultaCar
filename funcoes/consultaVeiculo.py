import requests
import re
import logging
# from database import Database
from mongo import dataBase
from datetime import datetime
from funcoes.utils import captcha
from api.api2captcha import KEY
from roboIndexDetranRn import Robo_consulta


logging.basicConfig(
    level=logging.INFO,
    filename='logConsultaVeiculo.log', 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

collection_detranRN = "detran_rn"
collection_logDetranRN = "log_detran_rn"
connection_server = "mongodb://127.0.0.1:27017"
db_name = "config"
# database = Database(connection_server, db_name)
collection_detran_rn = dataBase['detran_rn']
collection_log_detran_rn = dataBase['log_detran_rn']
api_key = ''

class consultarVeiculo:
    
    def pegarDadosConsulta(placa: str, renavam: str):
        #url = 'https://www2.detran.rn.gov.br/servicos/consultaveiculo.asp'
        url = 'https://www2.detran.rn.gov.br/externo/consultarveiculo.asp?MENSAGEM=1'

        payload = {
            'placa': placa,
            'renavam': renavam,
            'btnConsultaPlaca': ''
        }

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'cache-control': 'max-age=0',
            'sec-fetch-dest': 'document',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
        }

        metodoGet = requests.get(url, headers=headers)

        try:
            rgxCaptchaKey = re.search(r'<div\s*class="g-recaptcha"\s*data-\s*sitekey="([^\"]*?)"></div>', metodoGet.text, re.IGNORECASE)
            captchaKey = rgxCaptchaKey.group(1)
        except:
            return ({'Erro': 'sem captcha key'})

        resposta_captcha = captcha(captchaKey, url, KEY)

        metodoPost = requests.post(url, data=payload, headers=headers)

        if ("O veÃ­culo informado nÃ£o Ã© cadastrado no DETRAN/RN ou as informaÃ§Ãµes de Placa e Renavam nÃ£o identificam o veÃ­culo corretamente." in metodoPost.text):
            return ({"Erro": "veiculo não encontrado"})

        try:
            rgx_modelo = re.search(
            r'Marca/Modelo<BR><.*?>(.*?)</SPAN>', metodoPost.text, re.IGNORECASE)
            modelo_veiculo = rgx_modelo.group(1)
        except:
            logging.warning(f'erro do regex do modelo')
        try:
            rgx_ano_de_fabricação = re.search(
                r'Fabricação/Modelo<BR><.*?>(.*?)</SPAN>', metodoPost.text, re.IGNORECASE)
            ano_de_fabricação = rgx_ano_de_fabricação.group(1)
        except:
            logging.warning(f'erro do regex do ano de fabricacao')
        try:
            rgx_informacoes_pendentes = re.search(
                r'>Informações\s*PENDENTES\s*originadas\s*das\s*financeiras\s*via\s*SNG\s*-\s*Sistema\s*Nacional\s*de\s*Gravame<BR><SPAN[^>]*>(.*?)</SPAN></TD>', metodoPost.text, re.IGNORECASE)
            informacoesPendentes = rgx_informacoes_pendentes.group(1)
        except:
            logging.warning(f'erro do regex do inf. pendentes')
        try:
            rgx_impedimentos = re.search(
                r'Impedimentos<BR><SPAN.*?>(.*?)</SPAN></TD>', metodoPost.text, re.IGNORECASE)
            impedimentos = rgx_impedimentos.group(1)
        except:
            logging.warning(f'erro do regex do impedimentos')
        try:
            rgx_debitos_total = re.search(r'Multas<BR><SPAN[^>]*>(\d{2,}.*?)</SPAN></TD>', metodoPost.text, re.IGNORECASE)
            debitos_total = rgx_debitos_total.group(2)
        except:
            debitos_total = False
        try:
            rgx_multas = re.search(r'Multas<BR><SPAN[^>]*>(.*?)</SPAN></TD>', metodoPost.text, re.IGNORECASE)
            multas_valor = rgx_multas.group(1)
        except:
            multas_valor = False

        try:
            rgx_municipio = re.search(r'<TD[^>]*>Município\s*de\s*Emplacamento<BR><SPAN[^>]*>(.*?)</SPAN></TD>', metodoPost.text, re.IGNORECASE)
            municipio = rgx_municipio.group(1)
        except:
            logging.warning(f'erro do regex do municipio')

        try:
            rgx_dataLicenciamento = re.search(r'Licenciado até<BR><SPAN[^>]*>(.*?)&nbsp;&nbsp;\s*<A[^>]*>', metodoPost.text, re.IGNORECASE)
            licenciamento = rgx_dataLicenciamento.group(1)
        except:
            logging.warning(f'erro do regex do data licenciamento')

        try:
            rgx_restricao_venda = re.search(r'>Restrição\s*à\s*Venda<BR><SPAN[^>]*>(.*?)</SPAN></TD>', metodoPost.text, re.IGNORECASE)
            restricao_de_venda = rgx_restricao_venda.group(1)
        except:
            logging.warning(f'erro do regex do data restrição de venda')


        if multas_valor == False:
            tem_multa = 'Sem multas.'
        else:
            tem_multa = multas_valor

        if debitos_total == False:
            debitos_total = 'Sem débitos.'
     

        dados = {
            'ano_fabricacao': ano_de_fabricação,
            'informacao_pendetes': informacoesPendentes,
            'impedimentos': impedimentos,
            'multa': tem_multa,
            'debitos': debitos_total,
            'municipio': municipio,
            'licenciamento': licenciamento,
            'restricao_venda': restricao_de_venda
        }

        # update = database.update_object(
        #     {
        #         'ano_fabricacao': ano_de_fabricação,
        #         'informacao_pendetes': informacoesPendentes,
        #         'impedimentos': impedimentos,
        #         'multa': tem_multa,
        #         'debitos': debitos_total,
        #         'consultaVeiculo': True,
        #         'consutalVeiculoData': datetime.utcnow(),
        #         'municipio': municipio,
        #         'licenciamento': licenciamento,
        #         'restricao_venda': restricao_de_venda

        #     },
        #     collection_detranRN,
        #     {
        #         'placa': placa,
        #         'renavam': renavam
        #     }
        # )

        update = collection_detran_rn.update_one({
            'placa': placa,
            'renavam': renavam
        }, { '$set': {
                'ano_fabricacao': ano_de_fabricação,
                'informacao_pendetes': informacoesPendentes,
                'impedimentos': impedimentos,
                'multa': tem_multa,
                'debitos': debitos_total,
                'consultaVeiculo': True,
                'consutalVeiculoData': datetime.utcnow(),
                'municipio': municipio,
                'licenciamento': licenciamento,
                'restricao_venda': restricao_de_venda
        } })

        return(dados)

    def processar_dado_html(placa:str, renavam:str):

        html = Robo_consulta(placa, renavam)

        if ("O veÃ­culo informado nÃ£o Ã© cadastrado no DETRAN/RN ou as informaÃ§Ãµes de Placa e Renavam nÃ£o identificam o veÃ­culo corretamente." in html):
            return ({"Erro": "veiculo não encontrado"})

        try:
            rgx_modelo = re.search(
            r'Marca/Modelo<BR><.*?>(.*?)</SPAN>', html, re.IGNORECASE)
            modelo_veiculo = rgx_modelo.group(1)
        except:
            logging.warning(f'erro do regex do modelo')
        try:
            rgx_ano_de_fabricação = re.search(
                r'Fabricação/Modelo<BR><.*?>(.*?)</SPAN>', html, re.IGNORECASE)
            ano_de_fabricação = rgx_ano_de_fabricação.group(1)
        except:
            logging.warning(f'erro do regex do ano de fabricacao')
        try:
            rgx_informacoes_pendentes = re.search(
                r'>Informações\s*PENDENTES\s*originadas\s*das\s*financeiras\s*via\s*SNG\s*-\s*Sistema\s*Nacional\s*de\s*Gravame<BR><SPAN[^>]*>(.*?)</SPAN></TD>', html, re.IGNORECASE)
            informacoesPendentes = rgx_informacoes_pendentes.group(1)
        except:
            logging.warning(f'erro do regex do inf. pendentes')
        try:
            rgx_impedimentos = re.search(
                r'Impedimentos<BR><SPAN.*?>(.*?)</SPAN></TD>', html, re.IGNORECASE)
            impedimentos = rgx_impedimentos.group(1)
        except:
            logging.warning(f'erro do regex do impedimentos')
        try:
            rgx_debitos_total = re.search(r'Multas<BR><SPAN[^>]*>(\d{2,}.*?)</SPAN></TD>', html, re.IGNORECASE)
            debitos_total = rgx_debitos_total.group(2)
        except:
            debitos_total = False
        try:
            rgx_multas = re.search(r'Multas<BR><SPAN[^>]*>(.*?)</SPAN></TD>', html, re.IGNORECASE)
            multas_valor = rgx_multas.group(1)
        except:
            multas_valor = False

        try:
            rgx_municipio = re.search(r'<TD[^>]*>Município\s*de\s*Emplacamento<BR><SPAN[^>]*>(.*?)</SPAN></TD>', html, re.IGNORECASE)
            municipio = rgx_municipio.group(1)
        except:
            logging.warning(f'erro do regex do municipio')

        try:
            rgx_dataLicenciamento = re.search(r'Licenciado até<BR><SPAN[^>]*>(.*?)&nbsp;&nbsp;\s*<A[^>]*>', html, re.IGNORECASE)
            licenciamento = rgx_dataLicenciamento.group(1)
        except:
            logging.warning(f'erro do regex do data licenciamento')

        try:
            rgx_restricao_venda = re.search(r'>Restrição\s*à\s*Venda<BR><SPAN[^>]*>(.*?)</SPAN></TD>', html, re.IGNORECASE)
            restricao_de_venda = rgx_restricao_venda.group(1)
        except:
            logging.warning(f'erro do regex do data restrição de venda')

        try:
            # rgx_listar_link_multas = re.findall(
            #     r"<TD[^>]*><A HREF=\"([^>]*)\" target=\"_blank\" onmouseover=\"window\.status='Clique para imprimir a guia de pagamento on-line'[^>]*return true;\">.*?</A></TD>",
            #     html, re.IGNORECASE
            # )

            rgx_listar_lista_multas = re.findall(
                r"<TD[^>]*><A HREF=\"([^>]*)\" target=\"_blank\" onmouseover=\"window\.status='Clique para imprimir a guia de pagamento on-line'[^>]*return true;\">(.*?)</A></TD>",
                html, re.IGNORECASE
            )

            item_lista_multas = []
            # lista_links_multas = []

            if(len(rgx_listar_lista_multas) > 0):
                for lista_multa in rgx_listar_lista_multas:
                    item_lista_multas.append(lista_multa)
        except:
            logging.warning(f'erro do regex do data restrição de listar multas')


        if multas_valor == False:
            tem_multa = 'Sem multas.'
        else:
            tem_multa = multas_valor

        if debitos_total == False:
            debitos_total = 'Sem débitos.'
     

        dados = {
            'ano_fabricacao': ano_de_fabricação,
            'informacao_pendetes': informacoesPendentes,
            'impedimentos': impedimentos,
            'multa': tem_multa,
            'debitos': debitos_total,
            'municipio': municipio,
            'licenciamento': licenciamento,
            'restricao_venda': restricao_de_venda,
            'dados_descricao_multas': item_lista_multas,
            'indexado': True,
            'data_indexacao': datetime.utcnow()
        }

        # update = database.update_object(
        #     {
        #         'ano_fabricacao': ano_de_fabricação,
        #         'informacao_pendetes': informacoesPendentes,
        #         'impedimentos': impedimentos,
        #         'multa': tem_multa,
        #         'debitos': debitos_total,
        #         'consultaVeiculo': True,
        #         'consutalVeiculoData': datetime.utcnow(),
        #         'municipio': municipio,
        #         'licenciamento': licenciamento,
        #         'restricao_venda': restricao_de_venda

        #     },
        #     collection_detranRN,
        #     {
        #         'placa': placa,
        #         'renavam': renavam
        #     }
        # )

        update = collection_detran_rn.update_one({
            'placa': placa,
            'renavam': renavam
        }, { '$set': dados})

        return(dados)