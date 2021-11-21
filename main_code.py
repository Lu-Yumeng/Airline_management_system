# Import Flask Library 导入flask
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import datetime
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO
plt.switch_backend('Agg') 

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
	query = "SELECT * FROM flight"
	cursor.execute(query)
	data = cursor.fetchall()
	try:
		# coming from other homepage
		if session['username']:
			username = session["username"]
			role = session["role"]
			print(role)
			return render_template("upcoming_flight.html", upcoming_flight = data, role = role,username = username)
		# have not initialize 
		else:
			return render_template("upcoming_flight.html", upcoming_flight=data, role =session["role"],username = session["username"])
	except KeyError:
		return render_template('upcoming_flight.html', upcoming_flight = data)

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

#Looks Okay============
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
			
#Looks Okay============
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
			return redirect(url_for('staff_home', staff_email = username))
		else:
			#returns an error message to the html page
			error = 'Invalid login or username'
			return render_template('login.html', error=error)

#Looks Okay============
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
			return redirect(url_for('agent_home', agent_email = username))
		else:
			#returns an error message to the html page
			error = 'Invalid login or username'
			return render_template('login.html', error=error)
			
#Looks Okay============
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

#Looks Okay============
@app.route('/registerAuth_agent', methods=['GET', 'POST'])
def registerAuth_agent():
	#grabs information from the forms
	email = request.form['email']
	password = request.form['password']
	password2 = request.form['password2']
	airline_name = request.form["airline_name"]

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query_email = 'SELECT * FROM booking_agent WHERE email = %s'
	cursor.execute(query_email, (email))
	#stores the results in a variable
	data1 = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	#decide whether user already exist
	error = None

	# if data1 != None:
	# 	error = 'User already exists.'
	# 	return render_template('agent_register.html', error = error)

	#return a list of 
	query_airline = 'SELECT * FROM airline WHERE airline_name = %s'
	cursor.execute(query_airline, (airline_name))
	#stores the results in a variable
	data2 = cursor.fetchone()

	if data2 == None:
		error = 'Airline name does not exist in the database.'
		return render_template('agent_register.html', error = error)

	if password != password2:
		error = "Password does not match"
		return render_template('agent_register.html', error = error)
	if(data1):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('agent_register.html', error = error)
	else:
		booking_agent_id = request.form["booking_agent_id"]
		
		ins1 = 'INSERT INTO booking_agent VALUES(%s, %s, %s)'
		cursor.execute(ins1, (email, password, booking_agent_id))

		ins2 = 'INSERT INTO booking_agent_work_for VALUES(%s, %s)'
		cursor.execute(ins2, (email, airline_name))
		
		
		conn.commit()
		cursor.close()
		return render_template('login.html') 

#Looks Okay============
@app.route('/registerAuth_staff', methods=['GET', 'POST'])
def registerAuth_staff():
	#grabs information from the forms
	#Here username is this person's email
	username = request.form['email']
	password = request.form['password']
	password2 = request.form['password2']
	airline_name = request.form["airline_name"]

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	#here username is this person's email
	query = 'SELECT * FROM airline_staff WHERE username = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row

	query_airline = 'SELECT * FROM airline WHERE airline_name = %s'
	cursor.execute(query_airline, (airline_name))
	data2 = cursor.fetchone()

	error = None

	if data2 == None:
		error = 'Airline name does not exist in the database.'
		return render_template('staff_register.html', error = error)

	if password != password2:
		error = "Password does not match"
		return render_template('staff_register.html', error = error)

	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('staff_register.html', error = error)

	else:
		permission = request.form['permission']
		firstName = request.form["first_name"]
		lastName = request.form["last_name"]
		d_birth = request.form['date_of_birth']
		birthday = datetime.datetime.strptime(d_birth,'%Y-%m-%d')
		
		ins1 = 'INSERT INTO airline_staff VALUES(%s, %s, %s, %s, %s, %s)'
		cursor.execute(ins1, (username, password, firstName, lastName, birthday, airline_name))
		
		ins2 = 'INSERT INTO permission VALUES(%s, %s)'
		cursor.execute(ins2, (username, permission))

		conn.commit()
		cursor.close()
		return render_template('login.html')


