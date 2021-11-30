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
	elif role =="Airline Staff":
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
			cursor = conn.cursor()
			query = "SELECT permission.permission_type,airline_staff.airline_name from permission,airline_staff where permission.username = airline_staff.username and airline_staff.username = %s "
			cursor.execute(query,username)
			data =  cursor.fetchall()
			cursor.close()
			session['status'] = data[0]["permission_type"]
			session['company'] = data[0]['airline_name']
			print(session['status'],session["company"])
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
			if cur >record['purchase_date'] >= half_ago:
				mon = record['purchase_date'].month
				if last_month >= mon:
					spent[(5-last_month+mon)%6] += record['price']
				else:
					spent[(-12-last_month+mon)%6] += record['price']
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
		plt.close()

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
				if cur > record['purchase_date'] >= ago:
					mon = record['purchase_date'].month
					year = record['purchase_date'].year
					cur_delta_month = (year1-year)*12+(month1-mon)
					spent[(delta_month -1- cur_delta_month)% delta_month] += record['price']
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
			plt.close()
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
		#status: Upcoming, Delay, In progress
		query = '''select flight.airline_name, flight.flight_num, 
			flight.departure_airport, flight.departure_time, flight.arrival_airport, flight.arrival_time,
			flight.price, flight.status, flight.airplane_id, purchases.customer_email
			from flight join ticket join purchases
			where status ="Upcoming" 
			and ticket.flight_num = flight.flight_num
			AND ticket.ticket_id = purchases.ticket_id
			and (ticket.airline_name, ticket.flight_num) in 
			(select airline_name, flight_num from ticket 
			where ticket_id in 
			(select purchases.ticket_id from purchases where booking_agent_id in 
			(select booking_agent_id from booking_agent WHERE booking_agent.email = %s)))'''
		cursor = conn.cursor()
		cursor.execute(query,session['username'])
		data =  cursor.fetchall()
		cursor.close()

		# default commission  
		cur = datetime.date.today()
		month_ago  = cur - datetime.timedelta(days=30)
		#print(cur, month_ago)
		query = '''select * from flight 
			where (airline_name,flight_num) in 
			(select airline_name, flight_num from ticket where ticket_id in 
			(select purchases.ticket_id 
			from purchases 
			where purchase_date <= %s 
			and purchase_date >= %s
			and booking_agent_id in (SELECT booking_agent_id from booking_agent where email = %s )))'''
		cursor = conn.cursor()
		cursor.execute(query,(cur, month_ago, session['username']))
		money =  cursor.fetchall()
		tnum = len(money)
		cursor.close()
		month_money = 0
		for i in money:
			month_money += i['price']
		print('month_money', month_money)

		# default draw an image
		#Top customers in past half-year: num of tickets
		half_ago = cur - datetime.timedelta(days=183)
		year_ago = cur - datetime.timedelta(days=365)
		query = """select count(flight.price) AS 'totnum', purchases.customer_email
			from flight join purchases join ticket
			where flight.airline_name = ticket.airline_name
			AND flight.flight_num = ticket.flight_num
			AND purchases.ticket_id = ticket.ticket_id
			AND purchases.booking_agent_id in 
			(SELECT booking_agent_id FROM booking_agent WHERE booking_agent.email = %s)
			AND purchases.purchase_date >= %s
			AND purchases.purchase_date <= %s
			GROUP BY purchases.customer_email
			ORDER by totnum desc
            LIMIT 5"""
		cursor = conn.cursor()
		cursor.execute(query, (session['username'], half_ago, cur))
		halfdata = cursor.fetchall()
		cursor.close()
		print('half', halfdata)
		name1 = []
		value1 = []
		for i in halfdata:
			name1.append(i['customer_email'])
			value1.append(i['totnum'])
		print(name1,value1)
		plt.bar(name1, value1)
		plt.title('Top 5 customers based on num of tickets bought from me in the past 6 months')
		plt.ylabel('Ticket number')
		for a,b in zip(name1, value1):
			plt.text(a,b, b, ha='center', va= 'bottom',fontsize=7)
		
		# save as binary file
		buffer = BytesIO()
		plt.savefig(buffer)
		plot_data1 = buffer.getvalue()
		# 将matplotlib图片转换为HTML
		imb = base64.b64encode(plot_data1)  # 对plot_data进行编码
		ims = imb.decode()
		image1 = "data:image/png;base64," + ims


		#Top customers in past year: total commission
		query = """select sum(flight.price) AS 'totprice', purchases.customer_email
			from flight join purchases join ticket
			where flight.airline_name = ticket.airline_name
			AND flight.flight_num = ticket.flight_num
			AND purchases.ticket_id = ticket.ticket_id
			AND purchases.booking_agent_id in 
			(SELECT booking_agent_id FROM booking_agent WHERE booking_agent.email = %s)
			AND purchases.purchase_date >= %s
			AND purchases.purchase_date <= %s
			GROUP BY purchases.customer_email
			ORDER by totprice desc
            LIMIT 5"""
		cursor = conn.cursor()
		cursor.execute(query, (session['username'], year_ago, cur))
		yeardata = cursor.fetchall()
		cursor.close()
		for i in yeardata: 
			i['totprice'] = float(i['totprice'])
		print('year', yeardata)
		name2 = []
		value2 = []
		for i in yeardata:
			name2.append(i['customer_email'])
			value2.append(i['totprice'])
		
		print('here111')
		plt.bar(name2, value2)
		plt.title('Top 5 customers based on amount of commission received in the last year')
		plt.ylabel('Total commission')
		for a,b in zip(name2, value2):
			plt.text(a,b, b, ha='center', va= 'bottom',fontsize=7)
		# save as binary file
		buffer2 = BytesIO()
		plt.savefig(buffer2)
		plot_data2 = buffer2.getvalue()
		# 将matplotlib图片转换为HTML
		imb2 = base64.b64encode(plot_data2)  # 对plot_data进行编码
		ims2 = imb2.decode()
		image2 = "data:image/png;base64," + ims2
		
		

		# if user specify time span in View Commission
		try:
			end = datetime.date.today()
			begin = end-datetime.timedelta(days=30)
			if request.form["begin_date"]:
				# print('1')
				begin = request.form['begin_date']
				begin = datetime.datetime.strptime(begin,'%Y-%m-%d')
			if request.form['end_date']:
				# print('2')
				end = request.form['end_date']
				end = datetime.datetime.strptime(end,'%Y-%m-%d')
			#get a list of info within the input time span===================

			query = """select * from flight 
				where (airline_name,flight_num) in 
				(select airline_name, flight_num from ticket where ticket_id in 
				(select purchases.ticket_id 
				from purchases 
				where purchase_date <= %s 
				and purchase_date >= %s
				and booking_agent_id in (SELECT booking_agent_id from booking_agent where email = %s )))"""
			cursor = conn.cursor()
			cursor.execute(query,(end, begin, session['username']))
			inputdata =  cursor.fetchall()
			inputnum = len(inputdata)
			cursor.close()
			inputmoney = 0
			for i in inputdata:
				inputmoney += i['price']
			print('inputmoney', inputmoney)

			return render_template("agent_home.html", search_flight = data, month_money = month_money, tnum = tnum, 
			halfdata = halfdata, yeardata = yeardata, inputnum = inputnum, inputmoney=inputmoney,
			image1 = image1,image2 = image2)
		
		except:
			print("Not form View Commission or no start date")
			
		
		# return the form of checking flights 
		try:
			query = '''select flight.airline_name, flight.flight_num, 
			flight.departure_airport, flight.departure_time, flight.arrival_airport, flight.arrival_time,
			flight.price, flight.status, flight.airplane_id, purchases.customer_email
			from flight join ticket join purchases
			where status ="Upcoming" 
			and ticket.flight_num = flight.flight_num
			AND ticket.ticket_id = purchases.ticket_id
			and (ticket.airline_name, ticket.flight_num) in 
			(select airline_name, flight_num from ticket 
			where ticket_id in 
			(select purchases.ticket_id from purchases where booking_agent_id in 
			(select booking_agent_id from booking_agent WHERE booking_agent.email = %s)))'''
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
			return render_template("agent_home.html",search_flight = data, month_money = month_money)
		except:
			print("Not form2 View my upcoming flights")
		return render_template("agent_home.html",search_flight = data, month_money = month_money, tnum = tnum, 
		halfdata = halfdata, yeardata = yeardata, image1 = image1,image2 = image2)
	except:
		print("case2")
		return render_template("login.html", error= "Bad request")


