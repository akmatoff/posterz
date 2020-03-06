from flask import Flask, render_template, flash, redirect, url_for, session, request
from passlib.hash import sha256_crypt
from functools import wraps
import settings
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('home.html')

@app.route('/about')
def about():
  return render_template('home.html')  

@app.route('/articles')
def articles():

  con = sqlite3.connect('posterz.db')
  con.row_factory = sqlite3.Row
  cur = con.cursor()
  cur.execute("SELECT * FROM articles")

  articles = cur.fetchall()

  if len(articles) > 0:
    return render_template('articles.html', articles=articles)
  else:
    msg = "Статьи не найдены"
    return render_template('articles.html', msg=msg)

  cur.close()  

@app.route('/article/<string:id>/')
def article(id):
  con = sqlite3.connect('posterz.db')
  con.row_factory = sqlite3.Row
  cur = con.cursor()
  cur.execute("SELECT * FROM articles WHERE id = ?", [id])

  article = cur.fetchone()
  return render_template('article.html', article=article)

@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    first_name = request.form['first-name']
    last_name = request.form['last-name']
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    password_crypt = sha256_crypt.encrypt(str(request.form['password']))
    confirm = request.form['confirm']

    if confirm == password:
      # Create cursor
      con = sqlite3.connect('posterz.db')
      cur = con.cursor()
      
      cur.execute("SELECT COUNT(*) FROM users WHERE username = ?", [username])
      user = cur.fetchone()[0]

      if user > 0:
        flash('Пользователь уже существует! Авторизуйтесь или выберите другое имя пользователя!')
      else:
        cur.execute("INSERT INTO users(first_name, last_name, username, email, password) VALUES(?,?,?,?,?)", (first_name, last_name, username, email, password_crypt))
        # Commit to DB
        con.commit()

        flash('Поздравляем! Вы успешно прошли регистрацию!')
    else:  
      error = 'Пароли не совпадают, попробуйте еще раз!'
      return render_template('register.html', error=error)

    return redirect(url_for('login'))

    cur.close()
  return render_template('register.html')  

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    # Get form fields
    username = request.form['username']
    password = request.form['password']

    # Create cursor
    con = sqlite3.connect('posterz.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE username = ?", [username])
    count = cur.fetchone()[0]
    
    if count > 0:
      cur.execute("SELECT * FROM users WHERE username = ?", [username])
      data = cur.fetchone()
      
      password_db = data['password']

      # Check if correct
      if sha256_crypt.verify(password, password_db):
        session['logged_in'] = True
        session['username'] = username

        flash('Вы успешно авторизовались')
        return redirect(url_for('dashboard'))  
      else:
        error = 'Неверный логин или пароль!'
        return render_template('login.html', error=error) 

    else:
      error = 'Пользователь не найден'
      return render_template('login.html', error=error) 
    cur.close()    

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
@app.route('/dashboard', methods=['GET', 'POST'])
@is_logged_in
def dashboard():

  con = sqlite3.connect('posterz.db')
  con.row_factory = sqlite3.Row
  cur = con.cursor()

  cur.execute("SELECT * FROM articles")

  articles = cur.fetchall()

  if len(articles) > 0:
    return render_template('dashboard.html', articles=articles)
  else:  
    msg = 'У вас еще нет статьей.'
    return render_template('dashboard.html', msg=msg)  

# Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
  if request.method == 'POST':
    cover = request.form['cover']
    title = request.form['title']
    body = request.form['body']

    con = sqlite3.connect('posterz.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # Execute
    cur.execute("INSERT INTO articles(cover, title, body, author) VALUES(?, ?, ?, ?)",(cover, title, body, session['username']))
    
    con.commit()
    cur.close()

    flash('Статья опубликована!')

    return redirect(url_for('dashboard'))

  return render_template('add_article.html') 

# Edit article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):

  con = sqlite3.connect('posterz.db')
  con.row_factory = sqlite3.Row
  cur = con.cursor()
  
  # Get article by id
  cur.execute("SELECT * FROM articles WHERE id = ?", [id])

  article = cur.fetchone()

  cover_db = article['cover']
  title_db = article['title']
  body_db = article['body']

  if request.method == 'POST':
    cover = request.form['cover']
    title = request.form['title']
    body = request.form['body']

    con = sqlite3.connect('posterz.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    # Execute
    cur.execute("UPDATE articles SET cover=?, title=?, body=? WHERE id = ?", (cover, title, body, id))
    
    con.commit()
    cur.close()

    flash('Статья обновлена!')

    return redirect(url_for('dashboard'))

  return render_template('edit_article.html', cover_db=cover_db, title_db=title_db, body_db=body_db)   

# Delete article
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
  con = sqlite3.connect('posterz.db')
  con.row_factory = sqlite3.Row
  cur = con.cursor()
  cur.execute("DELETE FROM articles WHERE id = ?", [id])

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
  app.run(host='0.0.0.0', debug=True) 