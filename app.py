from flask import Flask, render_template, flash, redirect, url_for, session, request
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from passlib.hash import sha256_crypt
from functools import wraps
import settings
import sqlite3
import os

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = settings.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = settings.MAIL_PASSWORD
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

secret = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
mail = Mail(app)

# con = sqlite3.connect('posterz.db')
# cur = con.cursor()
# cur.execute("")
# con.commit()
# cur.close()

# Save picture from user input
def save_pic(form_pic):
  if 'username' in session:
    filename = session['username']
  else:
    filename = request.form['username']
  _, file_extension = os.path.splitext(form_pic.filename)
  pic_filename = filename + file_extension
  pic_path = os.path.join(app.root_path, 'static/profile_pics', pic_filename)
  form_pic.save(pic_path)

  return pic_filename

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

    pic_file = request.files.get('profile-pic')

    profile_pic = save_pic(pic_file)

    token = secret.dumps(email, salt="email-confirm")

    msg = Message('Подтверждение почты', sender="noreply@posterz.com", recipients=[email])

    link = url_for('confirm_email', token=token, _external=True)

    msg.body = """
    Подтвердите почту по данной ссылке:
    {}

    Если это не вы, то проигнорируйте данное сообщение.
    """.format(link)

    mail.send(msg)

    if confirm == password:
      # Create cursor
      con = sqlite3.connect('posterz.db')
      cur = con.cursor()
      
      cur.execute("SELECT COUNT(*) FROM users WHERE username = ?", [username])
      user = cur.fetchone()[0]

      if user > 0:
        flash('Пользователь уже существует! Авторизуйтесь или выберите другое имя пользователя!')
      else:
        cur.execute("INSERT INTO users(first_name, last_name, username, email, password, profile_pic, active) VALUES(?,?,?,?,?,?, 0)", (first_name, last_name, username, email, password_crypt, profile_pic))

        # Commit to DB
        con.commit()

        flash('Поздравляем! Вы успешно прошли регистрацию!')
    else:  
      error = 'Пароли не совпадают, попробуйте еще раз!'
      return render_template('register.html', error=error)

    flash('На вашу почту отправлена ссылка для подтверждения')
    return redirect(url_for('login'))

    cur.close()
  return render_template('register.html')  

# Email confirmation page
@app.route('/confirm_email/<token>')  
def confirm_email(token):
  try:
    email = secret.loads(token, salt="email-confirm", max_age=1200)
    
    con = sqlite3.connect('posterz.db')
    cur = con.cursor()
    cur.execute("UPDATE users SET active=1 WHERE email=?", [email])
    con.commit()
    cur.close()

  except SignatureExpired:
    error = 'Ссылка недействительна или просрочена!'
    return redirect(url_for('register', error=error))

  flash('Вы успешно активировали аккаунт!')
  return render_template('dashboard.html')  

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

      if data['active'] == 1:

        # Check if correct
        if sha256_crypt.verify(password, password_db):
          session['logged_in'] = True
          session['username'] = username
          session['email'] = data['email']
          session['profile_pic'] = data['profile_pic']

          flash('Вы успешно авторизовались')
          return redirect(url_for('dashboard'))  
        else:
          error = 'Неверный логин или пароль!'
          return render_template('login.html', error=error)
      else:
        flash('Ваш аккаунт не активирован! Сначала подтвердите почту!')
        return render_template('register.html')     

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

# Profile page
@app.route('/profile', methods=['GET', 'POST'])
@is_logged_in
def profile():
  con = sqlite3.connect('posterz.db')
  con.row_factory = sqlite3.Row
  cur = con.cursor()
  cur.execute("SELECT * FROM users WHERE username = ?", [session['username']])

  user = cur.fetchone()

  if request.method == 'POST':
    pic_file = request.files.get('profile-pic')
    profile_pic = save_pic(pic_file)

    cur.execute("UPDATE users SET profile_pic = ? WHERE username = ?", (profile_pic, session['username']))
    con.commit()
    cur.close()

    flash('Ваша фотография успешно обновлена!')
    
    return redirect(url_for('profile'))
  return render_template('profile.html', user=user)

# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@is_logged_in
def dashboard():

  con = sqlite3.connect('posterz.db')
  con.row_factory = sqlite3.Row
  cur = con.cursor()

  cur.execute("SELECT * FROM articles WHERE author = ?", [session['username']])

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