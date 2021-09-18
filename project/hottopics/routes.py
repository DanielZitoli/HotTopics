from flask import redirect, render_template, request, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, current_user, logout_user, login_required

from hottopics import app, db
from hottopics.models import Users, Posts, Favourites, Followers
from hottopics.forms import Registration, LoginForm


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect("/home")
    return render_template('index.html')
    

@app.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/home")

    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if not user:
            user = Users.query.filter_by(email=form.username.data).first()
        if user and check_password_hash(user.hash, form.password.data):
            login_user(user)
            return redirect("/home")
        else:
            flash("Login Unsuccessful, please check username/email and password", 'danger')
    return render_template("login.html", title="Login", form=form)
    
@app.route("/signup", methods=["GET","POST"])
def signup():
    if current_user.is_authenticated:
        return redirect("/home")

    form = Registration()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = Users(username=form.username.data, email=form.email.data, hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect("/home")
    return render_template("signup.html", title="Sign Up", form=form)

@app.route("/logout")
def logout():
    """Signs User Out"""
    logout_user()
    return redirect("/")




@app.route("/home")
@login_required
def home():
    return render_template("home.html", title="Home")

@app.route("/<username>")
@login_required
def account(username):
    return