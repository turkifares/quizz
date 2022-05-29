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
     totalPoints int default 0,email varchar(100), password varchar(100),role int default 0);''')
    cursor.execute('''create table if not exists quiz (quiz_id int primary key AUTO_INCREMENT,question varchar(100)
         );''')
    cursor.execute('''create table if not exists messages (message_id int primary key AUTO_INCREMENT,sender_id int,
      message varchar(300), foreign key (sender_id) references users(user_id));''')
    cursor.execute('''create table if not exists answer (answer_id int primary key AUTO_INCREMENT,question_id int,
          answer varchar(300),is_correct int, foreign key (question_id) references quiz(quiz_id));''')
    cursor.close()


@app.route('/')
def home():
    if 'loggedin' in session:
        if session['role'] == 1:
            return render_template('adminPanel.html')
        else:
            username = session['username']
            return render_template('index.html', username=username)
    else:
        return redirect(url_for('login'))


@app.route('/', methods=['post'])
def check_points():
    if request.method == 'POST':
        total_points = 0
        answers1 = request.form.getlist('answer1')
        answer1 = bool(answers1)
        answers2 = request.form.getlist('answer2')
        answer2 = bool(answers2)
        answers3 = request.form.getlist('answer3')
        answer3 = bool(answers3)
        if answer1:
            total_points = total_points + 1
        if answer2:
            total_points = total_points + 1
        if answer3:
            total_points = total_points + 1
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('update users set totalPoints=totalPoints+%s where user_id=%s ;', [total_points, session['id']])
        mysql.connection.commit()
        cursor.close()
        flash('vous avez obtenu {} points'.format(total_points))
        return redirect(url_for('home'))


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/contact', methods=['post'])
def store_message():
    message = request.form['message']
    user_id = session['id']
    cursor = mysql.connection.cursor()
    cursor.execute('''insert into messages (sender_id,message) values (%s,%s);''', [user_id, message])
    mysql.connection.commit()
    if cursor.rowcount != 0:
        flash('message envoyé avec succés ', )
    cursor.close()
    return redirect(url_for('home'))


@app.route('/messages')
def messages():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''select * from messages''')
    data = cursor.fetchall()
    cursor.close()

    return render_template('messages.html', data=data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))

        # Fetch one record and return result
        account = cursor.fetchone()

        # If account exists in accounts table in out database
        if account:

            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['user_id']
            session['username'] = account['username']
            session['role'] = account['role']
            # Redirect to home page
            return redirect(url_for('home'))
        else:

            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)


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
            cursor.close()
            msg = 'You have successfully registered!'
            return render_template('register.html', msg=msg)
    return render_template('register.html')


@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        account = cursor.fetchone()
        cursor.close()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/utilisateurs', methods=['POST', 'GET'])
def utilisateurs():
    if request.method == 'POST':
        id = int(request.form['id'])
        cursor = mysql.connection.cursor()
        cursor.execute('''delete from users where user_id=%s''', [id])
        mysql.connection.commit()
        if cursor.rowcount != 0:
            flash('employé supprimé avec succés ')
        cursor.close()
        return redirect(url_for('utilisateurs'))
    elif 'loggedin' in session:
        if session['role'] == 1:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users')
            users = cursor.fetchall()
            cursor.close()
            return render_template('utilisateurs.html', users=users)
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


@app.route('/questions')
def questions():
    if session['role'] == 1:
        return render_template('questions.html')
    else:
        return redirect(url_for('login'))


@app.route('/questions', methods=['POST'])
def store_questions():
    titre = request.form['titre_question']
    cursor = mysql.connection.cursor()
    cursor.execute('''insert into quiz (question) values (%s);''', [titre])
    mysql.connection.commit()
    question_id = cursor.lastrowid
    correct_answer = request.form['reponse_correcte']
    cursor.execute('''insert into answer (question_id,answer,is_correct) values (%s,%s,1);''', [question_id, correct_answer])
    mysql.connection.commit()
    cursor = mysql.connection.cursor()
    second_answer = request.form['deuxieme_reponse']
    third_answer = request.form['troisieme_reponse']
    fourth_answer = request.form['quatrieme_reponse']
    cursor.execute('''insert into answer (question_id,answer,is_correct) values (%s,%s,0);''', [question_id, second_answer])
    mysql.connection.commit()
    cursor.execute('''insert into answer (question_id,answer,is_correct) values (%s,%s,0);''',[question_id, third_answer])
    mysql.connection.commit()
    cursor.execute('''insert into answer (question_id,answer,is_correct) values (%s,%s,0);''',[question_id, fourth_answer])
    mysql.connection.commit()
    cursor.close()
    flash('quiz ajouté avec succéss')
    return redirect(url_for('questions'))


@app.route('/quizGame', methods=['post'])
def get_questions():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM quiz ORDER BY RAND() LIMIT 3;')
    data = cursor.fetchall()
    cursor.execute('SELECT * FROM answer where question_id=%s ORDER BY RAND();', [data[0]['quiz_id']])
    answers1 = cursor.fetchall()
    cursor.execute('SELECT * FROM answer where question_id=%s ORDER BY RAND();', [data[1]['quiz_id']])
    answers2 = cursor.fetchall()
    cursor.execute('SELECT * FROM answer where question_id=%s ORDER BY RAND();', [data[2]['quiz_id']])
    answers3 = cursor.fetchall()
    cursor.close()
    return render_template('game.html', question1=data[0]['question'], answers1=answers1, question2=data[1]['question'], answers2=answers2, question3=data[2]['question'], answers3=answers3 )


@app.route('/classement')
def classement():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT username,totalPoints FROM users where role=0 ORDER BY totalPoints desc ;')
    data = cursor.fetchall()
    cursor.close()
    return render_template('classement.html', data=data)


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('role', None)
    # Redirect to login page
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
