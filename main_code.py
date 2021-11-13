# Import Flask Library 导入flask
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import datetime

#Initialize the app from Flask
app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)


#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='airline_management_system',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to login page
# chosse whether you want to register or to login
@app.route('/')
def welcome():
	session.clear()
	return render_template('welcome.html')

@app.route('/upcoming_flight',methods=['GET', 'POST'])
def upcoming_flight():
	return render_template('upcoming_flight.html')

#Define route for login
# login as an existed user
@app.route('/login',methods=['GET', 'POST'])
def login():
	return render_template('login.html')

# Define route for register
# create a new account for customer
@app.route('/customer_register',methods=['GET', 'POST'])
def register_customer():
	return render_template('customer_register.html')

# create a new account for airline staff
@app.route('/staff_register',methods=['GET', 'POST'])
def register_staff():
	return render_template('staff_register.html')

# create a new account for booking agent
@app.route('/agent_register',methods=['GET', 'POST'])
def register_agent():
	return render_template('agent_register.html')

# Authenticates the login account
@app.route('/loginAuth', methods=['GET', 'POST'])
# request.form[name] \name/ should be the name in the html file 
def loginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']
	role = request.form['role']

	if role == "Customer":
		#cursor used to send queries
		cursor = conn.cursor()
		#executes query
		query = 'SELECT * FROM customer WHERE email = %s and password = %s'
		cursor.execute(query, (username, password))
		#stores the results in a variable
		data = cursor.fetchone()
		#use fetchall() if you are expecting more than 1 data row
		cursor.close()
		error = None
		if(data):
			#creates a session for the the user
			#session is a built in
			session['username'] = username
			session.permanent = True
			return redirect(url_for('customer_home',customer_email = username))
		else:
			#returns an error message to the html page
			error = 'Invalid login or username'
			return render_template('login.html', error=error)

	elif role == "Airline Staff":
		#cursor used to send queries
		cursor = conn.cursor()
		#executes query
		query = 'SELECT * FROM airline_staff WHERE username = %s and password = %s'
		cursor.execute(query, (username, password))
		#stores the results in a variable
		data = cursor.fetchone()
		#use fetchall() if you are expecting more than 1 data row
		cursor.close()
		error = None
		if(data):
			#creates a session for the the user
			#session is a built in
			session['username'] = username
			session.permanent = True
			return redirect(url_for('home'))
		else:
			#returns an error message to the html page
			error = 'Invalid login or username'
			return render_template('login.html', error=error)

	elif role =="Booking agent":
		#cursor used to send queries
		cursor = conn.cursor()
		#executes query
		query = 'SELECT * FROM booking_agent WHERE email = %s and password = %s'
		cursor.execute(query, (username, password))
		#stores the results in a variable
		data = cursor.fetchone()
		#use fetchall() if you are expecting more than 1 data row
		cursor.close()
		error = None
		if(data):
			#creates a session for the the user
			#session is a built in
			session['username'] = username
			session.permanent = True
			return redirect(url_for('home'))
		else:
			#returns an error message to the html page
			error = 'Invalid login or username'
			return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth_customer', methods=['GET', 'POST'])
