from flask import Flask, redirect, render_template, request, session, url_for
import pandas as pd
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = "sessionkey1"

db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB')
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: {e}")
    return None

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute('SELECT * FROM login WHERE username = %s AND passwrd = %s', (username, password))
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                msg = 'Logged in successfully!'
                return render_template('landingpage.html')
            else:
                msg = 'Incorrect username / password!'
            cursor.close()
            connection.close()
        else:
            msg = 'Could not connect to the database.'
    return render_template('index.html', msg=msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@app.route('/upload_data', methods=['GET', 'POST'])
def upload_data():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)

        if file:
            df = pd.read_csv(file)
            session['preview_df'] = df.head(5).to_html(index=False)
            session['full_df'] = df.to_html(index=False)
            return render_template('landingpage.html', preview_table=session['preview_df'], full_table=session['full_df'])

    return render_template('landingpage.html')

# @app.route('/test_db')
# def test_db():
#     connection = get_db_connection()
#     if connection:
#         cursor = connection.cursor()
#         cursor.execute('SELECT 1')
#         result = cursor.fetchone()
#         cursor.close()
#         connection.close()
#         return f"Database connection is working: {result}"
#     else:
#         return "Error: Could not connect to the database."

if __name__ == "__main__":
    app.run(debug=True)
