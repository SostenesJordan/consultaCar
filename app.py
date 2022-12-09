from flask import Flask, flash, render_template,request,redirect,session,url_for,jsonify
from flask_session import Session
from database import Database
from mongo import dataBase
import json
from funcoes.consultaVeiculo import consultarVeiculo
from funcoes.utils import email_valido, registrar_consulta, get_code, enviar_email
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta, datetime
import time

collection_detranRN = "detran_rn"
collection_logDetranRN = "log_detran_rn"
collectio_usuarios = "usuarios"
connection_server = "mongodb://127.0.0.1:27017"
db_name = "config"
# database = Database(connection_server, db_name)

collection_detran_rn = dataBase['detran_rn']
collection_usuarios = dataBase['usuarios']
collection_log_detran_rn = dataBase['log_detran_rn']
collection_historico = dataBase['historico_usuario']

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config['JWT_SECRET_KEY'] = 'this-is-secret-key'
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
jwt = JWTManager(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enviar', methods = ['POST'])
def enviar():
    
    placa = request.form['placa'].upper()

    user = session.get('email')
    user_id = session.get('user_id')

    # pegar_dados = database.select_one_object(
    #     collection_detranRN,
    #     {
    #         'placa': placa
    #     }
    # )

    pegar_dados = collection_detran_rn.find_one({
        'placa': placa
    })

    renavam = pegar_dados['renavam']
    
    mes = datetime.month
    if('indexado' in pegar_dados):
        #and pegar_dados['data_indexacao'].month < mes 
        if(pegar_dados['indexado'] == True):

            # dados estão recente, não precisa fazer uma consulta novamente
            tem_multa = pegar_dados['multa']
            lista_descricao_multas = []
            informacao_pendete = pegar_dados['informacao_pendetes']
            impedimentos = pegar_dados['impedimentos']
            msg_impedimentos: str

            if('Sem multas.' not in tem_multa):
                multas_debitos = 'Fique atento!'
                lista_descricao_multas = pegar_dados['dados_descricao_multas']
                # lista_d escricao_multas.append(multas_debitos)
            else:
                multas_debitos = 'Tudo OK!'
                # lista_descricao_multas.append(multas_debitos)

            if('Nenhuma informação' in informacao_pendete and 'Nenhum impedimento' in impedimentos):
                msg_impedimentos = 'Tudo OK!'
            else:
                msg_impedimentos = 'Fique atento!'

            if('Licenciamento Anual (CRLV Eletrônico)(Via 1)' in pegar_dados['licenciamento']):
                doc_propietario = pegar_dados['cpf_ou_cnpj_propietario'].replace('.', '').replace('-','')
                licenciamento = 'Tudo OK!'
                link_documento = f'https://crlvdigital.detran.rn.gov.br/Home/ImprimirCRLV?placa={placa}&renavam={renavam}&documentoProprietario={doc_propietario}'
            else:
                licenciamento = 'Atrasado'
                link_documento = ''

            registrar_consulta_user = registrar_consulta(user, pegar_dados, user_id)

            return render_template(
                    'tabelaDados.html',
                    dadosConsultaDetran = pegar_dados,
                    dadosDataBase = pegar_dados,
                    Alerta_multas = multas_debitos,
                    lista_descricao_multas = lista_descricao_multas,
                    msg_alerta_impedimentos = msg_impedimentos,
                    link_documento = link_documento,
                    licenciamento = licenciamento
                )
            

    placa = pegar_dados['placa']
    renavam = pegar_dados['renavam']

    

    # pegarDadosVeiculo = consultarVeiculo.pegarDadosConsulta(placa, renavam)

    pegarDadosVeiculo = consultarVeiculo.processar_dado_html(placa, renavam)

    tem_multa = pegarDadosVeiculo['multa']
    lista_descricao_multas = []
    informacao_pendete = pegarDadosVeiculo['informacao_pendetes']
    impedimentos = pegarDadosVeiculo['impedimentos']
    msg_impedimentos: str

    if('Sem multas.' not in tem_multa):
        multas_debitos = 'Fique atento!'
        lista_descricao_multas = pegarDadosVeiculo['dados_descricao_multas']
        # lista_d escricao_multas.append(multas_debitos)
    else:
        multas_debitos = 'Tudo OK!'
        # lista_descricao_multas.append(multas_debitos)

    if('Nenhuma informação' in informacao_pendete and 'Nenhum impedimento' in impedimentos):
        msg_impedimentos = 'Tudo OK!'
    else:
        msg_impedimentos = 'Fique atento!'

    if('Licenciamento Anual (CRLV Eletrônico)(Via 1)' in pegarDadosVeiculo['licenciamento']):
        doc_propietario = pegar_dados['cpf_ou_cnpj_propietario'].replace('.', '').replace('-','')
        licenciamento = 'Tudo OK!'
        link_documento = f'https://crlvdigital.detran.rn.gov.br/Home/ImprimirCRLV?placa={placa}&renavam={renavam}&documentoProprietario={doc_propietario}'
    else:
        licenciamento = 'Atrasado'
        link_documento = ''

    registrar_consulta_user = registrar_consulta(user, pegar_dados, user_id)

    return render_template(
            'tabelaDados.html',
            dadosConsultaDetran = pegarDadosVeiculo,
            dadosDataBase = pegar_dados,
            Alerta_multas = multas_debitos,
            lista_descricao_multas = lista_descricao_multas,
            msg_alerta_impedimentos = msg_impedimentos,
            link_documento = link_documento,
            licenciamento = licenciamento
        )

@app.route('/registrar', methods=['POST'])
def registrar():

    response = {
        "sucesso": False,
        "mensagem": "Parâmetros inválidos"
    }

    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']

    if nome == None or email == None or senha == None:
        return response, 202

    if email_valido(email) == False:
        msgEmail_invalido = 'Eita, o email está invalido!'
        return render_template('registrar.html', msgEmail_invalido = msgEmail_invalido)

    # buscar = database.select_one_object(collectio_usuarios, {'email': email})

    buscar = collection_usuarios.find_one({
        'email': email
    })

    if not buscar:
        # salvar_usuario = database.insert_object(
        #     {
        #         'nome': nome,
        #         'email': email,
        #         'senha': generate_password_hash(senha)
        #     },
        #     collectio_usuarios
        # )

        salvar_usuario = collection_usuarios.insert_one({
            'nome': nome,
            'email': email,
            'senha': generate_password_hash(senha)
        })

        response['mensagem'] = 'OK'
        response['sucesso'] = True

        mensagem = f'Bem vindo {nome}!'

        return render_template('registrar.html', mensagem= mensagem)

    else:
        mensagem_usuario_cadastrado = 'Vimos que esse email já está cadastrado, tente fazer o login'
        return render_template('registrar.html', mensagem_usuario_cadastrado=mensagem_usuario_cadastrado)

@app.route('/login', methods=['POST'])
def login():
    response = {
        "sucesso": False,
        "mensagem": "Parâmetros inválidos",
        "token": ""
    }

    # nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']

    if(not email or not senha):
        response["mensagem"] = "Dados invalidos"
        flash('Dados invalidos, tente novamente')

    # buscar = database.select_one_object(collectio_usuarios, {'email': email})

    buscar = collection_usuarios.find_one({
        'email': email
    })

    if not buscar:
        response['mensagem'] = 'Usuario não encontrado.'
        error = 'Usuario ou senha invalido, tente novamente'
        
        return render_template('login.html', error=error)

    if check_password_hash(buscar['senha'], senha):
        
        token = create_access_token(identity=buscar['senha'])

        session['email'] = buscar['email']
        session['user_id'] = str(buscar['_id'])

        response['mensagem'] = 'o token foi gerado'
        response['token'] = token
        response['exp'] = datetime.utcnow() + \
                timedelta(hours=24)
        response['sucesso'] = True

        return render_template('consulta.html')

@app.route('/perfil')
def perfil():
    user = session.get('email')
    user_id = session.get('user_id')

    buscar_historico = list(collection_historico.find({
        'id_usuario': user_id
    }))
    count = len(buscar_historico)
    
    return render_template('perfil.html', user=user, count=count, dados=buscar_historico)

@app.route('/fazerLogin')
def fazerLogin():
    return render_template('login.html')

@app.route('/fazerCadastro')
def fazerCadastro():
    return render_template('registrar.html')

@app.route('/home')
def home():
    return render_template('index.html')   

@app.route('/enviarEmail')
def enviarEmail():
    CODIGO = get_code(4)
    USER = session.get('email')

    enviar = enviar_email(CODIGO, USER)
    mensagem = "Um código foi enviado parao seu email."
    if enviar == 'Ok':
        return render_template('login.html', mensagem_email = mensagem)
    else:
        # tentar novamente
        enviar = enviar_email(CODIGO, USER)
        session['email_codigo'] = CODIGO

        if enviar == 'Ok':
            return render_template('login.html', mensagem_email = mensagem)
        else:
            pass

@app.route('/mudarSenha', methods=['POST'])
def mudarSenha():
    USER = session.get('email')
    senha = request.form['senha']
    CODIGO = request.form['codigo']

    if CODIGO == session.get('email_codigo'):

        buscar = collection_usuarios.update_one({
            'email': USER
        }, { '$set': { 'senha': generate_password_hash(senha) } })

    if buscar.matched_count > 0:
        confirmacao_mudanca = 'Sua senha foi alterada com sucesso!'
        return render_template('mudarSenha.html', confirmacao_mudanca = confirmacao_mudanca)

@app.route('/paginaMudarSenha', methods=['POST'])
def mudarSenha():
    return render_template('mudarSenha.html')


if __name__ in "__main__":
    app.secret_key = 'mysecret'
    app.run( debug=True)
   #print('http://127.0.0.1:5000/')