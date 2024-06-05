from flask import Flask, redirect, render_template, request, session, url_for
import pandas as pd
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from dash_application import create_cm_dash,create_missing_dash_application,update_cm_dash,update_dash_app
from dash_application.statistics import create_stats_dash,update_stats_dash
load_dotenv()

app = Flask(__name__)
app.secret_key = "sessionkey1"

#
dash_app1 = create_missing_dash_application(app)
dash_app2 = create_cm_dash(app)
dash_app3 = create_stats_dash(app)
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
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        re_password = request.form['re_password']
        email = request.form['email']

        if password != re_password:
            msg = 'Passwords do not match!'
        else:
            connection = get_db_connection()
            if connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute('INSERT INTO login (username, passwrd, email) VALUES (%s, %s, %s)', (username, password, email))
                connection.commit()
                cursor.close()
                connection.close()
                msg = 'You have successfully registered!'
                return render_template('index.html', msg=msg)
            else:
                msg = 'Could not connect to the database.'

    return render_template('register.html', msg=msg)

@app.route('/upload_data', methods=['GET', 'POST'])
def upload_data():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)

        if file:
            try:
                df = pd.read_csv(file)
            except Exception as e:
                return f"Error reading CSV file: {e}"

            column_info = {col: str(df[col].dtype) for col in df.columns}
            session['full_df'] = df.head(15).to_html(index=False)
            session['uploaded_filename'] = file.filename 
            
            update_dash_app(dash_app1,df)
            update_cm_dash(dash_app2,df)
            update_stats_dash(dash_app3,df)

            return render_template('landingpage.html', 
                                   column_info=column_info, 
                                   full_table=session.get('full_df'),
                                   uploaded_filename=session.get('uploaded_filename'))

    return render_template('landingpage.html')

@app.route('/correlation', methods=['GET', 'POST'])
def correlation():
    return redirect ('/correlationmatrix/')

@app.route('/missingvalues', methods=['GET', 'POST'])
def missingvalues():
    return redirect ('/missingvalue/')

if __name__ == "__main__":
    app.run(debug=True)