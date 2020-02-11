from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import sqlite3
from data import Articles

app = Flask(__name__)
Articles = Articles()

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
  username = StringField('Никнейм', [validators.Length(min=4, max=30)])
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

if __name__ == "__main__":
  app.secret_key = '1337228133722800001526'
  app.run(debug=True)  