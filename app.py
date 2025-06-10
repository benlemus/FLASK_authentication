from flask import Flask, redirect, render_template, session, flash, request
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, UpdateFForm

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


''' USER '''

@app.route('/register', methods=['GET', 'POST'])
def user_register():
    register_form = RegisterForm()

    if register_form.validate_on_submit():
        username = register_form.username.data
        password = register_form.password.data
        email = register_form.email.data
        first_name = register_form.first_name.data
        last_name = register_form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id

        return redirect(f'/users/{username}')

    return render_template('user_register.html', form=register_form)

@app.route('/login', methods=['GET', 'POST'])
def user_login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data 

        user = User.authenticate(username, password)

        if user:
            session['user_id'] = user.id
            return redirect(f'/users/{username}')

    return render_template('user_login.html', form=login_form)

@app.route('/users/<username>')
def user(username):
    if "user_id" not in session:
        flash("You are not logged in!")
        return redirect("/")

    cur_u = User.query.get_or_404(username)

    u_feedback = cur_u.feedback

    return render_template('user.html', user=cur_u, feedback=u_feedback)

@app.route("/logout")
def user_logout():
    session.pop("user_id")

    return redirect("/")


''' FEEDBACK '''

@app.route('/feedback/<int:f_id>/update', methods=['GET', 'POST'])
def feedback_update(f_id):
    f = Feedback.query.get_or_404(f_id)
    update_f_form = UpdateFForm(obj=f)

    if f.user.id == session['user_id']:
        if update_f_form.validate_on_submit():
            f.title = update_f_form.title.data
            f.content = update_f_form.content.data
            db.session.commit()
            return redirect(f'/users/{f.user.username}')
        
        
        return render_template('feedback_update.html', form=update_f_form)

@app.route('/feedback/<int:f_id>/delete')
def feedback_delete(f_id):
    f = Feedback.query.get_or_404(f_id)
    cur_u = User.query.get_or_404(f.user.username)
    db.session.delete(f)
    db.session.commit()
    return redirect(f'/users/{cur_u.username}')


