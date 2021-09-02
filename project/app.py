import os

from flask import Flask, redirect, render_template, request, session, flash
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, apology
from forms import Registration, LoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = '055a23834110d872426d5f7ee0ac198a'

ENV = 'dev'
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost/hottopics'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.Text())
    hash = db.Column(db.Text(), nullable=False)
    joined = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Posts', backref='post-author', lazy=True)

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    agrees = db.Column(db.Integer, nullable=False, default=0)
    disagrees = db.Column(db.Integer, nullable=False, default=0)
    comments = db.relationship('Comments', backref='comment-post', lazy=True) 
    posted = db.Column(db.DateTime, default=datetime.utcnow)

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    author = db.Column(db.Integer, nullable=False)
    post = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    posted = db.Column(db.DateTime, default=datetime.utcnow)

class Followers(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    follower = db.Column(db.Integer) 
    following = db.Column(db.Integer) 

class Favourites(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    user = db.Column(db.Integer)
    post = db.Column(db.Integer)
        

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configs cookies to be stored in computer's harddrive, and to not last permanently
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

@app.route("/")
def index():
    if session.get("user_id") is None:
        return render_template('index.html')
    return redirect("/home") 

@app.route("/login", methods=["GET","POST"])
def login():
    # forgets user info
    session.clear()

    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password") 

        # checks for user error
        if not name or not password:
            return apology("Missing Fields")

        # selects user with name/email user submitted
        user = Users.query.filter(Users.username == name or Users.email == name).first()
        print(user)

        # checks that username exists and password matches hash
        if not user or not check_password_hash(user.hash, password):
            return apology("Invalid Username and/or Password")

        # remembers user
        session["user_id"] = user.id

        return redirect("/home")
        
    else:
        return render_template("login.html")
    
@app.route("/signup", methods=["GET","POST"])
def signup():
    """Signs user up and inserts into database"""
    if request.method == "POST":
        name = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password") 
        confirm = request.form.get("confirmation") 

        # checks for mistakes in user input
        if not name or not email or not password or not confirm:
            return apology("Missing fields")
        elif password != confirm:
            return apology("Passwords do not match")
        
        # gets list of users with same name or email as the ones entered
        rows = Users.query.filter(Users.username==name or Users.email == email or Users.email == name).all()

        if rows:
            for row in rows:
                if row.email == email:
                    return apology("Email already in use")
            return apology("Username already in use")

        #TODO
        # email confirmation
        
        # generates hash for password and enters user into the database
        hash = generate_password_hash(password)
        user = Users(username=name, email=email, hash=hash)
        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id

        print(user.joined)
        return redirect("/home")
    else:
        return render_template("signup.html")


@app.route("/logout")
def logout():
    """Signs User Out"""

    # forgets all user info
    session.clear()

    return redirect("/")




@app.route("/home")
@login_required
def home():
    return render_template("home.html")

@app.route("/<username>")
@login_required
def account(username):
    return

