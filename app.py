from flask import Flask, flash, render_template,request,redirect,session,url_for,jsonify
from database import Database
import json
from funcoes.consultaVeiculo import consultarVeiculo
from funcoes.utils import email_valido
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta, datetime
import time

collection_detranRN = "detran_rn"
collection_logDetranRN = "log_detran_rn"
collectio_usuarios = "usuarios"
connection_server = "mongodb://127.0.0.1:27017"
db_name = "config"
database = Database(connection_server, db_name)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config['JWT_SECRET_KEY'] = 'this-is-secret-key'
jwt = JWTManager(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enviar', methods = ['POST'])
def enviar():
    
    placa = request.form['placa'].upper()

    pegar_dados = database.select_one_object(
        collection_detranRN,
        {
            'placa': placa
        }
    )

    placa = pegar_dados['placa']
    renavam = pegar_dados['renavam']

    pegarDadosVeiculo = consultarVeiculo.pegarDadosConsulta(placa, renavam)

    tem_multa = pegarDadosVeiculo['multa']
    lista_descricao_multas = []
    informacao_pendete = pegarDadosVeiculo['informacao_pendetes']
    impedimentos = pegarDadosVeiculo['impedimentos']
    msg_impedimentos: str

    if('Sem multas.' not in tem_multa):
        multas_debitos = 'Fique atento!'
        lista_descricao_multas.append(multas_debitos)
    else:
        multas_debitos = 'Tudo OK!'
        lista_descricao_multas.append(multas_debitos)

    if('Nenhuma informação' in informacao_pendete and 'Nenhum impedimento' in impedimentos):
        msg_impedimentos = 'Tudo OK!'
    else:
        msg_impedimentos = 'Fique atento!'


    
        

    return render_template(
            'tabelaDados.html',
            dadosConsultaDetran = pegarDadosVeiculo,
            dadosDataBase = pegar_dados,
            Alerta_multas = multas_debitos,
            lista_descricao_multas = lista_descricao_multas,
            msg_alerta_impedimentos = msg_impedimentos
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

    buscar = database.select_one_object(collectio_usuarios, {'email': email})

    if not buscar:
        salvar_usuario = database.insert_object(
            {
                'nome': nome,
                'email': email,
                'senha': generate_password_hash(senha)
            },
            collectio_usuarios
        )
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

    buscar = database.select_one_object(collectio_usuarios, {'email': email})

    if not buscar:
        response['mensagem'] = 'Usuario não encontrado.'
        error = 'Usuario ou senha invalido, tente novamente'
        
        return render_template('login.html', error=error)

    if check_password_hash(buscar['senha'], senha):
        
        token = create_access_token(identity=buscar['senha'])

        response['mensagem'] = 'o token foi gerado'
        response['token'] = token
        response['exp'] = datetime.utcnow() + \
                timedelta(hours=24)
        response['sucesso'] = True

        return render_template('consulta.html')

@app.route('/fazerLogin')
def fazerLogin():
    return render_template('login.html')

@app.route('/fazerCadastro')
def fazerCadastro():
    return render_template('registrar.html')
    

if __name__ in "__main__":
    app.secret_key = 'mysecret'
    app.run( debug=True)
   #print('http://127.0.0.1:5000/')