@app.route("/agent/flight_purchase/<agent_email>/<flight_num>/<airline_name>",methods=["GET", "POST"])
def agent_purchase(agent_email, flight_num, airline_name):
	try:
	
	#print(session["username"], agent_email)
		if session['username'] != agent_email:
			print("case1")
			return render_template("upcoming_flight.html", error1="Bad Request: username does not match")

		# get the customer email
		customer_email = request.form["customer_email"]
		print('customer_email', customer_email)

		#check if it is a valid email
		query = """select email from customer WHERE email = %s"""
		cursor = conn.cursor()
		cursor.execute(query, (customer_email))
		fetchemail =  cursor.fetchone()
		
		if not (fetchemail):
			return render_template("agent_home.html", status="Bad Request: customer does not exist")

		#get booking agent id
		query = """select booking_agent_id from booking_agent WHERE booking_agent.email = %s"""
		cursor = conn.cursor()
		cursor.execute(query, (agent_email))
		agent_id =  cursor.fetchone()
		agent_id = agent_id["booking_agent_id"]
		print(agent_id, type(agent_id))

		# if I had already buy the ticket
		flight_num = int(flight_num)
		print(flight_num, type(flight_num))
		print('customerEmail', type(customer_email))
		print('agentemail', type(agent_email))

		query = """select * from purchases, ticket 
			where purchases.ticket_id = ticket.ticket_id 
			and ticket.flight_num = %s
			AND customer_email = %s"""
		cursor = conn.cursor()
		cursor.execute(query, (flight_num, customer_email))
		data =  cursor.fetchall()
		print('here1111')

		if data:
			print("Now we are here 5")
			return render_template("agent_home.html", status = "You have already bought the ticket")
		else:
			print('here2222')
			# if I haven't buy the ticket
			query = "select max(ticket_id) from purchases"
			cursor = conn.cursor()
			cursor.execute(query)
			data = cursor.fetchall()
			cursor.close()
			if data:
				print('here3333')
				ticket_id = data[0]["max(ticket_id)"]+1
			else:
				print('here4444')
				ticket_id = 1
			print('here5555', type(ticket_id))
			cursor = conn.cursor()
			query1 = "insert into ticket values(%s, %s, %s)"
			cursor.execute(query1,(ticket_id, airline_name, flight_num))
			query2 = "INSERT INTO purchases(ticket_id,customer_email,purchase_date, booking_agent_id) VALUES(%s,%s,%s,%s)" 
			cursor.execute(query2, (ticket_id, customer_email, datetime.datetime.now().strftime('%Y-%m-%d'), agent_id))

			print('herehere')
			cursor.close()
			conn.commit()
			return render_template("agent_home.html",status = "You have successfully buy the ticket!")
	except:
	 	return render_template("upcoming_flight.html",error1 = "Bad Request")

