from sqlalchemy.orm import backref, lazyload
from hottopics import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text(), nullable=False)
    email = db.Column(db.Text())
    hash = db.Column(db.Text(), nullable=False)
    followers = db.Column(db.Integer, default=0) 
    following = db.Column(db.Integer, default=0) 
    image_file = db.Column(db.Text(), nullable=False, default='default.jpeg')
    joined = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Posts', backref='author', lazy=True)
    favourites = db.relationship('Favourites', backref='favourites-user', lazy=True)
    comments = db.relationship('Comments', backref='author', lazy=True) 
    posts_voted_for = db.relationship('Votes', backref='voter', lazy=True)

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    choice_1 = db.Column(db.Text())
    votes_1 = db.Column(db.Integer, default=0)
    choice_2 = db.Column(db.Text())
    votes_2 = db.Column(db.Integer, default=0)
    choice_3 = db.Column(db.Text())
    votes_3 = db.Column(db.Integer, default=0)
    choice_4 = db.Column(db.Text())
    votes_4 = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0) 
    comments = db.relationship('Comments', backref='post', lazy=True) 
    posted = db.Column(db.DateTime, default=datetime.utcnow)

    def total_votes(self):
        return self.votes_1 + self.votes_2 + self.votes_3 + self.votes_4

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns} 

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    likes = db.Column(db.Integer, default=0)
    posted = db.Column(db.DateTime, default=datetime.utcnow)

class Follows(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    follower = db.Column(db.Integer) 
    following = db.Column(db.Integer) 

class Favourites(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post = db.Column(db.Integer)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

class Votes(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post = db.Column(db.Integer)
    choice = db.Column(db.Integer) 
        