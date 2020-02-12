from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import sqlite3
from data import Articles

app = Flask(__name__)
Articles = Articles()

# con = sqlite3.connect('posterz.db')
# con.row_factory = sqlite3.Row
# con.close()

@app.route('/')
def index():
  return render_template('home.html')

@app.route('/about')
def about():
  return render_template('about.html')  

@app.route('/articles')
def articles():
  return render_template('articles.html', articles=Articles)

@app.route('/article/<string:id>/')
def article(id):
  return render_template('article.html', id=id)

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
    password_en = request.form['password']

    # Create cursor
    with sqlite3.connect('posterz.db') as con:
      cur = con.cursor()
      result = cur.execute("SELECT * FROM users WHERE username = ?", [username])

      if result > 0:
        data = cur.fetchone()
        password = data['password']

        # Check if correct
        if sha256_crypt.verify(password_en, password):
          app.logger.info('Пароли совпадают')
        else:
          app.logger.info('Пароли не совпадают')
        return redirect(url_for('index'))
      else:
        app.logger.info('Пользователь не существует')      

  return render_template('login.html')

if __name__ == "__main__":
  app.secret_key = '1337228133722800001526'
  app.run(host='0.0.0.0', debug=True)  