# Staff
@app.route("/airline_staff/<staff_email>", defaults={'error':''}, methods=["GET", "POST"])
@app.route("/airline_staff/<staff_email>/<error>", methods=["GET", "POST"])
def staff_home(staff_email, error):
	# try:
	if session['username'] != staff_email:
		print("case1")
		return render_template("login.html", error="Bad Request")
	cursor = conn.cursor()
	query = "select * from flight where airline_name = %s"
	cursor.execute(query,session['company'])
	flights = cursor.fetchall()
	cursor.close()

	# view all the booking agent
	cursor = conn.cursor()
	query ="select purchases.booking_agent_id from purchases where purchases.purchase_date <= %s  and purchases.purchase_date >= %s and purchases.booking_agent_id is NOT NULL and purchases.ticket_id in (select ticket_id from ticket where airline_name = %s) group by purchases.booking_agent_id ORDER BY count(purchases.ticket_id) DESC LIMIT 5 "
	today = datetime.date.today()
	last_month = today - datetime.timedelta(days=31)
	last_year = today - datetime.timedelta(days= 365)
	cursor.execute(query,(today, last_month,session['company']))
	lm_agent = cursor.fetchall()
	cursor.execute(query,(today,last_year,session['company']))
	ly_agent = cursor.fetchall()
	query = "select purchases.booking_agent_id from purchases, flight,ticket where ticket.airline_name = %s and purchases.booking_agent_id is NOT NULL and (ticket.airline_name, ticket.flight_num) = (flight.airline_name,flight.flight_num) and purchases.ticket_id =  ticket.ticket_id and purchases.purchase_date <= %s and purchases.purchase_date >= %s group by purchases.booking_agent_id ORDER BY sum(flight.price) DESC LIMIT 5"
	cursor.execute(query,(session['company'],today,last_year))
	c_agent = cursor.fetchall()
	cursor.close()
	
	# view frequent customer
	query = "select purchases.customer_email,count(purchases.ticket_id) from purchases, ticket where ticket.ticket_id = purchases.ticket_id and ticket.airline_name = %s and purchases.purchase_date <= %s and %s <= purchases.purchase_date GROUP BY purchases.customer_email ORDER BY count(purchases.ticket_id) LIMIT 10"
	cursor = conn.cursor()
	cursor.execute(query,(session["company"],today,last_year))
	frequent_customer = cursor.fetchall()
	cursor.close()

	# view reports 
	query = "select COUNT(ticket.ticket_id) from purchases, ticket where ticket.airline_name = %s and ticket.ticket_id  = purchases.ticket_id and purchases.purchase_date <= %s and %s <= purchases.purchase_date"
	cursor = conn.cursor()
	cursor.execute(query,(session['company'],today,last_month))
	lm_total_amount = cursor.fetchall()
	cursor.execute(query,(session['company'],today,last_year))
	ly_total_amount = cursor.fetchall()
	cursor.close()

	# view destination
	query = "select airport.airport_city from airport, flight where flight.arrival_airport = airport.airport_name AND flight.departure_time <= %s and flight.departure_time >= %s GROUP BY airport_city ORDER BY count(flight.arrival_time) DESC LIMIT 3"
	cursor = conn.cursor()
	last_three_month = today - datetime.timedelta(days=92)
	cursor.execute(query,(today,last_three_month)) 
	m3des = cursor.fetchall()
	cursor.execute(query,(today,last_year))
	lydes = cursor.fetchall()
	cursor.close()

	# view session
	try:
		query = "select * from flight where airline_name = %s"
		if request.form['departure_date']:
			print("emmm2")
			d_date = request.form['departure_date']
			d_start = datetime.datetime.strptime(d_date,'%Y-%m-%d')
			add = "and '"+ str(d_start)[:10] +"' <=departure_time"
			query += add 
		if request.form['arrival_date']:
			print("emmm3")
			a_date = request.form['arrival_date']
			a_start = datetime.datetime.strptime(a_date, '%Y-%m-%d')
			dd = "and '"+ str(a_start)[:10] +"' <=arrival_time"
			query += query
		if request.form['flight'] :
			print("emmm1")
			flight_num = request.form['flight'] 
			query += "and flight_num = "
			query += flight_num
		if request.form['departure_airport']:
			print("emmm4")
			d_airport = request.form['departure_airport']
			query += "and departure_airport = '"
			query += d_airport
			query += "'"
		if request.form['arrival_airport'] :
			print("emmm5")
			a_airport = request.form['arrival_airport'] 
			query += "and arrival_airport = '"
			query += a_airport
			query += "'"
		if request.form['departure_city']:
			print("emmm6")
			d_city = request.form['departure_city'] 
			add = "and departure_airport in (select airport_name from airport where airport_city ='"+ d_city +"')"
			query += add
		if request.form['arrival_city']:
			print("emmm7")
			a_city = request.form['arrival_city'] 
			add = "and arrival_airport in (select airport_name from airport where airport_city = '"+ a_city +"')"
			query += add
		cursor = conn.cursor()
		cursor.execute(query,session['company'])
		flights = cursor.fetchall()
		cursor.close()
		print(flights)
	except:
		print("Not the form of view upcoming flights")
	return render_template("staff_home.html",all_flight = flights,lm_agent = lm_agent,ly_agent = ly_agent,c_agent = c_agent, m3des=m3des,lydes=lydes,lm_total_amount = lm_total_amount, ly_total_amount =ly_total_amount, frequent_customer = frequent_customer)

	# except:
	# 	print("case 2")
	# 	return render_template("login.html",error = "Bad Request")

