import os
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '055a23834110d872426d5f7ee0ac198a'
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Configs cookies to be stored in computer's harddrive, and to not last permanently
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


ENV = 'dev'
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost/hottopics'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://yrnugqkbbjqmqd:9af42259e3b62867f9add5761bd5295d29844ac6924232422ab9907012210de5@ec2-34-205-209-14.compute-1.amazonaws.com:5432/d1u80l661238l6'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Session(app)
login_manager = LoginManager(app)
login_manager.login_view = 'index'
login_manager.login_message_category = 'info'


from hottopics import routes