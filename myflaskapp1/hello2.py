from flask import Flask, flash, redirect, url_for, session, logging
from flask import render_template
#from data import Articles
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from flask import request
import MySQLdb, MySQLdb.cursors 
import gc
from functools import wraps
app = Flask(__name__)
app.secret_key='secret123'

#config MySQL
def connection():
    conn = MySQLdb.connect(host="localhost",
                           user = "root",
                           passwd = "",
                           db = "myflaskapp",
                           cursorclass = MySQLdb.cursors.DictCursor
                          )

   
    c = conn.cursor()
   

    return c, conn

#Init MySQL


#Articles = Articles()

@app.route('/articles')
def articles():
	c, conn = connection()

	result = c.execute("SELECT * FROM articles")

	articles = c.fetchall()

	if result > 0:
		return render_template("articles.html", articles=articles)

	else:
		msg = 'No Articles Found'
		return render_template("articles.html", msg=msg)

	c.close()
	
 
@app.route('/article/<string:id>/')
def article(id):
	c , conn = connection()

	result = c.execute("SELECT * FROM articles WHERE id = %s", [id])

	article = c.fetchone()


	return render_template('article.html', article=article)

@app.route('/')
def webprint():
    return render_template('home.html') 

@app.route('/about')
def abou():
	return render_template("about.html")





class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	username = StringField('Username', [validators.Length(min=4, max=25)])
	email = StringField('Email', [validators.Length(min=6, max=50)])
	password = PasswordField('Password', [
		validators.DataRequired(),
	validators.EqualTo('confirm', message='Passwords do not match')
	])
	confirm = PasswordField('Confirm Password')
    

@app.route('/register', methods=["GET","POST"])
def register_page():
    try:
        form = RegisterForm(request.form)

        if request.method == "POST" and form.validate():
        	name = form.name.data
        	email = form.email.data
        	username = form.username.data
        	password = sha256_crypt.encrypt(str(form.password.data))
        	c, conn = connection()
        	

        
        	c.execute("INSERT INTO users (name, email, username, password) VALUES (%s, %s, %s, %s)", (name, email, username, password))
        	conn.commit()

        	flash("Thanks for registering!")

        	c.close()

        	conn.close()

        	gc.collect()
        	session['logged_in'] = True

        	session['username'] = username

        	



   
        return render_template("register.html", form=form)

    except Exception as e:
        return(str(e))  



#User login
@app.route('/login', methods=['GET', 'POST'])
def login():
	error =''
	
	c, conn = connection()
	if request.method == "POST":

		username = request.form['username']
		password_candidate = request.form['password']

        
		result = c.execute("SELECT * FROM users WHERE username = (%s)", [username])

		if result > 0:



		    data = c.fetchone()
		    password = data['password']
		   

		    if sha256_crypt.verify(password_candidate, password):

		    	session['logged_in'] = True

		    	session['username'] = username

		    	flash("You are now logged in", 'success')

		    	return redirect(url_for("dashboard"))

		    else:
		    	error = 'Invalid login'
		    	return render_template('login.html', error=error)
		    c.close()
            

		else:
				error = "Username not found"
				return render_template('login.html', error=error)


	return render_template("login.html", error=error)

def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorised, Please login', 'success')
			return redirect(url_for('login'))
	return wrap


@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash('You are now logged out', 'success')
	return redirect(url_for('login'))
	 


@app.route('/dashboard')
@is_logged_in
def dashboard():

	c, conn = connection()

	result = c.execute("SELECT * FROM articles")

	articles = c.fetchall()

	if result > 0:
		return render_template("dashboard.html", articles=articles)

	else:
		msg = 'No Articles Found'
		return render_template("dashboard.html", msg=msg)

	c.close()

	
     
       
 



class ArticleForm(Form):
	title = StringField('Title', [validators.Length(min=1, max=200)])
	body = TextAreaField('Body', [validators.Length(min=30)])
	

@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
	
		form = ArticleForm(request.form)
		if request.method == 'POST' and form.validate():
			title = form.title.data

			body = form.body.data

			c, conn = connection()

			c.execute ("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)", (title, body, session['username']))
			conn.commit()

			flash("Article Created", 'success')

			c.close()

			conn.close()

			return redirect(url_for('dashboard'))

		return render_template('add_article.html', form=form)
	  

#Edit Article		
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
	#Create cursor
	c, conn = connection()

	#get article by id
	result = c.execute("SELECT * FROM articles WHERE id = %s", [id])

	article = c.fetchone()


	form = ArticleForm(request.form)


	#Populate article form fields
	form.title.data = article['title']
	form.body.data = article['body']


	if request.method == 'POST' and form.validate():
		title = request.form['title']

		body = request.form['body']

		c, conn = connection()

		c.execute ("UPDATE articles SET title=%s, body=%s WHERE id=%s", (title, body, id))
		conn.commit()

		flash("Article Updated", 'success')

		c.close()

		conn.close()

		return redirect(url_for('dashboard'))

	return render_template('edit_article.html', form=form)


	    	
		   
#Delete Article
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
	c, conn = connection()

	c.execute("DELETE FROM articles WHERE id = %s", [id])

	conn.commit()

	c.close()

	flash("Article Deleted", 'success')

	return redirect(url_for('dashboard'))
		    


		   

		   

		    

		    

		    

	

		

	
        


   


	


        
       


         