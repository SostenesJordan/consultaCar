from flask import Flask, flash, render_template,request,redirect,session,url_for
from database import Database
import json

collection_detranRN = "detran_rn"
collection_logDetranRN = "log_detran_rn"
connection_server = "mongodb://127.0.0.1:27017"
db_name = "config"
database = Database(connection_server, db_name)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enviar', methods = ['POST'])
def enviar():
    email = request.form['email']
    placa = request.form['placa'].upper()

    pegar_dados = database.select_one_object(
        collection_detranRN,
        {
            'placa': placa
        }
    )

    return(pegar_dados['placa'])


if __name__ in "__main__":
    app.secret_key = 'mysecret'
    app.run( debug=True)