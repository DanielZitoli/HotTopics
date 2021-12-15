from operator import pos
import secrets
import os
from PIL import Image
from flask import redirect, render_template, request, flash, jsonify
from flask.helpers import url_for
from sqlalchemy.orm import query
from sqlalchemy.orm.session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime

from hottopics import app, db
from hottopics.models import Users, Posts, Comments, Favourites, Follows
from hottopics.forms import Registration, LoginForm, UpdateAccount, CreatePost
from hottopics.helpers import display_date


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
@login_required
def logout():
    """Signs User Out"""
    logout_user()
    return redirect("/")




@app.route("/home")
@login_required
def home():
    query = Posts.query.order_by(Posts.posted).all()

    posts = []
    for post in query:
        author = post.author
        post = post.as_dict()
        post["author_username"] = author.username
        post["author_image"] = author.image_file
        posts.append(post)
    jsonify(posts)

    return render_template("home.html", title="Home", posts=posts, time_since=time_since)

@app.route("/following")
@login_required
def following():
    following = Follows.query.filter(Follows.follower==current_user.id).all()
    posts = []
    for follow in following:
        user_posts = Posts.query.filter(Posts.user_id==follow.following).all()
        for post in user_posts:
            posts.append(post)

    if posts:
        posts = posts.sort(key=get_time)
    
    return render_template("home.html", title="Following", posts=posts, time_since=time_since)

def get_time(post):
    return post.posted

@app.route("/favourites")
@login_required
def favourites():
    favourites = current_user.favourites
    posts=[]

    for favourite in favourites:
        posts.append(Posts.query.get(favourite.post))
 
    return render_template("home.html", title="Favourites", posts=posts, time_since=time_since)

def serialize_posts(query):
    posts = []
    for post in query:
        dict_post = post.as_dict()
        dict_post["total_votes"] = post.total_votes()
        dict_post["author_username"] = post.author.username
        dict_post["author_image"] = post.author.image_file
        posts.append(post)
    return jsonify(posts)

@app.route("/account/<username>")
@login_required
def account(username):
    user = Users.query.filter_by(username = username).first()
    follow = Follows.query.filter_by(follower=current_user.id, following=user.id).first()
   
    #posts = user.posts.sort(key=get_time)
    return render_template('account.html', title="Account", user=user, follow=follow, date_joined=display_date(user.joined))

@app.route("/account/settings", methods=["GET", "POST"])
@login_required
def settings():
    settingsForm = UpdateAccount()
    if settingsForm.validate_on_submit():
        if settingsForm.picture.data:
            picture_file = save_picture(settingsForm.picture.data)
            if current_user.image_file != "default.jpeg":
                remove_picture()
            current_user.image_file = picture_file
        current_user.username = settingsForm.username.data
        current_user.email = settingsForm.email.data
        db.session.commit()
        #flash message
        return redirect("/account/" + current_user.username)
    elif request.method == "GET":
        settingsForm.username.data = current_user.username
        settingsForm.email.data = current_user.email
    return render_template('settings.html', settingsForm=settingsForm)

def save_picture(picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, "static/profile_pics", picture_fn)

    output_size = (150, 150)
    i = Image.open(picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def remove_picture():
    picture_path = os.path.join(app.root_path, "static/profile_pics", current_user.image_file) 
    os.remove(picture_path)

@app.route("/create_post", methods=["GET", "POST"])
@login_required
def create_post():
    PostForm = CreatePost()

    if PostForm.validate_on_submit():
        post = Posts(content=PostForm.content.data, choice_1=PostForm.choice_1.data, choice_2=PostForm.choice_2.data,
        choice_3=PostForm.choice_3.data, choice_4=PostForm.choice_4.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        #flash message
        return redirect(url_for('home'))
    elif request.method == "GET":
        PostForm.choice_1.data = "Agree"
        PostForm.choice_2.data = "Disagree"
    return render_template('create_post.html', title="Create Post", PostForm=PostForm)

def time_since(posted):
    now = datetime.utcnow
    difference = now - posted
    print(difference)

"""
@app.route("/account/<username>/followers")
@login_required
def account(username):
    return

@app.route("/account/<username>/following")
@login_required
def account(username):
    return
"""

@app.route("/api/like", methods=["PUT"])
@login_required
def like():
    post_id = request.form.get("post_id")
    like = Favourites.query.filter_by(user_id=current_user.id).filter_by(post=post_id).first()
    post = Posts.query.get(post_id)
    if post:
        if like:
            db.session.delete(like)
            post.likes = post.likes - 1
            db.session.commit()
            return jsonify(action='unliked')
        else:
            like = Favourites(user_id=current_user.id, post=post_id)
            db.session.add(like)
            post.likes = post.likes + 1
            db.session.commit()
            return jsonify(action='liked')
    else:
        return jsonify(action='error')

@app.route("/api/follow", methods=["PUT"])
@login_required
def follow():
    user_id = request.form.get("user_id") 
    user = Users.query.get(user_id)
    follow = Follows.query.filter_by(follower=current_user.id, following=user_id).first()
    if user:
        if follow:
            db.session.delete(follow)
            user.followers = user.followers - 1
            current_user.following = current_user.following - 1 
            db.session.commit()
            jsonify(action='unfollow')
        else:
            follow = Follows(follower=current_user.id, following=user_id)
            db.session.add(follow)
            user.followers = user.followers + 1
            current_user.following = current_user.following + 1
            db.session.commit()
            return jsonify(action='follow')
    else:
        return jsonify(action='error')


def create_tests():
    user1 = Users(username="test1", email="Test1@rogers.com", hash="jhvytresdckhcjh")
    user2 = Users(username="test2", email="Test2@gmail.com", hash="jhavscljhqvckjhqvh")
    db.session.add(user1) 
    db.session.add(user2)
    post1 = Posts(content="A tribute to those who got us this far. And an invitation to those who will take us further.", choice_1="yes indeed", choice_2="absolutely", choice_3="yes ", choice_4="no", author=user1) 
    post2 = Posts(content="GOODNIGHT TWITTER BIG DAY TOMORROW", choice_1="haha so true", choice_2="no", choice_3="woah", author=user2)
    post3 = Posts(content="ready for neither trio making top 10. Letssssss go. So good", choice_1="woah really", choice_2="yes for sure", author=user1)
    db.session.add(post1)
    db.session.add(post2)
    db.session.add(post3)
    db.session.commit()
    return