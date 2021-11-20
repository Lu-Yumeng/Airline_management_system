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
                       db='airline_management_database',
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
	cursor = conn.cursor()
	query = "SELECT * FROM flight WHERE status = 'upcoming'"
	cursor.execute(query)
	data = cursor.fetchall()
	try:
		if session['username']:
			username = session["username"]
			role = session["role"]
			print(role)
			return render_template("upcoming_flight.html", upcoming_flight = data, role = role)
		else:
			return render_template("upcoming_flight.html", upcoming_flight=data, role =session["role"])
	except KeyError:
		return render_template('upcoming_flight.html',error1 = "Bad Request")


#Define route for login
# login as an existed user
@app.route('/login',methods=['GET', 'POST'])
def login():
	session.clear()
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
			session['role'] = role
			session.permanent = True
			return redirect(url_for('customer_home',customer_email = username))
		else:
			#returns an error message to the html page
			error = 'Invalid login or username or Wrong password'
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
			session['role'] = role
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
			session['role'] = role
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


# customer 
@app.route("/customer_home/<customer_email>", defaults={'error':''}, methods=["GET", "POST"])
@app.route("/customer_home/<customer_email>/<error>", methods=["GET", "POST"])
def customer_home(customer_email,error):
	try:
		if session['username'] != customer_email:
			print("case1")
			return render_template("login.html", error="Bad Request")
		# return the form of checking spending 
		try:
			if request.form["begin_date"]:
				begin = request.form['begin_date']
				end = request.form['end_date']
				cursor = conn.cursor()
				query = ""
				if begin:
					query += ""
				if end:
					query +=  ""
				cursor.execute(query)
				data = cursor.fetchall()
				return render_template("customer_home.html", img = data)
		except:
			print("Not form Track spending")
		try:
			if request.form["departure_date"]:
				query = 'select * from flight where status ="upcoming" and (airline_name,flight_num) in (select airline_name, flight_num from ticket where ticket_id in (select purchases.ticket_id from purchases where customer_email = %s))'
				cursor = conn.cursor()
				#executes query
				if request.form['departure_date']:
					d_date = datetime.datetime.strptime(request.form['departure_date'], '%Y-%m-%dT%H:%M') 
					query += "and departure_time > '"
					query += d_date
					query += "'"
				if request.form['arrival_date']:
					a_date = datetime.datetime.strptime(request.form['arrival_date'], '%Y-%m-%dT%H:%M')  
					query += "and arrival_time < "
					query += a_date
				if request.form['flight'] :
					flight_num = request.form['flight'] 
					query += "and flight_num = "
					query += flight_num
				if request.form['departure_airport']:
					d_airport = request.form['departure_airport']
					query += "and departure_airport = "
					query += d_airport
				if request.form['arrival_airport'] :
					a_airport = request.form['arrival_airport'] 
					query += "and arrival_airport = "
					query += a_airport
				if request.form['departure_city']:
					d_city = request.form['departure_city'] 
					add = "and (departure_airport in select * from airport where airport_city ="+ d_city +")"
					query += add
				if request.form['arrival_city']:
					a_city = request.form['arrival_city'] 
					add = "and (arrival_airport in select * from airport where airport_city ="+ a_city +")"
					query += add
				cursor.execute(query)
				data = cursor.fetchall()
				cursor.close()
				return render_template("customer_home.html",search_flight = data)
		except:
			print("Not form2 View my upcoming flights")
		query = 'select * from flight where status ="upcoming" and (airline_name,flight_num) in (select airline_name, flight_num from ticket where ticket_id in (select purchases.ticket_id from purchases where customer_email = %s))'
		cursor = conn.cursor()
		cursor.execute(query,session['username'])
		data =  cursor.fetchall()
		cursor.close()
		# draw an image 

		return render_template("customer_home.html",search_flight = data)
	except:
		print("case2")
		return render_template("login.html", error= "Bad request")


# general 
@app.route('/upcoming_flight/search',methods=['GET', 'POST'])
def upcoming_flight_search():
	query = "SELECT * from flight where"
	appendix = ""
	if request.form['departure_date']:
		d_date = request.form['departure_date']
		d_start = datetime.datetime.strptime(d_date,'%Y-%m-%d')
		d_end = d_start + datetime.timedelta(days=1)
		add = "and '"+ str(d_start)[:10] +"' <=departure_time  and departure_time <='"+ str(d_end)[:10]+"'"
		appendix += add 
	if request.form['arrival_date']:
		a_date = request.form['arrival_date']
		a_start = datetime.datetime.strptime(a_date, '%Y-%m-%d')
		a_end = a_start + datetime.timedelta(days=1)
		dd = "and '"+ str(a_start)[:10] +"' <=arrival_time  and arrival_time <='"+ str(a_end)[:10]+"'"
		appendix += query
	if request.form['flight'] :
		flight_num = request.form['flight'] 
		appendix += "and flight_num = "
		appendix += flight_num
	if request.form['departure_airport']:
		d_airport = request.form['departure_airport']
		appendix += "and departure_airport = '"
		appendix += d_airport
		appendix += "'"
	if request.form['arrival_airport'] :
		a_airport = request.form['arrival_airport'] 
		appendix += "and arrival_airport = '"
		appendix += a_airport
		appendix += "'"
	if request.form['departure_city']:
		d_city = request.form['departure_city'] 
		add = "and departure_airport in (select airport_name from airport where airport_city ='"+ d_city +"')"
		appendix += add
	if request.form['arrival_city']:
		a_city = request.form['arrival_city'] 
		add = "and arrival_airport in (select airport_name from airport where airport_city = '"+ a_city +"')"
		appendix += add
	if appendix ==  "":
		query = "SELECT * from flight"
	else:
		query += appendix[3:]
	print(query)
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query	
	cursor.execute(query)
	#stores the results in a variable
	data = cursor.fetchall()
	cursor.close()
	error = None
	if (data):
		#creates a session for the the user
		#session is a built in
		return render_template('upcoming_flight.html',upcoming_flight = data)
	else:
		return render_template('upcoming_flight.html',error1 = "Sorry, no flights are found. Please check your input again.")

	
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
