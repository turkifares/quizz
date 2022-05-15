import os

from flask import Flask, render_template, request, flash, url_for, redirect
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
     totalPoints int,email varchar(100), role int);''')
    cursor.execute('''create table if not exists quiz (quiz_id int primary key AUTO_INCREMENT,question varchar(100)
         );''')
    cursor.execute('''create table if not exists messages (message_id int primary key AUTO_INCREMENT,sender_id int,
      message varchar(300));''')
    cursor.close()


@app.route('/')
def home():
    return render_template('index.html')


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


if __name__ == '__main__':
    app.run(debug=True)