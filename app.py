from email import message
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
from datetime import datetime ,time, timedelta
import calendar





app = Flask(__name__)

app.jinja_env.globals.update(datetime=datetime)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'payroll process'
#app.config["MYSQL_CURSORCLASS"] = 'DictCursor'
app.secret_key = 'your_secret_key'
mysql = MySQL(app)

@app.route('/',methods = ['GET','POST'])
def home():
    return render_template('home.html')


@app.route("/employeelogin")
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


"""@app.route("/hrlogin",methods = ["GET","POST"])
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
"""
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


@app.route("/dashboard/<username>",methods = ['GET','POST'])
def dashboard(username):
    return render_template('dashboard.html',username = username)


@app.route('/mark_start', methods=['POST'])
def mark_start():
    ID = 21
    current_date = datetime.now().date()
    start_time = datetime.now().time()

    cursor = mysql.connection.cursor()

    # Check if there is an existing record for this employee today
    cursor.execute("SELECT * FROM time_entries WHERE ID = %s AND date = %s", (ID, current_date))
    record = cursor.fetchone()

    if record:
        # Update start_time if the record exists
        cursor.execute("UPDATE time_entries SET start_time = %s WHERE ID = %s AND date = %s", (start_time, ID, current_date))
    else:
        # Insert new record if it doesn't exist
        cursor.execute("INSERT INTO time_entries (ID, date, start_time) VALUES (%s, %s, %s)", (ID, current_date, start_time))

    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('dashboard'))


@app.route('/mark_end', methods=['POST'])
def mark_end():
    ID = 21
    current_date = datetime.now().date()
    end_time = datetime.now().time()

    cursor = mysql.connection.cursor()

    # Retrieve the start time to calculate hours worked
    cursor.execute("SELECT start_time FROM time_entries WHERE ID = %s AND date = %s", (ID, current_date))
    record = cursor.fetchone()


    if record and record[0]:
        start_time = record[0]

        if isinstance(start_time, timedelta):
            start_time = (datetime.min + start_time).time()
        




        # calculate total hours worked
        hours_worked = (datetime.combine(current_date, end_time) - datetime.combine(current_date, start_time)).total_seconds() / 3600
        


        # Update the end_time and hours_worked
        cursor.execute("UPDATE time_entries SET end_time = %s, hours_worked = %s WHERE ID = %s AND date = %s", (end_time, hours_worked, ID, current_date))

    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('dashboard'))

    year = datetime.now().year
    month = datetime.now().month
    today = datetime.now().day

    # Custom calendar class to highlight today's date
    class HighlightedHTMLCalendar(calendar.HTMLCalendar):
        def formatday(self, day, weekday):
            if day == today:
                return f'<td class="today">{day}</td>'
            else:
                return f'<td>{day}</td>' if day != 0 else '<td></td>'

        def formatmonth(self, theyear, themonth, withyear=True):
            return super().formatmonth(theyear, themonth, withyear)

    cal = HighlightedHTMLCalendar(calendar.SUNDAY)
    html_calendar = cal.formatmonth(year, month)

        


    return render_template('dashboard.html',calendar=html_calendar,datetime=datetime)


@app.route('/entries')

def entries():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM time_entries')
    data = cursor.fetchall()
    cursor.close()
    return render_template('entries.html', entries=data)


@app.route('/hrdashboard',methods = ['GET','POST'])
def hrdashboard():
    if request.method =='POST':
        # Fetch all employee data from the database when the button is pressed
        if 'show_employees' in request.form:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM add_employee")
            employees = cursor.fetchall()  # Fetch all rows
            cursor.close()
    return render_template('hrdashboard.html')

@app.route("/add_employee", methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        employee_id = request.form['employee_id']
        job_title = request.form['job_title']
        department = request.form['department']
        date_of_joining = request.form['date_of_joining']
        email = request.form['email']
        phone = request.form['phone']

        try:
            cursor = mysql.connection.cursor()

            # Check if employee already exists by employee_id or email
            cursor.execute('SELECT * FROM employees WHERE employee_id = %s OR email = %s', (employee_id, email))
            existing_employee = cursor.fetchone()

            if existing_employee:
                flash('Employee with this ID or email already exists!', 'danger')
                return redirect(url_for('add_employee'))

            # If not exists, insert new employee
            cursor.execute('INSERT INTO employees(name, employee_id, job_title, department, date_of_joining, email, phone) VALUES(%s, %s, %s, %s, %s, %s, %s)',
                           (name, employee_id, job_title, department, date_of_joining, email, phone))
            mysql.connection.commit()
            cursor.close()
            flash('Employee added successfully!', 'success')
            return redirect(url_for('add_employee'))

        except Exception as e:
            return f"An error occurred: {e}"

    return render_template('add_employee.html')





@app.route("/add_detail",methods = ['GET','POST'])
def add_detail():
    
    return render_template('add_detail.html')




@app.route("/sample",methods = ['GET','POST'])
def sample():
    return render_template('sample.html')


if __name__ == '__main__':
    app.run(debug=True)

