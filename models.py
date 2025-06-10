from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)
    bcrypt.init_app(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, autoincrement=True)
    username = db.Column(db.String(20), primary_key=True, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    @classmethod
    def register(cls, username, pswd, email, first_name, last_name):
        hashed = bcrypt.generate_password_hash(pswd)
        hashed_utf8 = hashed.decode('utf8')

        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)
    
    @classmethod
    def authenticate(cls, username, pswd):
        
        cur_u = User.query.get_or_404(username)

        if cur_u and bcrypt.check_password_hash(cur_u.password, pswd):
            return cur_u
        
        return False