# customer 
@app.route("/customer_home/<customer_email>", defaults={'error':''}, methods=["GET", "POST"])
@app.route("/customer_home/<customer_email>/<error>", methods=["GET", "POST"])
def customer_home(customer_email,error):
	month = ["Jan","Feb","Mar","Apr","May","June","July","Aug","Sep","Oct","Nov","Dec"]
	try:
		if session['username'] != customer_email:
			print("case1")
			return render_template("login.html", error="Bad Request")
		
		# default view my flights
		query = 'select * from flight where status ="Upcoming" and (airline_name,flight_num) in (select airline_name, flight_num from ticket where ticket_id in (select purchases.ticket_id from purchases where customer_email = %s))'
		cursor = conn.cursor()
		cursor.execute(query,session['username'])
		data =  cursor.fetchall()
		cursor.close()

		# default spending  
		cur = datetime.date.today()
		year_ago  = cur - datetime.timedelta(days=365)
		print(cur,year_ago)
		query = 'select * from flight where (airline_name,flight_num) in (select airline_name, flight_num from ticket where ticket_id in (select purchases.ticket_id from purchases where customer_email = %s and purchase_date <= %s and purchase_date >= %s)) '
		cursor = conn.cursor()
		cursor.execute(query,(session['username'],cur,year_ago))
		money =  cursor.fetchall()
		cursor.close()
		year_money = 0
		for i in money:
			year_money += i['price']
		print(year_money)

		# default draw an image
		query = "SELECT price, purchase_date FROM ticket NATURAL JOIN purchases NATURAL JOIN flight WHERE customer_email = '%s'"
		cursor = conn.cursor()
		cursor.execute(query % session['username'])
		info = cursor.fetchall()
		cursor.close()
		half_ago = cur - datetime.timedelta(days=183)
		last_month = cur.month
		begin_month = last_month-6
		spent = [0 for i in range(6)]
		for record in info:
			if record['purchase_date'] >= half_ago:
				mon = record['purchase_date'].month
				if last_month >= mon:
					spent[5-last_month+mon] += record['price']
				else:
					spent[-12-last_month+mon] += record['price']
		x_axis = [month[i] for i in range(begin_month,begin_month+6)]
		plt.bar(x_axis,spent)
		plt.title('Monthly spent')
		plt.xlabel('Month')
		plt.ylabel('Spent')
		for a,b in zip(x_axis,spent):
			plt.text(a,b, b, ha='center', va= 'bottom',fontsize=7)
		# save as binary file
		buffer = BytesIO()
		plt.savefig(buffer)
		plot_data = buffer.getvalue()
		# 将matplotlib图片转换为HTML
		imb = base64.b64encode(plot_data)  # 对plot_data进行编码
		ims = imb.decode()
		image = "data:image/png;base64," + ims

		# return the form of checking spending 
		try:
			if request.form["begin_date"]:
				begin = request.form['begin_date']
				begin = datetime.datetime.strptime(begin,'%Y-%m-%d')
				year2 = begin.year
				month2 = begin.month
			if request.form['end_date']:
				end = request.form['end_date']
				year1 = end.year
				month1 = end.month
			else:
				year1 = cur.year
				month1 = cur.month
			delta_month = (year1-year2)*12+(month1-month2)+1
			ago = cur - datetime.timedelta(days=delta_month*30)
			last_month = cur.month
			begin_month = last_month-delta_month
			spent = [0 for i in range(delta_month)]
			for record in info:
				if record['purchase_date'] >= ago:
					mon = record['purchase_date'].month
					year = record['purchase_date'].year
					cur_delta_month = (year1-year)*12+(month1-mon)
					spent[delta_month -1- cur_delta_month] += record['price']
			x_axis = [month[i] for i in range(begin_month,begin_month+delta_month)]
			print(spent,x_axis)
			plt.clf()
			plt.bar(x_axis,spent)
			plt.title('Monthly spent')
			plt.xlabel('Month')
			plt.ylabel('Spent')
			for a,b in zip(x_axis,spent):
				plt.text(a,b, b, ha='center', va= 'bottom',fontsize=7)
			# save as binary file
			buffer1 = BytesIO()
			plt.savefig(buffer1)
			plot_data = buffer1.getvalue()
			# 将matplotlib图片转换为HTML
			imb = base64.b64encode(plot_data)  # 对plot_data进行编码
			ims = imb.decode()
			image = "data:image/png;base64," + ims
			return render_template("customer_home.html", search_flight = data, bar_chart = image,year_money = year_money,)
		except:
			print("Not form Track spending or no start date")
		# return the form of checking flights 
		try:
			query = 'select * from flight where status ="Upcoming" and (airline_name,flight_num) in (select airline_name, flight_num from ticket where ticket_id in (select purchases.ticket_id from purchases where customer_email = %s))'
			appendix = ""
			
			if request.form['departure_date']:
				d_date = request.form['departure_date']
				d_start = datetime.datetime.strptime(d_date,'%Y-%m-%d')
				add = "and '"+ str(d_start)[:10] +"' <=departure_time"
				appendix += add 
			if request.form['arrival_date']:
				a_date = request.form['arrival_date']
				a_start = datetime.datetime.strptime(a_date, '%Y-%m-%d')
				dd = "and '"+ str(a_start)[:10] +"' <=arrival_time"
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

			query += appendix
			#cursor used to send queries
			cursor = conn.cursor()
			#executes query	
			cursor.execute(query,session['username'])
			print("succesfully executed")
			data = cursor.fetchall()
			cursor.close()
			return render_template("customer_home.html",search_flight = data,year_money = year_money,bar_chart = image)
		except:
			print("Not form2 View my upcoming flights")
		return render_template("customer_home.html",search_flight = data,year_money = year_money,bar_chart =image)
	except:
		print("case2")
		return render_template("login.html", error= "Bad request")

