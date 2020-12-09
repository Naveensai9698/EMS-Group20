from flask import Flask,render_template, flash, redirect , url_for , session ,request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField , TextAreaField ,PasswordField , validators
from passlib.hash import sha256_crypt
from functools import wraps


app = Flask(__name__)
app.debug = True


#Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
#init MYSQL
mysql = MySQL(app)


#Articles = Articles()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():

        #create cursor
        cur = mysql.connection.cursor()

        #get articles
        result = cur.execute("SELECT * FROM articles")

        articles = cur.fetchall()

        if result > 0:
            return render_template('articles.html',articles=articles)
        else:
            msg = 'No Employees Found'
            return render_template('articles.html',msg=msg)
        #close connection
        cur.close()



@app.route('/article/<string:id>/')
def article(id):

    #create cursor
    cur = mysql.connection.cursor()

    #get article
    result = cur.execute("SELECT * FROM articles WHERE id = %s",[id])
    #result = cur.execute("SELECT * FROM articles")

    article = cur.fetchone()

    return render_template('article.html',article=article)


class RegisterForm(Form):
    name = StringField('Name',[validators.Length(min=1,max=50)])
    username = StringField('Username',[validators.Length(min=4,max=25)])
    email = StringField('Email',[validators.Length(min=4,max=25)])
    password = PasswordField('Password', [ validators.DataRequired (),validators.EqualTo('confirm',message ='passwords do not match')])
    confirm = PasswordField('Confirm password')

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        #password = sha256_crypt.encrypt(str(form.password.data))
        password = str(form.password.data)

        # Create crusor
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO users(name,email,username,password) VALUES(%s,%s,%s,%s)",(name,email,username,password))

        # commit to DB
        mysql.connection.commit()
        #close connection
        cur.close()

        flash("You are now Registered and you can login" , 'success')

        redirect(url_for('login'))
    return render_template('register.html',form=form)

# user login
@app.route('/login',methods =['GET','POST'])
def login():
    if request.method == 'POST':
        #Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor

        cur = mysql.connection.cursor()

        #Get user by username

        result = cur.execute("SELECT * FROM users WHERE username = %s" ,[username])

        if result > 0:
        # Get Stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            #if sha256_crypt.verify(password_candidate,password):
            if password==password_candidate:
                #Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in ','success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Username not found'
                return render_template('login.html',error=error)
                #close connection
            cur.close()

        else:
            error = 'Username not found'
            return render_template('login.html',error=error)

    return render_template('login.html')

#check if user logged in

def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, please login','danger')
            return redirect(url_for('login'))
    return wrap



#logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('you are now logged out ','success')
    return redirect(url_for('login'))
# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():

    #create cursor
    cur = mysql.connection.cursor()
    #result=0
    #get articles
    result = cur.execute("SELECT * FROM articles")

    articles = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html',articles=articles)
    else:
        msg = 'No Details Found'
        return render_template('dashboard.html',msg=msg)
    #close connection
    cur.close()


	
class ArticleForm(Form):
    title = StringField('Employee Name',[validators.Length(min=1,max=50)])
    body = TextAreaField('Designation',[validators.Length(min=1,max=50)])
    author = StringField('Department',[validators.Length(min=1,max=50)])
    phone = StringField('Phone',[validators.Length(min=1,max=50)])
    email = StringField('Email',[validators.Length(min=1,max=50)])
    experience = StringField('Experience',[validators.Length(min=1,max=50)])
    salary = StringField('Salary',[validators.Length(min=1,max=50)])
    address = StringField('Address',[validators.Length(min=1,max=50)])


#Add Article

@app.route('/add_article', methods=['GET','POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        author=form.author.data
        phone=form.phone.data
        email=form.email.data
        experience=form.experience.data
        salary=form.salary.data
        address=form.address.data
        
        # Create a cursor

        cur = mysql.connection.cursor()

        #execute

        cur.execute("INSERT INTO articles(title,body,author,phone,email,experience,salary,address) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",(title, body, author, phone, email, experience, salary, address))

        #commit to db

        mysql.connection.commit()

        #close connection
        cur.close()

        flash('created ','success')

        return redirect(url_for('dashboard'))

    return render_template('add_article.html',form=form)

#Edit Article

@app.route('/edit_article/<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_article(id):
    # Create cursor
    cur = mysql.connection.cursor()
    #get article by id
    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = cur.fetchone()

    #get form
    form = ArticleForm(request.form)

    #populate article form fields
    form.title.data = article['title']
    form.body.data = article['body']
    form.author.data = article['author']
    form.phone.data = article['phone']
    form.email.data = article['email']
    form.experience.data = article['experience']
    form.salary.data = article['salary']
    form.address.data = article['address']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']
        author = article['author']
        phone = request.form['phone']
        email = request.form['email']
        experience = request.form['experience']
        salary = request.form['salary']
        address = request.form['address']

        # Create a cursor

        cur = mysql.connection.cursor()

        #execute

        cur.execute("UPDATE articles SET title=%s, body=%s, phone=%s, email=%s, experience=%s, salary=%s, address=%s WHERE id = %s" , (title,body,phone, email, experience, salary, address,id))

        #commit to db

        mysql.connection.commit()

        #close connection
        cur.close()

        flash('Updated ','success')

        return redirect(url_for('dashboard'))

    return render_template('edit_article.html',form=form)

#Delete article
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    #Execute
    cur.execute("DELETE FROM articles WHERE id = %s",[id])

    #Commit to DB

    mysql.connection.commit()
    #close connection

    cur.close()

    flash('Deleted  ','success')

    return redirect(url_for('dashboard'))



if __name__ =='__main__':
    app.secret_key='secret123'
    app.run()
