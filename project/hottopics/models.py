from hottopics import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Users(db.Model, UserMixin):
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
        