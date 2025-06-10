from flask import Flask, redirect, render_template, session, flash, request
from models import connect_db, db, User
from forms import RegisterForm, LoginForm

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///authentication_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["SECRET_KEY"] = 'shhhhhh'

connect_db(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home_page():
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    register_form = RegisterForm()

    if register_form.validate_on_submit():
        username = register_form.username.data
        pswd = register_form.password.data
        email = register_form.email.data
        first_name = register_form.first_name.data
        last_name = register_form.last_name.data

        new_user = User.register(username, pswd, email, first_name, last_name)

        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id

        return redirect(f'/users/{username}')

    return render_template('register.html', register_form=register_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        username = login_form.username.data
        pswd = login_form.password.data 

        user = User.authenticate(username, pswd)

        if user:
            session['user_id'] = user.id
            return redirect(f'/users/{username}')

    return render_template('login.html', login_form=login_form)

@app.route('/users/<username>')
def user(username):
    if "user_id" not in session:
        flash("You are not logged in!")
        return redirect("/")

    cur_u = User.query.get_or_404(username)

    return render_template('user.html', user=cur_u)

@app.route("/logout")
def logout():
    session.pop("user_id")

    return redirect("/")