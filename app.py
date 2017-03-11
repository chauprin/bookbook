import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug import check_password_hash, generate_password_hash
import MySQLdb
from datetime import datetime

from flask import Flask

app=Flask(__name__)

db = MySQLdb.connect(host = "localhost", user = "root", passwd = "root", db="bookbook")

app.secret_key="This*is*th'e*secret*key"

@app.route('/')
def home():
	if not session.get('userid'):
		return render_template('index.html')

	else:
		return redirect(url_for('book'))


@app.route('/signup_page')
def signup_page():
	return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
	if request.method=='POST':

		first_name=request.form['first_name']
		last_name=request.form['last_name']
		email=request.form['email']
		password=str(generate_password_hash(request.form['password']))
		locality=request.form['locality']
		city=request.form['city']
		district=request.form['district']
		state=request.form['state']
		country=request.form['country']
		
		cursor=db.cursor()
		

		cursor.execute("select email from users;")
		emails_temp=list(cursor.fetchall())

		emails=[]

		for lis in emails_temp:
			emails.append(lis[0])

		
		if email in emails:
			flash("Email already registered")
			return redirect(url_for('signup_page'))	

		else:
			cursor.execute("insert into users(first_name, last_name, email, password, locality, city, district, state, country) values(%s,%s,%s,%s,%s,%s,%s,%s,%s);",[first_name, last_name, email, password, locality, city, district, state, country])
			db.commit()
			flash("Signup Successfull, Please login to continue")
			return redirect(url_for('home'))

	else:
		flash("Signup not successfull, Please try again")
		return redirect(url_for('signup_page'))


@app.route('/login_page')
def login_page():
	return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
		if request.form['email']=="admin" and request.form['password']=="adminpassword":
			session['admin']="prince"
			flash("Admin you have successfully logged in ")
			return redirect(url_for('admin_home_page'))
		else:
			cursor=db.cursor()	
			cursor.execute("select password from users where email=%s;", request.form['email'])
		
			row=cursor.fetchall()
		
			if not len(row):
				flash("User not registered !")
				return render_template('index.html')
		
			else:
				result=row[0][0].strip()
				if check_password_hash(result, request.form['password']):
				
					cursor.execute("select userid from users where email=%s;", request.form['email'])
					temp=cursor.fetchall()
					session['userid']=temp[0][0]
					return redirect('book')

				else:
					error="Wrong Password"
					flash(error)
					return render_template('login.html')

@app.route('/book')
def book():
	if not session.get('userid'):
		return render_template('index.html')
	else:
		cursor=db.cursor()
		cursor.execute("select * from agency_branches;")
		rows=cursor.fetchall()
		return render_template('book.html', rows=rows)

@app.route('/logout')
def logout():
	if not (session.get('userid')):
		flash("Not Logged in...")
		return redirect(url_for('home'))

	else:
		del session['userid']
		flash("You are successfully logged out")
		return render_template('index.html')


@app.route('/search_locations', methods=['POST'])
def search_locations():
	if not session.get('userid'):
		return render_template('index.html')
	else:
		if request.method=='POST':
			location=request.form['location']

			cursor=db.cursor()
			query="select * from agency_branches where locality like '%"+location+"%'or city like '%"+location+"%'or district like '%"+location+"%'or state like '%"+location+"%' or country like '%"+location+"%';"
			cursor.execute(query)

			rows=cursor.fetchall()
			return render_template('book.html', rows=rows)


@app.route('/booking_page/<int:branch_id>')
def booking_page(branch_id):
	if not session.get('userid'):
		return render_template('index.html')
	else:
		userid=session['userid']
		return render_template('booking.html',branch_id=branch_id,userid=userid)

@app.route('/booking', methods=['POST'])
def booking():
	if not session.get('userid'):
		return render_template('index.html')
	else:	
		if request.method=='POST':
			userid=request.form['userid']
			branch_id=request.form['branch_id']
			vehicle=request.form['vehicle']
			no_of_passengers=request.form['no_of_passengers']
			departure_date=request.form['departure_date']
			return_date=request.form['return_date']

			cursor=db.cursor()
			cursor.execute("insert into booking(userid, branch_id, no_of_passengers,vehicle, departure_date, return_date) values(%s,%s,%s,%s,%s,%s);",[userid,branch_id,no_of_passengers, vehicle,departure_date,return_date])
			db.commit()
			flash("successfully booked your journey")
			return redirect(url_for('home'))
		else:
			flash("Some problem occurred, Please try again")
			return redirect(url_for('book'))

@app.route('/profile')
def profile():
	if not session.get('userid'):
		return render_template('index.html')
	else:
		cursor=db.cursor()
		cursor.execute('select * from users where userid=%s;', session['userid'])
		users=cursor.fetchall()

		cursor.execute("select * from booking where userid=%s;",session['userid'])
		bookings=cursor.fetchall()

		return render_template("profile.html", users=users, bookings=bookings)

@app.route('/admin_home_page')
def admin_home_page():
	if not session.get('admin'):
		return redirect(url_for('home'))
	else:
		return render_template("admin_home_page.html")

@app.route('/admin_bookings_page')
def admin_bookings_page():
	if not session.get('admin'):
		return redirect(url_for('home'))
	else:
		cursor=db.cursor()
		cursor.execute("select * from booking;")
		bookings=cursor.fetchall()

		return render_template('admin_bookings_page.html', bookings=bookings)

@app.route('/admin_users_page')
def admin_users_page():
	if not session.get('admin'):
		return redirect(url_for('home'))
	else:
		cursor=db.cursor()
		cursor.execute("select * from users;")
		users=cursor.fetchall()

		return render_template('admin_users_page.html', users=users)

@app.route('/admin_add_branch_page')
def admin_add_branch_page():
	if not session.get('admin'):
		return redirect(url_for('home'))
	else:
		return render_template('admin_add_branch_page.html')

@app.route('/admin_add_branch', methods=['POST'])
def admin_add_branch():
	if not session.get('admin'):
		return redirect(url_for('home'))
	else:
		if request.method=='POST':
			locality=request.form['locality']
			city=request.form['city']
			district=request.form['district']
			state=request.form['state']
			country=request.form['country']

			cursor=db.cursor()
			cursor.execute("insert into agency_branches(locality, city, district, state, country) values(%s,%s,%s,%s,%s);",[locality, city, district, state, country])
			db.commit()

			flash("Branch successfully added")
			return redirect(url_for('admin_home_page'))
		else:
			flash("some problem occurred, please try again")
			return redirect(url_for('admin_home_page'))

if __name__=='__main__':
	app.run(debug=True)
