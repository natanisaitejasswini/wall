from flask import Flask, render_template, request, redirect, session, flash
import re
from datetime import datetime
from flask.ext.bcrypt import Bcrypt
from flask_bcrypt import Bcrypt
from mysqlconnection import MySQLConnector
app = Flask(__name__)
dbc = MySQLConnector(app, 'wall2')
# mysql = MySQLConnector(app, 'registration')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
bcrypt = Bcrypt(app)
app.secret_key= 'my_secret_key'


@app.route('/')
def index():
  return render_template('wall.html')

@app.route('/registration', methods=['POST'])
def register():
  print (50*"*")
  print request.form
  print 50*"*"
  error = True

  if(not request.form['first_name'] or not len(request.form['first_name']) >= 2):
    flash('Not a valid Firstname','error')
    error = False

  if(not request.form['last_name'] or not len(request.form['last_name']) >= 2):
    flash('Not a valid Lastname','error')
    error = False

  if not EMAIL_REGEX.match(request.form['email']):
    flash("hey, we have a invalid email",'error')
    error = False

  if len(request.form['password']) < 6:
    flash('Password cannot be less than 6 characters', 'error')
    error = False

  if (request.form['password']) != request.form['confirm_password']:
    flash('Passwords doesnt match', 'error')
    error = False
  if error == True:
    password = request.form['password']
    pw_hash = bcrypt.generate_password_hash(password)
    query = "INSERT INTO users(first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name,:email, :password, NOW(), NOW())"
    values = {
      'first_name': request.form['first_name'],
      'last_name': request.form['last_name'],
      'email': request.form['email'],
      'password': pw_hash, 
      'created_at': "NOW()",
      'updated_at': "NOW()"
    } 
    flash('Thank You for Registrating','success')
    dbc.query_db(query, values)
  return redirect('/')

@app.route('/login', methods=['POST'])
def login():
  email = request.form['email']
  password = request.form['password']
  print request.form['email']
  user_query = "SELECT * FROM users WHERE email = :email LIMIT 1"
  query_data = {'email' : email}
  user = dbc.query_db(user_query, query_data)
  print user
  if not user:
    flash('Please enter Valid Email','error')
    return redirect('/')
  if bcrypt.check_password_hash(user[0]['password'], password):
    session['user_id'] = user[0]['id']
    flash('User Matched','success')
    return redirect('/wall')
  else:
    flash('Your Login info did not match','error')
    return redirect('/')

@app.route('/wall')
def wallpost():
  name_query = "SELECT * FROM users"
  first_name = dbc.query_db(name_query)

  m_query = "SELECT users.first_name, users.last_name, messages.message, messages.created_at , messages.id FROM messages LEFT JOIN users ON messages.user_id = users.id ORDER BY created_at DESC"
  message = dbc.query_db(m_query)
  
  n_query = "SELECT users.first_name, users.last_name, messages.message, messages.created_at, comments.message_id, messages.id, comments.comment, comments.created_at, comments.id  FROM comments, users, messages WHERE comments.message_id = messages.id AND comments.user_id = users.id"
  comment = dbc.query_db(n_query)
 
  session['message_id'] = message[0]['id']
  return render_template('wallsucess.html', all_messages= message, comment_messages= comment, all_names= first_name)

@app.route('/message', methods = ['POST'])
def message():
  i_query = "INSERT INTO messages(message, created_at, updated_at, user_id) VALUES (:message1, NOW(), NOW(), :id)"
  data1 = {
  'id' : session['user_id'],
  'message1' : request.form['message']
  }
  print 50*'*'
  dbc.query_db(i_query,data1)
  return redirect('/wall')

@app.route("/comment", methods = ['POST'])
def comment():
  c_query = "INSERT INTO comments(comment, created_at, updated_at, message_id, user_id) VALUES (:add_comment, NOW(), NOW(), :m, :id)"
  data2 = {
    'id': session['user_id'],
    'add_comment': request.form['add_comment'],
    'm': request.form['comments_add']
  }
  dbc.query_db(c_query,data2)
  return redirect('/wall')

@app.route('/remove_message', methods=['POST'])
def delete():
  # DELETE QUERIES
    c_query = "DELETE FROM comments WHERE message_id = :message_id and created_at > NOW() - INTERVAL 30 MINUTE"
    d_query = "DELETE FROM messages WHERE id = :message_id and created_at > NOW() - INTERVAL 30 MINUTE"
    data = {'message_id': request.form['delete_message']}
    dbc.query_db(c_query, data)
    dbc.query_db(d_query, data)
    return redirect('/wall')

@app.route('/wallcomment')
def wallcomment():
  return redirect('/')
app.run(debug=True)








