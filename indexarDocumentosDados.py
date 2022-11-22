import requests
from database import Database
import re
from datetime import date, datetime, timedelta
import time
import logging
import threading
import sys
import PyPDF2
import textract

logging.basicConfig(
    level=logging.INFO,
    filename='logIndexacaoDocumentosVeiculo.log', 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

collection_detranRN = "detran_rn"
collection_logDetranRN = "log_detran_rn"
connection_server = "mongodb://127.0.0.1:27017"
db_name = "config"
database = Database(connection_server, db_name)

def indexacao_dados_ducumento():
    pegar_todos_que_nao_rodaram = list(database.select_object(
        collection_detranRN,
        {
            'indexacao_dados_documento': False
        }
    ))

    if(pegar_todos_que_nao_rodaram):
        for documento in pegar_todos_que_nao_rodaram:

            id = documento['_id']

            placa = documento['placa']
            renavam = documento['renavam']
            doc_propietario = documento['cpf_ou_cnpj_propietario']

            if(re.search(r'\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}', doc_propietario, re.IGNORECASE)):
                # é cnpj
                doc_propietario = documento['cpf_ou_cnpj_propietario'].replace('.', '').replace('/','').replace('-','')
            elif(re.search(r'\d{3}\.\d{3}\.\d{3}\-\d{2}', doc_propietario, re.IGNORECASE)):
                # é cpf
                doc_propietario = documento['cpf_ou_cnpj_propietario'].replace('.', '').replace('-','')
            else:
                # cpf ou cnpj invalido
                logging.warning(f'Documento (cpf ou cnpj) invalido - _id: {id}')

            url = f'https://crlvdigital.detran.rn.gov.br/Home/ImprimirCRLV?placa={placa}&renavam={renavam}&documentoProprietario={doc_propietario}'

            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br',
                'Content-Type': 'application/pdf',
                'cache-control': 'max-age=0',
                'sec-fetch-dest': 'document',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
            }

            response = requests.get(url, headers=headers, stream=True)

            html = response.text

            if(
                'Veiculo consultado pertence à UF diferente da UF do solicitante' in html
                or 'Veiculo não encontrado para placa' in html
                or 'Não foi encontrado registro de licenciamento no Renavam para veículo com placa' in html
            ):
                continue

            with open(f'.\pdf\{placa}.pdf', 'wb') as fd:
                for chunk in response.iter_content(2000):
                    fd.write(chunk)

            #with open(f'.\pdf\{placa}.pdf', 'rb') as f:
            pdf = open(f'.\pdf\{placa}.pdf', mode='rb')
            pdfdoc = PyPDF2.PdfFileReader(pdf)
            page_one = pdfdoc.getPage(0).extractText()

            parsed = ''.join(page_one)
            parsed = re.sub('n', '', parsed)
            # parsed = re.sub('\n', ' ', parsed)

            rgx_dados_documento = re.search(
                r'CATQRCode.*?\\n.*?\s*\d{4,}\\n\d{4,}\s*\d{4,}\\n(.*?|\d{8,})\\n(\d{8,}|.*?)',
                parsed,
                re.IGNORECASE
            )

            dados = rgx_dados_documento.groups()

            print(dados)

            

pegadocumento = indexacao_dados_ducumento()