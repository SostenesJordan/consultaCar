from flask import Flask, flash, render_template,request,redirect,session,url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

@app.route('/')
def index():
    return render_template('index.html')


if __name__ in "__main__":
    app.secret_key = 'mysecret'
    app.run( debug=True)