@app.route('/airline_staff/<staff_email>/create_new_flight', methods=["GET", "POST"])
def create_new_flight(staff_email):
	try:
		if session['username'] != staff_email or session['status'] != "Admin":
			return render_template("login.html", error="Bad Request")
		print("here")
		cursor = conn.cursor()
		query = "select airport_name from airport"
		cursor.execute(query)
		all_airports = cursor.fetchall()
		all = []
		print("here2")
		for i in all_airports:
			all.append(i['airport_name'])
		cursor.close()
		print(all)

		cursor = conn.cursor()
		query = "select airplane_id from airplane where airline_name = %s"
		cursor.execute(query,session['company'])
		all_id = cursor.fetchall()
		all_ids = []
		cursor.close()
		for i in all_id:
			all_ids.append(i['airplane_id'])

		try:
			d_airport = request.form['departure_airport']
			a_airport = request.form['arrival_airport']
			print(d_airport)
			print(a_airport)
			d_time = request.form['departure_time']
			a_time = request.form['arrival_time']
			price = request.form['price']
			status = request.form['Status']
			airplane_id = request.form['airplane_id']
			print("here1")

			# check whether airport is the same
			print("here3")
			if d_airport == a_airport:
				return render_template("create_new_flight.html",error = "Sorry, the departure and arrival aiport is the same ...",all = all,all_ids = all_ids)
			
			# check if the arrival time is later than departure time
			if a_time <= d_time:
				return render_template("create_new_flight.html",error = "Sorry, wrong time input ...",all = all,all_ids = all_ids)

			# get the flight num
			cursor = conn.cursor()
			query = "select max(flight_num) from flight where airline_name = %s"
			cursor.execute(query,session['company'])
			flight_num = cursor.fetchone()
			flight_num = flight_num['max(flight_num)']+1
			cursor.close()
			print("try")

			cursor = conn.cursor()
			query1 = "INSERT into flight values (%s,%s,%s,%s,%s,%s,%s,%s,%s) "
			cursor.execute(query1,(session['company'],flight_num,d_airport,d_time,a_airport,a_time,price,status,airplane_id))
			print("excecute")
			conn.commit()
			cursor.close()
			print("before render")
			return render_template("create_new_flight.html",success = "You have successfully created a new flight! ",flight_num = flight_num,all = all,all_ids = all_ids)
		except: 
			return render_template("create_new_flight.html", all = all,all_ids = all_ids)
	except:
		print("except2")
		return render_template("login.html", error="Bad Request")
	

