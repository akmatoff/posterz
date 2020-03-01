from flask import Flask, render_template, flash, redirect, url_for, session, request
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import psycopg2
import psycopg2.extras
import settings
# import sqlite3

app = Flask(__name__)

# def dict_factory(cursor, row):
#     d = {}
#     for idx, col in enumerate(cursor.description):
#         d[col[0]] = row[idx]
#     return d

@app.route('/')
def index():
  return render_template('home.html')

@app.route('/about')
def about():
  return render_template('about.html')  

@app.route('/articles')
def articles():

  # con = sqlite3.connect('posterz.db')
  # con.row_factory = dict_factory
  con = psycopg2.connect("dbname=" + "'" + settings.DB_NAME + "'" + "user=" + "'" + settings.DB_USER + "'" + "host=" + "'" + settings.DB_HOST + "'" +  "password=" + "'" + settings.DB_PASSWORD + "'")
  cur = con.cursor(cursor_factory = psycopg2.extras.DictCursor)

  result = cur.execute("SELECT * FROM articles")

  articles = cur.fetchall()

  if len(articles) > 0:
    return render_template('articles.html', articles=articles)
  else:
    msg = "Статьи не найдены"
    return render_template('articles.html', msg=msg)

  cur.close()  

@app.route('/article/<string:id>/')
def article(id):
  # con = sqlite3.connect('posterz.db')
  # con.row_factory = dict_factory
  con = psycopg2.connect("dbname=" + "'" + settings.DB_NAME + "'" + "user=" + "'" + settings.DB_USER + "'" + "host=" + "'" + settings.DB_HOST + "'" +  "password=" + "'" + settings.DB_PASSWORD + "'")
  cur = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
  result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

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
    # with sqlite3.connect('posterz.db') as con:
    #   con.row_factory = dict_factory
    con = psycopg2.connect("dbname=" + "'" + settings.DB_NAME + "'" + "user=" + "'" + settings.DB_USER + "'" + "host=" + "'" + settings.DB_HOST + "'" +  "password=" + "'" + settings.DB_PASSWORD + "'")
    cur = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM users WHERE username = %s", [username])
    user = cur.fetchone()

    if username == user['username']:
      flash('Пользователь уже существует! Авторизуйтесь или выберите другое имя пользователя!')
    else:
      cur.execute("INSERT INTO users(first_name, last_name, username, email, password) VALUES(%s,%s,%s,%s,%s)", (first_name, last_name, username, email, password))
      # Commit to DB
      con.commit()

      flash('Поздравляем! Вы успешно прошли регистрацию!')
    return redirect(url_for('login'))

    cur.close()
  return render_template('register.html', form=form)  

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    # Get form fields
    username = request.form['username']
    password_c = request.form['password']

    # Create cursor
    # con = sqlite3.connect('posterz.db')
    # con.row_factory = dict_factory
    con = psycopg2.connect("dbname=" + "'" + settings.DB_NAME + "'" + "user=" + "'" + settings.DB_USER + "'" + "host=" + "'" + settings.DB_HOST + "'" +  "password=" + "'" + settings.DB_PASSWORD + "'")
    cur = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
    query = "SELECT count(*) FROM users WHERE username = %s"
    cur.execute(query, [username])
    count = int(cur.fetchone()[0])
    result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
    if count > 0:
      data = cur.fetchone()
      password = data['password']

      # Check if correct
      if sha256_crypt.verify(password_c, password):
        session['logged_in'] = True
        session['username'] = username

        flash('Вы успешно авторизовались')
        return redirect(url_for('dashboard'))  
        cur.close()
      else:
        error = 'Неверный логин или пароль!'
        return render_template('login.html', error=error) 

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
      flash('Вы не авторизованы, пожалуйста авторизуйтесь!')
      return redirect(url_for('login'))

  return wrap    

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():

  # con = sqlite3.connect('posterz.db')
  # con.row_factory = dict_factory
  con = psycopg2.connect("dbname=" + "'" + settings.DB_NAME + "'" + "user=" + "'" + settings.DB_USER + "'" + "host=" + "'" + settings.DB_HOST + "'" +  "password=" + "'" + settings.DB_PASSWORD + "'")
  cur = con.cursor(cursor_factory = psycopg2.extras.DictCursor)

  result = cur.execute("SELECT * FROM articles")

  articles = cur.fetchall()

  if len(articles) > 0:
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

    # con = sqlite3.connect('posterz.db')
    # con.row_factory = dict_factory
    con = psycopg2.connect("dbname=" + "'" + settings.DB_NAME + "'" + "user=" + "'" + settings.DB_USER + "'" + "host=" + "'" + settings.DB_HOST + "'" +  "password=" + "'" + settings.DB_PASSWORD + "'")
    cur = con.cursor(cursor_factory = psycopg2.extras.DictCursor)

    # Execute
    cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)",(title, body, session['username']))
    
    con.commit()
    cur.close()

    flash('Статья опубликована!')

    return redirect(url_for('dashboard'))

  return render_template('add_article.html', form=form) 

# Edit article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):

  # con = sqlite3.connect('posterz.db')
  # con.row_factory = dict_factory
  con = psycopg2.connect("dbname=" + "'" + settings.DB_NAME + "'" + "user=" + "'" + settings.DB_USER + "'" + "host=" + "'" + settings.DB_HOST + "'" +  "password=" + "'" + settings.DB_PASSWORD + "'")
  cur = con.cursor(cursor_factory = psycopg2.extras.DictCursor)

  # Get article by id
  result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

  article = cur.fetchone()

  form = ArticleForm(request.form)

  form.title.data = article['title']
  form.body.data = article['body'] 

  if request.method == 'POST' and form.validate():
    title = request.form['title']
    body = request.form['body']

    # con = sqlite3.connect('posterz.db')
    # con.row_factory = dict_factory
    con = psycopg2.connect("dbname=" + "'" + settings.DB_NAME + "'" + "user=" + "'" + settings.DB_USER + "'" + "host=" + "'" + settings.DB_HOST + "'" +  "password=" + "'" + settings.DB_PASSWORD + "'")
    cur = con.cursor(cursor_factory = psycopg2.extras.DictCursor)

    # Execute
    cur.execute("UPDATE articles SET title=%s, body=%s WHERE id = %s", (title, body, id))
    
    con.commit()
    cur.close()

    flash('Статья обновлена!', 'success')

    return redirect(url_for('dashboard'))

  return render_template('edit_article.html', form=form)   

# Delete article
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
  # con = sqlite3.connect('posterz.db')
  # con.row_factory = dict_factory
  con = psycopg2.connect("dbname=" + "'" + settings.DB_NAME + "'" + "user=" + "'" + settings.DB_USER + "'" + "host=" + "'" + settings.DB_HOST + "'" +  "password=" + "'" + settings.DB_PASSWORD + "'")
  cur = con.cursor(cursor_factory = psycopg2.extras.DictCursor)

  cur.execute("DELETE FROM articles WHERE id = %s", [id])

  con.commit()
  cur.close()

  flash('Статья удалена!')

  return redirect(url_for('dashboard'))

# Logout
@app.route('/logout')
@is_logged_in
def logout():
  session.clear()
  return redirect(url_for('login')) 

if __name__ == "__main__":
  app.secret_key = settings.SECRET_KEY
  app.run(debug=True) 