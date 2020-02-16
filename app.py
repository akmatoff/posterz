from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import sqlite3
from data import Articles

app = Flask(__name__)
Articles = Articles()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.route('/')
def index():
  return render_template('home.html')

@app.route('/about')
def about():
  return render_template('about.html')  

@app.route('/articles')
def articles():

  con = sqlite3.connect('posterz.db')
  con.row_factory = dict_factory
  cur = con.cursor()

  result = cur.execute("SELECT * FROM articles")

  articles = cur.fetchall()

  if articles != None:
    return render_template('articles.html', articles=articles)
  else:
    msg = "Статьи не найдены"
    return render_template('articles.html', msg=msg)

  cur.close()  

@app.route('/article/<string:id>/')
def article(id):
  con = sqlite3.connect('posterz.db')
  con.row_factory = dict_factory
  cur = con.cursor()
  result = cur.execute("SELECT * FROM articles WHERE id = ?", [id])

  article = cur.fetchone()
  return render_template('article.html', article=article)

class RegisterForm(Form):
  first_name = StringField('Имя', [validators.Length(min=1, max=80)])
  last_name = StringField('Фамилия', [validators.Length(min=1, max=80)])
  username = StringField('Имя пользователя', [validators.Length(min=4, max=30)])
  email = StringField('Email', [validators.Length(min=6, max=50)])
  password = PasswordField('Пароль', [
    validators.DataRequired(),
    validators.EqualTo('confirm', message='Пароли не совпадают')
  ])
  confirm = PasswordField('Подтвердите пароль')

@app.route('/register', methods=['GET', 'POST'])
def register():
  form = RegisterForm(request.form)  
  if request.method == 'POST' and form.validate():
    first_name = form.first_name.data
    last_name = form.last_name.data
    username = form.username.data
    email = form.email.data
    password = sha256_crypt.encrypt(str(form.password.data))

    # Create cursor
    with sqlite3.connect('posterz.db') as con:
      con.row_factory = dict_factory
      cur = con.cursor()
      cur.execute("INSERT INTO users(first_name, last_name, username, email, password) VALUES(?,?,?,?,?)", (first_name, last_name, username, email, password))

      # Commit to DB
      con.commit()

    flash('Поздравляем! Вы успешно прошли регистрацию!', 'success')
    return redirect(url_for('login'))


  return render_template('register.html', form=form)  

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    # Get form fields
    username = request.form['username']
    password_c = request.form['password']

    # Create cursor
    con = sqlite3.connect('posterz.db')
    con.row_factory = dict_factory
    cur = con.cursor()
    result = cur.execute("SELECT * FROM users WHERE username = ?", [username])
    if result != None:
      data = cur.fetchone()
      password = data['password']

      # Check if correct
      if sha256_crypt.verify(password_c, password):
        session['logged_in'] = True
        session['username'] = username

        flash('Вы успешно авторизовались', 'success')
        return redirect(url_for('dashboard'))  
      else:
        error = 'Неверный логин или пароль!'
        return render_template('login.html', error=error) 

      cur.close()  
    else:
      error = 'Пользователь не найден'
      return render_template('login.html', error=error) 

  return render_template('login.html')

def is_logged_in(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if 'logged_in' in session:
      return f(*args, **kwargs)
    else:
      flash('Вы не авторизованы, пожалуйста авторизуйтесь!', 'danger')
      return redirect(url_for('login'))

  return wrap    

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():

  con = sqlite3.connect('posterz.db')
  con.row_factory = dict_factory
  cur = con.cursor()

  result = cur.execute("SELECT * FROM articles")

  articles = cur.fetchall()

  if articles != None:
    return render_template('dashboard.html', articles=articles)
  else:  
    msg = 'У вас еще нет статьей.'
    return render_template('dashboard.html', msg=msg)  

# Article form class
class ArticleForm(Form):
  title = StringField('Название', [validators.Length(min=1, max=250)])
  body = TextAreaField('Статья', [validators.Length(min=30)])

# Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
  form = ArticleForm(request.form)
  if request.method == 'POST' and form.validate():
    title = form.title.data
    body = form.body.data

    con = sqlite3.connect('posterz.db')
    con.row_factory = dict_factory
    cur = con.cursor()

    # Execute
    cur.execute("INSERT INTO articles(title, body, author) VALUES(?, ?, ?)",(title, body, session['username']))
    
    con.commit()
    cur.close()

    flash('Статья опубликована!', 'success')

    return redirect(url_for('dashboard'))

  return render_template('add_article.html', form=form) 

# Logout
@app.route('/logout')
@is_logged_in
def logout():
  session.clear()
  return redirect(url_for('login')) 

if __name__ == "__main__":
  app.secret_key = '1337228133722800001526'
  app.run(debug=True) 