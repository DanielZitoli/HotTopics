import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Configs cookies to be stored in computer's harddrive, and to not last permanently
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

if os.environ.get('ENVIRONMENT_TYPE', '') == 'prod':
    ENV = 'prod'
else:
    ENV = 'dev'
    
if ENV == 'dev':
    app.debug = True
    app.config['SECRET_KEY'] = '055a23834110d872426d5f7ee0ac198a'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost/hottopics'
else:
    app.debug = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '') 
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'index'
login_manager.login_message_category = 'info'

from hottopics import routes