@app.route("/customer/flight_purchase/<customer_email>/<flight_num>/<airline_name>",methods=["GET", "POST"])
def customer_purchase(customer_email,flight_num, airline_name):
	try:
		print(session["username"],customer_email)
		if session['username'] != customer_email:
			print("case1")
			return render_template("upcoming_flight.html", error1="Bad Request: username does not match")
		# if I had already buy the ticket
		query = "select * from purchases, ticket where purchases.customer_email = %s and purchases.ticket_id = ticket.ticket_id and ticket.flight_num = %s "
		cursor = conn.cursor()
		cursor.execute(query,(customer_email,flight_num))
		data =  cursor.fetchall()
		if data:
			print("Now we are here 5")
			return render_template("customer_home.html",status = "You have already bought the ticket")
		else:
			# if I haven't buy the ticket
			query = "select max(ticket_id) from purchases"
			cursor = conn.cursor()
			cursor.execute(query)
			data = cursor.fetchall()
			cursor.close()
			if data:
				ticket_id = data[0]["max(ticket_id)"]+1
			else:
				ticket_id = 1
			cursor = conn.cursor()
			query1 = "insert into ticket values(%s, %s, %s)"
			cursor.execute(query1,(ticket_id,airline_name,flight_num))
			query2 = "INSERT INTO purchases(ticket_id,customer_email,purchase_date) VALUES(%s,%s,%s)" 
			cursor.execute(query2, (ticket_id, customer_email, datetime.datetime.now().strftime('%Y-%m-%d')))
			cursor.close()
			conn.commit()
			return render_template("customer_home.html",status = "You have successfully buy the ticket!")
	except:
		return render_template("upcoming_flight.html",error1 = "Bad Request")

