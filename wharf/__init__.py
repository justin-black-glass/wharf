from config import LANGUAGES

from flask import Flask
from flask import request
from flask import session
from flask.ext.babel import Babel
from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security
from flask.ext.security import SQLAlchemyUserDatastore
from flask.ext.security import UserMixin
from flask.ext.security import RoleMixin

# set defaults

DOCKER_HOST="localhost"
DOMAIN = "localhost"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
SERVICES_FOLDER = '/home/vagrant/wharf/services/'
SERVICE_DICT = {'description':'description.txt',
                'client':'client/client.txt',
                'about':'html/about.html',
                'body':'html/body.html',
                'link':'html/link.html',
                'dockerfile':'docker/Dockerfile'}
UPLOAD_FOLDER = '/home/vagrant/wharf/tmp/'

app = Flask(__name__)
app.config['DEBUG'] = True
# this should be re-generated for production use
app.config['SECRET_KEY'] = 'EckNi2Fluincawd+'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/db.sqlite'
app.config['DEFAULT_MAIL_SENDER'] = 'dockerwharf@gmail.com'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_CONFIRMABLE'] = True
app.config['SECURITY_CHANGEABLE'] = True
app.config['SECURITY_RECOVERABLE'] = True
app.config['SECURITY_PASSWORD_HASH'] = 'sha512_crypt'
# this should be re-generated for production use
app.config['SECURITY_PASSWORD_SALT'] = 'S)1<P3_~$XF}DI=#'
app.config['SECURITY_POST_REGISTER_VIEW'] = '/login'
app.config['DOCKER_HOST'] = DOCKER_HOST
app.config['DOMAIN'] = DOMAIN
app.config['REDIS_HOST'] = REDIS_HOST
app.config['REDIS_PORT'] = REDIS_PORT
app.config['SERVICES_FOLDER'] = SERVICES_FOLDER
app.config['SERVICE_DICT'] = SERVICE_DICT
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_object('wharf.email_config.email')
app.debug = True

# Setup mail extension
mail = Mail(app)

# Setup babel
babel = Babel(app)

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(LANGUAGES.keys())

# Create database connection object
db = SQLAlchemy(app)

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return '<User id=%s email=%s>' % (self.id, self.email)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

db.create_all()

import wharf.details
import wharf.edit
import wharf.favicon
import wharf.forms
import wharf.index
import wharf.kill
import wharf.new
import wharf.profile
import wharf.robot
import wharf.saas
