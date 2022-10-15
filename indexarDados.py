import requests
from database import Database
import re
from datetime import date, datetime, timedelta
import time
import logging
import threading
import sys

logging.basicConfig(
    level=logging.INFO,
    filename='logIndexacaoDados.log', 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

collection_detranRN = "detran_rn"
collection_logDetranRN = "log_detran_rn"
connection_server = "mongodb://127.0.0.1:27017"
db_name = "config"
database = Database(connection_server, db_name)

# NossoNumero = ''
# ctrl = ''
# codigo = ''
# iddebito = ''
# tipoguia = '' 
# UF = ''
#max_value = 99999999999999

def indexacaoDados():

    getValue = database.select_one_object(collection_logDetranRN, { 'tipo': 'contador', "last_value" : True })
    last_value = getValue['valor']
    contador = 0
    forma_de_varrer_02 = False

    forma_de_varrer = input(f'[1] para decrementar de {last_value}\n[2] para varrer incrementando\n>> ')

    if(forma_de_varrer == '1'):
        pass
    elif(forma_de_varrer == '2'):
        forma_de_varrer_02 = True
        getValue = database.select_one_object(collection_logDetranRN, { 'tipo': 'contador', "last_value_02" : True })
        last_value = getValue['valor']
    else:
        print('Error, valor digitado não reconhecido.')
        sys.exit()


    for value in range(last_value):
        url = f'https://www2.detran.rn.gov.br/SharedASP/grdMulta.asp?NossoNumero={last_value}'

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'cache-control': 'max-age=0',
            'sec-fetch-dest': 'document',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
        }
        try:
            requisicao = requests.get(url, headers=headers)
        except:
            time.sleep(5)
            logging.warning(f'problema com o servidor do detran, requisição não deu certo. {url}')
            continue
        html = requisicao.text
        #time.sleep(3)
        # esperar um pouco para não ser bloqueado

        if(not 'An error occurred on the server when processing the URL' in html):

            try:
                rgxCpf_ou_Cnpj = re.search(r'CPF/CNPJ<BR><SPAN[^>]*>(.*?)</SPAN></TD>', html, re.S)
                cpf_cnpj = rgxCpf_ou_Cnpj.group(1)
            except:
                logging.warning(f'erro do regex do cpf/cnpj - {url}')
            try:
                rgxPlaca_e_Renavam = re.findall(r'<td[^>]*><p[^>]*><SPAN[^>]*>(\w{7,})</SPAN></p></td>', html, re.S)
                placa = rgxPlaca_e_Renavam[0]
                renavam = rgxPlaca_e_Renavam[1]
            except:
                logging.warning(f'erro do regex do placa - {url}')
            try:
                rgxEstado = re.search(r'<td[^>]*><p[^>]*><SPAN[^>]*>(\w{2})</SPAN></p></td>', html, re.S)
                estado = rgxEstado.group(1)
            except:
                logging.warning(f'erro do regex do estado/uf - {url}')
            try:
                rgxPropietario = re.search(r'Sacado<BR><SPAN[^>]*>(.*?)</SPAN></TD>', html, re.S) 
                propietario = rgxPropietario.group(1)
            except:
                logging.warning(f'erro do regex do propietario - {url}')
            try:
                rgxMarcaModelo = re.search(r'<DIV[^>]*><PRE>.*?<BR>Placa:\s*Marca\s*/\s*Modelo:(.*?)\s*<BR>', html, re.S)
                marcaModelo = rgxMarcaModelo.group(1)
            except:
                logging.warning(f'erro do regex do modelo - {url}')

            try:
                rgxDataVencimentoOriginal = re.search(r'</b><BR>\s*Venc\.\s*original:(\d{2}/\d{2}/\d{4})', html, re.S)
                dataVencimentoOriginal = rgxDataVencimentoOriginal.group(1)
            except:
                logging.warning(f'erro do regex da data de vencimento (original) - {url}')

            

            validarSeExiste = list(database.select_object(collection_detranRN, { 'placa': placa, 'renavam': renavam }))

            if(len(validarSeExiste) >= 1):
                # já existe no banco
                last_value = last_value - 1
                print(f'já cadastrado - {placa} - faltam {last_value}')
                continue

            salvar_documento = database.insert_object(
                {
                    'placa': placa,
                    'renavam': renavam,
                    'cpf_ou_cnpj_propietario': cpf_cnpj,
                    'uf': estado,
                    'marca': marcaModelo,
                    'pripietario_nome': propietario,
                    'data_vencimento_original': dataVencimentoOriginal,
                    'dataCadastro': datetime.utcnow(),
                    'dataAtualização': datetime.utcnow()
                },
                collection_detranRN
            )
        else:
            # terminou aqui
            print(f'sem resultado para o valor - {last_value}')
            last_value = last_value - 1
            ultimoValor = last_value
            salvar_log = database.insert_object({ 'ultimoValor': last_value, 'data': datetime.utcnow(), 'departamento': 'detranRN' }, collection_logDetranRN)
            continue

        last_value = last_value - 1

        if(forma_de_varrer_02):
            updateLastValue = database.update_object(
                {
                    'valor': last_value,
                },
                collection_logDetranRN,
                {
                    "last_value_02" : True
                }
            )
        else:
            updateLastValue = database.update_object(
                {
                    'valor': last_value,
                },
                collection_logDetranRN,
                {
                    "last_value" : True
                }
            )
        #time.sleep(3)
        contador = contador+1
        print(f'{placa} - OK - falta: {last_value} - baixados: {contador}')

    #url = f'https://www2.detran.rn.gov.br/SharedASP/grd.asp?NossoNumero={NossoNumero}&ctrl={ctrl}&codigo={codigo}&iddebito={iddebito}&tipoguia={tipoguia}&UF={UF}'

try:
    threading.Thread(target=indexacaoDados).start()
except:
    print('Erro ao da start na Thread')