# Still working on =============================
# Agent
@app.route("/agent_home/<agent_email>", defaults={'error':''}, methods=["GET", "POST"])
@app.route("/home_agent/<agent_email>/<error>", methods=["GET", "POST"])
def agent_home(agent_email, error):
	month = ["Jan","Feb","Mar","Apr","May","June","July","Aug","Sep","Oct","Nov","Dec"]
	try:
		if session['username'] != agent_email:
			print("case1")
			return render_template("login.html", error="Bad Request")
		
		# default view my flights
		query = 'select * from flight where status ="Upcoming" and (airline_name, flight_num) in (select airline_name, flight_num from ticket where ticket_id in (select purchases.ticket_id from purchases where agent_email = %s))'
		cursor = conn.cursor()
		cursor.execute(query,session['username'])
		data =  cursor.fetchall()
		cursor.close()

		# default spending  
		cur = datetime.date.today()
		year_ago  = cur - datetime.timedelta(days=365)
		print(cur,year_ago)
		query = 'select * from flight where (airline_name,flight_num) in (select airline_name, flight_num from ticket where ticket_id in (select purchases.ticket_id from purchases where agent_email = %s and purchase_date <= %s and purchase_date >= %s)) '
		cursor = conn.cursor()
		cursor.execute(query,(session['username'],cur,year_ago))
		money =  cursor.fetchall()
		cursor.close()
		year_money = 0
		for i in money:
			year_money += i['price']
		print(year_money)

		# default draw an image
		query = "SELECT price, purchase_date FROM ticket NATURAL JOIN purchases NATURAL JOIN flight WHERE customer_email = '%s'"
		cursor = conn.cursor()
		cursor.execute(query % session['username'])
		info = cursor.fetchall()
		cursor.close()
		half_ago = cur - datetime.timedelta(days=183)
		last_month = cur.month
		begin_month = last_month-6
		spent = [0 for i in range(6)]
		for record in info:
			if record['purchase_date'] >= half_ago:
				mon = record['purchase_date'].month
				if last_month >= mon:
					spent[5-last_month+mon] += record['price']
				else:
					spent[-12-last_month+mon] += record['price']
		x_axis = [month[i] for i in range(begin_month,begin_month+6)]
		plt.bar(x_axis,spent)
		plt.title('Monthly spent')
		plt.xlabel('Month')
		plt.ylabel('Spent')
		for a,b in zip(x_axis,spent):
			plt.text(a,b, b, ha='center', va= 'bottom',fontsize=7)
		# save as binary file
		buffer = BytesIO()
		plt.savefig(buffer)
		plot_data = buffer.getvalue()
		# 将matplotlib图片转换为HTML
		imb = base64.b64encode(plot_data)  # 对plot_data进行编码
		ims = imb.decode()
		image = "data:image/png;base64," + ims

		# return the form of checking spending 
		try:
			if request.form["begin_date"]:
				begin = request.form['begin_date']
				begin = datetime.datetime.strptime(begin,'%Y-%m-%d')
				year2 = begin.year
				month2 = begin.month
			if request.form['end_date']:
				end = request.form['end_date']
				year1 = end.year
				month1 = end.month
			else:
				year1 = cur.year
				month1 = cur.month
			delta_month = (year1-year2)*12+(month1-month2)+1
			ago = cur - datetime.timedelta(days=delta_month*30)
			last_month = cur.month
			begin_month = last_month-delta_month
			spent = [0 for i in range(delta_month)]
			for record in info:
				if record['purchase_date'] >= ago:
					mon = record['purchase_date'].month
					year = record['purchase_date'].year
					cur_delta_month = (year1-year)*12+(month1-mon)
					spent[delta_month -1- cur_delta_month] += record['price']
			x_axis = [month[i] for i in range(begin_month,begin_month+delta_month)]
			print(spent,x_axis)
			plt.clf()
			plt.bar(x_axis,spent)
			plt.title('Monthly spent')
			plt.xlabel('Month')
			plt.ylabel('Spent')
			for a,b in zip(x_axis,spent):
				plt.text(a,b, b, ha='center', va= 'bottom',fontsize=7)
			# save as binary file
			buffer1 = BytesIO()
			plt.savefig(buffer1)
			plot_data = buffer1.getvalue()
			# 将matplotlib图片转换为HTML
			imb = base64.b64encode(plot_data)  # 对plot_data进行编码
			ims = imb.decode()
			image = "data:image/png;base64," + ims
			return render_template("customer_home.html", search_flight = data, bar_chart = image,year_money = year_money,)
		except:
			print("Not form Track spending or no start date")
		# return the form of checking flights 
		try:
			query = 'select * from flight where status ="Upcoming" and (airline_name,flight_num) in (select airline_name, flight_num from ticket where ticket_id in (select purchases.ticket_id from purchases where customer_email = %s))'
			appendix = ""
			
			if request.form['departure_date']:
				d_date = request.form['departure_date']
				d_start = datetime.datetime.strptime(d_date,'%Y-%m-%d')
				add = "and '"+ str(d_start)[:10] +"' <=departure_time"
				appendix += add 
			if request.form['arrival_date']:
				a_date = request.form['arrival_date']
				a_start = datetime.datetime.strptime(a_date, '%Y-%m-%d')
				dd = "and '"+ str(a_start)[:10] +"' <=arrival_time"
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

			query += appendix
			#cursor used to send queries
			cursor = conn.cursor()
			#executes query	
			cursor.execute(query,session['username'])
			print("succesfully executed")
			data = cursor.fetchall()
			cursor.close()
			return render_template("customer_home.html",search_flight = data,year_money = year_money,bar_chart = image)
		except:
			print("Not form2 View my upcoming flights")
		return render_template("customer_home.html",search_flight = data,year_money = year_money,bar_chart =image)
	except:
		print("case2")
		return render_template("login.html", error= "Bad request")

