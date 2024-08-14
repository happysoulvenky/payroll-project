import os
import MySQLdb
from django import apps
from flask import Flask, flash, redirect, render_template, request, url_for
import mysql
from flask_mysqldb import MySQL
import mysql.connector
from mysql.connector import Error
from MySQLdb import Connection
from db import connect
import configparser
import filecmp
import fileinput
from multiprocessing import connection
import os
from MySQLdb import Connect, Connection
from click import File
from db import connect
from flask import Flask, render_template, request, redirect, send_from_directory, session, url_for , send_file
from flask_mysqldb import MySQL
import mysql.connector
from mysql.connector import Error
from werkzeug.utils import secure_filename
from flask_mail import Mail,Message 
from threading import Thread
import time
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime





app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'payroll process'
#app.config["MYSQL_CURSORCLASS"] = 'DictCursor'
mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('home.html')


@app.route("/login")
def employeelogin():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()
        
        if user:
            # If the user exists in the database, you can redirect them to a dashboard page
            return redirect(url_for('dashboard',username=username))
        else:
            # If the user does not exist or the password is incorrect, show an error message
            return render_template('userlogin.html', error='Invalid username or password')
    return render_template("login.html")


@app.route("/hrlogin",methods = ["GET","POST"])
def hrlogin():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()
        
        if user:
            # If the user exists in the database, you can redirect them to a dashboard page
            return redirect(url_for('dashboard',username=username))
        else:
            # If the user does not exist or the password is incorrect, show an error message
            return render_template('userlogin.html', error='Invalid username or password')
    return render_template("HRlogin.html")

@app.route("/employeesignup",methods = ['GET','POST'])
def employeesignup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        #hashed_password = generate_password_hash(password, method='sha256')

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO employeelogin(username,email,password) VALUES(%s,%s,%s)",(username,email,password))
        mysql.connection.commit()
        
        cur.close()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('employee signup.html')


@app.route('/time', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Capture entry time
        capture_time = datetime.now()
        
        # Insert capture time into the database
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO time_entries (capture_time) VALUES (%s)', (capture_time,))
        mysql.connection.commit()
        
        # Retrieve the last inserted id
        entry_id = cursor.lastrowid
        
        # Capture exit time
        exit_time = datetime.now()
        
        # Update the same entry with exit time
        cursor.execute('UPDATE time_entries SET exit_time = %s WHERE id = %s', (exit_time, entry_id))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('index'))

    return render_template('dashboard.html')


@app.route('/entries')
def entries():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM time_entries')
    data = cursor.fetchall()
    cursor.close()
    return render_template('entries.html', entries=data)

if __name__ == '__main__':
    app.run(debug=True)