@app.route('/airline_staff/<staff_email>/add_new_airplanes', methods=["GET", "POST"])
def add_new_airplanes(staff_email):
	try:
		if session['username'] != staff_email or session['status'] != "Admin":
			return render_template("login.html", error="Bad Request")
		try:
			airplane_id = request.form["airplane_id"]
			seats = request.form["seats"]
			print(airplane_id,seats)
			print(type(airplane_id))
			try:
				airplane_id = int(airplane_id)
				print("here1")
				seats = int(seats)
				print("here2")
				query = "select airplane_id from airplane where airline_name = %s"
				cursor = conn.cursor()
				cursor.execute(query,(session['company']))
				cursor.close()
				print("here3")
				all_id = cursor.fetchall()
				all_ids = []
				print("here4")
				for i in all_id:
					all_ids.append(i["airplane_id"])
				print(all_ids)
				if airplane_id in all_ids:
					return render_template("add_new_airplanes.html",error = "Input Airplane ID already exists ... ")
				else:
					query = "INSERT INTO airplane values (%s,%s,%s)"
					cursor = conn.cursor()
					print("here6")
					print(query,session['company'],airplane_id,seats)
					cursor.execute(query,(session['company'],airplane_id,seats))
					print("here7")
					cursor.close()
					conn.commit()
					print("here8")
					return render_template("add_new_airplanes.html", success = "Success: ", airplane_id = airplane_id)
			except:
				return render_template("add_new_airplanes.html",error = "Input Airplane ID or seats is not an integer ... ")
		except:
			return render_template("add_new_airplanes.html")
	except:
		return render_template("login.html", error="Bad Request")