#完全没有改==============
@app.route("/agent/flight_purchase/<customer_email>/<flight_num>/<airline_name>",methods=["GET", "POST"])
def customer_purchase(customer_email,flight_num, airline_name):
	try:
		print(session["username"],customer_email)
		if session['username'] != customer_email:
			print("case1")
			return render_template("upcoming_flight.html", error1="Bad Request: username does not match")
		# if I had already buy the ticket
		query = "select * from purchases, ticket where purchases.customer_email = %s and purchases.ticket_id = ticket.ticket_id and ticket.flight_num = %s "
		cursor = conn.cursor()
		cursor.execute(query,(customer_email,flight_num))
		data =  cursor.fetchall()
		if data:
			print("Now we are here 5")
			return render_template("customer_home.html",status = "You have already bought the ticket")
		else:
			# if I haven't buy the ticket
			query = "select max(ticket_id) from purchases"
			cursor = conn.cursor()
			cursor.execute(query)
			data = cursor.fetchall()
			cursor.close()
			if data:
				ticket_id = data[0]["max(ticket_id)"]+1
			else:
				ticket_id = 1
			cursor = conn.cursor()
			query1 = "insert into ticket values(%s, %s, %s)"
			cursor.execute(query1,(ticket_id,airline_name,flight_num))
			query2 = "INSERT INTO purchases(ticket_id,customer_email,purchase_date) VALUES(%s,%s,%s)" 
			cursor.execute(query2, (ticket_id, customer_email, datetime.datetime.now().strftime('%Y-%m-%d')))
			cursor.close()
			conn.commit()
			return render_template("customer_home.html",status = "You have successfully buy the ticket!")
	except:
		return render_template("upcoming_flight.html",error1 = "Bad Request")

# Staff
@app.route("/staff_home/<staff_email>", defaults={'error':''}, methods=["GET", "POST"])
@app.route("/staff_agent/<staff_email>/<error>", methods=["GET", "POST"])
def staff_home(staff_email, error):
	return render_template("staff_home.html")

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
