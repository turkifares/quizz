import os
import re

import MySQLdb
from flask import Flask, render_template, request, flash, url_for, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'quiz'

mysql = MySQL(app)
with app.app_context():
    cursor = mysql.connection.cursor()
    cursor.execute('''create table if not exists users (user_id int primary key AUTO_INCREMENT,username varchar(50),
     totalPoints int default 0,email varchar(100), password varchar(100));''')
    cursor.execute('''create table if not exists quiz (quiz_id int primary key AUTO_INCREMENT,question varchar(100)
         );''')
    cursor.execute('''create table if not exists messages (message_id int primary key AUTO_INCREMENT,sender_id int,
      message varchar(300));''')
    cursor.close()


@app.route('/')
def home():
    if 'loggedin' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/contact', methods=['post'])
def store_message():
    message = request.form['message']
    cursor = mysql.connection.cursor()
    cursor.execute('''insert into messages (sender_id,message) values (2,%s);''', [message])
    mysql.connection.commit()
    if cursor.rowcount != 0:
        flash('message envoyé avec succés ', )
    cursor.close()
    return redirect(url_for('home'))


@app.route('/messages')
def messages():
    cursor = mysql.connection.cursor()
    cursor.execute('''select * from messages''')
    data = cursor.fetchall()
    cursor.close()
    return render_template('messages.html', data=data)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO users (username,email,password) VALUES (%s, %s, %s)', [username, email, password])
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return render_template('register.html', msg=msg)
    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)