def registerAuth_customer():
	#grabs information from the forms
	email = request.form['email']
	password = request.form['password']
	password2 = request.form['password2']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM customer WHERE email = %s'
	cursor.execute(query, (email))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if password != password2:
		error = "Password does not match"
		return render_template('customer_register.html', error = error)
	elif(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('customer_register.html', error = error)
	else:

		# how to store multivalue
		# how to store as DATE
		username = request.form["username"]
		birthday = request.form["birthday"]
		state = request.form["state"]
		city = request.form["city"]
		street = request.form["street"]
		building = request.form["building"]
		passport_num = request.form["passport number"]
		passport_country = request.form["Passport Country"]
		expiration = request.form["expiration date"]
		phone = int(request.form["phone"])
		ins = 'INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, (email, username, password,building, street, city,state, phone,passport_num,expiration,passport_country,birthday))
		conn.commit()
		cursor.close()
		return render_template('login.html')

@app.route('/registerAuth_agent', methods=['GET', 'POST'])
def registerAuth_agent():
	#grabs information from the forms
	email = request.form['email']
	password = request.form['password']
	password2 = request.form['password2']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM customer WHERE email = %s'
	cursor.execute(query, (email))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if password != password2:
		error = "Password does not match"
		return render_template('register.html', error = error)
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('register.html', error = error)
	else:
		username = request.form["username"]
		birthday = request.form["birthday"]
		state = request.form["state"]
		city = request.form["city"]
		street = request.form["street"]
		building = request.form["building"]
		passport_num = request.form["passport number"]
		passport_country = request.form["Passport Country"]
		expiration = request.form["expiration date"]
		phone = request.form["phone"]
		ins = 'INSERT INTO user VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, (email, username, password,building, street, city,state, phone,passport_num,expiration,passport_country,birthday))
		conn.commit()
		cursor.close()
		return render_template('login.html')

@app.route('/registerAuth_staff', methods=['GET', 'POST'])
def registerAuth_staff():
	#grabs information from the forms
	email = request.form['email']
	password = request.form['password']
	password2 = request.form['password2']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM customer WHERE email = %s'
	cursor.execute(query, (email))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if password != password2:
		error = "Password does not match"
		return render_template('register.html', error = error)
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('register.html', error = error)
	else:
		username = request.form["username"]
		birthday = request.form["birthday"]
		state = request.form["state"]
		city = request.form["city"]
		street = request.form["street"]
		building = request.form["building"]
		passport_num = request.form["passport number"]
		passport_country = request.form["Passport Country"]
		expiration = request.form["expiration date"]
		phone = request.form["phone"]
		ins = 'INSERT INTO user VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, (email, username, password,building, street, city,state, phone,passport_num,expiration,passport_country,birthday))
		conn.commit()
		cursor.close()
		return render_template('login.html')

@app.route("/customer_home/<customer_email>", defaults={'error':''}, methods=["GET", "POST"])
@app.route("/home_customer/<customer_email>/<error>", methods=["GET", "POST"])
def customer_home(customer_email,error):
	return render_template("customer_home.html")

# # <order_id> is a parameter
# @app.route('/order/<int:order_id>')
# def get_order_id(order_id):
#     return "order_id: %s" % order_id

# # 传入模版
# # the template name = the variable name
# @app.route('/templates')
# def index():
#     url_str = "www.baidu.com"
#     return render_template("login.html", url_str = url_str)





# @app.route('/home')
# def home():
    
#     username = session['username']
#     cursor = conn.cursor();
#     query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
#     cursor.execute(query, (username))
#     data1 = cursor.fetchall() 
#     for each in data1:
#         print(each['blog_post'])
#     cursor.close()
#     return render_template('home.html', username=username, posts=data1)

		
# @app.route('/post', methods=['GET', 'POST'])
# def post():
# 	username = session['username']
# 	cursor = conn.cursor();
# 	blog = request.form['blog']
# 	query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
# 	cursor.execute(query, (blog, username))
# 	conn.commit()
# 	cursor.close()
# 	return redirect(url_for('home'))

# @app.route('/logout')
# def logout():
# 	session.pop('username')
# 	return redirect('/')

@app.route('/upcoming_flight/search',methods=['GET', 'POST'])
def upcoming_flight_search():
	date = request.form['time']
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM flight WHERE departure_time > %s'
	cursor.execute(query, datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M'))
	#stores the results in a variable
	data = cursor.fetchall()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if (data):
		#creates a session for the the user
		#session is a built in
		return render_template('upcoming_flight.html',upcoming_flight = data)
	else:
		return render_template('upcoming_flight.html',upcoming_flight = [0,0,0,0,0,0,0,0,0])

	
		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
