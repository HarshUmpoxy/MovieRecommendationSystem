# from crypt import methods
from flask import Flask,render_template,request,redirect,session,jsonify
import os,requests,pickle
from flask_mysqldb import MySQL
import MySQLdb.cursors
import pandas as pd,re
import random

import urllib3
urllib3.disable_warnings()

from dotenv import load_dotenv
load_dotenv()

PASSWORD=os.getenv("PASSWORD")

app=Flask(__name__)
app.secret_key=os.urandom(24)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = PASSWORD
app.config['MYSQL_DB'] = 'userdata'

mysql = MySQL(app)

def fetch_poster(movie_id):
    try:
        response= requests.get('https://api.themoviedb.org/3/movie/{}?api_key=c70f1dc5636cb5108f116ff14060f29f&language=en-US'.format(movie_id),verify=False)
        data=response.json()
        return "https://image.tmdb.org/t/p/original"+data['poster_path']
    except requests.exceptions.RequestException as e:
        return ""

def recommend(movie): 
    movie_index=movies[movies['title']==movie].index[0]
    distances=similarity[movie_index]
    movies_list=sorted(list(enumerate(distances)),reverse=True,key=lambda x:x[1])[1:6]
    recommended_movies=[]
    recommended_movies_posters=[]
    for i in movies_list:
        movie_id=movies.iloc[i[0]].movie_id
        recommended_movies.append((movies.iloc[i[0]].title))
        recommended_movies_posters.append(fetch_poster(movie_id))
    return zip(recommended_movies,recommended_movies_posters)


file = open(r"C:\Users\HARSH KUMAR\Desktop\Flask_Login_System\Python\movie_dict.pkl", 'rb')
movies_dict=pickle.load(file)
movies= pd.DataFrame(movies_dict)

file1 = open(r"C:\Users\HARSH KUMAR\Desktop\Flask_Login_System\Python\similarity.pkl", 'rb')

similarity=pickle.load(file1)


@app.route('/')
def login():    
    return render_template('login.html')

@app.route('/register')
def about():
    return render_template('register.html')

@app.route('/home')
def home():
    if 'user_id' in session:
        return render_template('home.html')
    else:
        redirect('/')


@app.route('/login_validation',methods=['POST'])
def login_validation():
    user_id=random.getrandbits(32)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = % s AND password = % s', (email, password, ))
        account = cursor.fetchone()
        if account:
            session['user_id'] = account['user_id']
            
            return redirect('/recommend_engine')
        else:
            return redirect('/')

file = open(r"C:\Users\HARSH KUMAR\Desktop\Flask_Login_System\Python\movie_dict.pkl", 'rb')
movies_dict=pickle.load(file)
movies= pd.DataFrame(movies_dict)

file1 = open(r"C:\Users\HARSH KUMAR\Desktop\Flask_Login_System\Python\similarity.pkl", 'rb')

similarity=pickle.load(file1)


@app.route('/recommend_engine',methods=['GET','POST'],)
def recommendengine():
    if request.method == "GET":
        return render_template('home.html', m=movies['title'])
    elif request.method == "POST":
        moviev = request.form['movie']
        a = recommend(moviev)
        return render_template('results.html', name = a)      
       

 

@app.route('/add_user',methods=['POST'])
def add_user():
    
    if request.method == 'POST' and 'uname' in request.form and 'upassword' in request.form and 'uemail' in request.form :
        username = request.form['uname']
        password = request.form['upassword']
        email = request.form['uemail']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not username or not password or not email:
            pass
        else:
            cursor.execute('INSERT INTO users VALUES (NULL, % s, % s, % s)', (username, email, password, ))
            mysql.connection.commit()
            cursor.execute('SELECT * FROM users WHERE email = % s', (email, ))
            uaccount = cursor.fetchone()
            session['user_id']=uaccount['user_id']
            return redirect('/recommend_engine')
    elif request.method == 'POST':
        pass
        return render_template('register.html')

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/')

if __name__=="__main__":
    app.run(debug=True)