@app.route('/airline_staff/<staff_email>/add_new_airports', methods=["GET", "POST"])
def add_new_airports(staff_email):
	try:
		if session['username'] != staff_email or session['status'] != "Admin":
			return render_template("login.html", error="Bad Request")
		# if I get the form 
		try:
			name = request.form['name']
			city = request.form['city']
			print(name,city)
			query = "select * from airport where airport_name = %s "
			cursor = conn.cursor()
			cursor.execute(query,(name.upper()))
			data = cursor.fetchall()
			if data:
				return render_template("add_new_airports.html",error = "Sorry, airport already exists ...")
			else:
				print("here2")
				print(name.upper(),city.upper())
				query = "INSERT INTO airport values (%s,%s)"
				cursor.execute(query,(name.upper(),city.upper()))
				print("here3")
				conn.commit()
				cursor.close()
				return render_template("add_new_airports.html",success = "Success: ",name = name.upper(), city = city.upper())
		except:
			return render_template("add_new_airports.html")
	except:
		return render_template("login.html", error="Bad Request")
	

@app.route('/airline_staff/<staff_email>/grant_permission', methods=["GET", "POST"])
def grant_permission(staff_email):
	try:
		if session['username'] != staff_email or session['status'] != "Admin":
			return render_template("login.html", error="Bad Request")
	except:
		return render_template("login.html", error="Bad Request")
	return render_template("grant_permission.html")


@app.route('/airline_staff/<staff_email>/add_booking_agents', methods=["GET", "POST"])
def add_booking_agents(staff_email):
	try:
		if session['username'] != staff_email or session['status'] != "Admin":
			return render_template("login.html", error="Bad Request")
	except:
		return render_template("login.html", error="Bad Request")
	return render_template("add_booking_agents.html")



@app.route("/airline_staff/view_customer/<username>/<flight_num>/<airline_name>",methods=["GET", "POST"])
def view_customer(flight_num, airline_name,username):	
	try:
		if session['username'] != username:
			print("case1")
			return render_template("login.html", error1="Bad Request: username does not match")
		cursor = conn.cursor()
		query = "select purchases.customer_email from ticket,purchases where ticket.airline_name = %s and ticket.flight_num  = %s and purchases.ticket_id = ticket.ticket_id"
		cursor.execute(query,(airline_name,flight_num))
		customer_lst = cursor.fetchall()
		cursor.close()
		print(customer_lst)
		return render_template("view_all_customer.html",airline_name = airline_name, flight_num = flight_num, customer = customer_lst)
	except:
	 	return render_template("login.html", error = "Bad Request")
	

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
