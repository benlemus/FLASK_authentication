from flask import Flask, redirect, render_template, session, flash, request
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm

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

    if 'username' not in session:
        register_form = RegisterForm()

        if register_form.validate_on_submit():
            username = register_form.form_username.data
            password = register_form.form_password.data
            email = register_form.email.data
            first_name = register_form.first_name.data
            last_name = register_form.last_name.data

            new_user = User.register(username, password, email, first_name, last_name)

            db.session.add(new_user)
            db.session.commit()

            session['username'] = new_user.username

            return redirect(f'/users/{username}')

        return render_template('user_register.html', form=register_form)
    
    flash('You are logged in.' , category="info")
    
    return redirect(f'/users/{session["username"]}')

@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if 'username' not in session:
        login_form = LoginForm()

        if login_form.validate_on_submit():
            username = login_form.form_username.data
            password = login_form.form_password.data 

            user = User.authenticate(username, password)

            if user:
                session['username'] = user.username    
                return redirect(f'/users/{username}')

        return render_template('user_login.html', form=login_form)
    
    flash('You are logged in.' , category="warning")
    
    return redirect(f'/users/{session["username"]}')

@app.route('/users/<username>')
def user(username):
    if "username" not in session:
        flash("You are not logged in!", category="danger")
        return redirect("/")

    cur_u = User.query.get_or_404(username)

    u_feedback = cur_u.feedback.order_by(Feedback.title).all()

    return render_template('user.html', user=cur_u, feedback=u_feedback)

@app.route('/logout')
def user_logout():
    session.pop('username')

    return redirect('/')

@app.route('/users/<username>/delete')
def delete_user(username):
    if "username" not in session:
        flash("You are not logged in!", category="danger")
        return redirect("/")
    
    user = User.query.get_or_404(session['username'])

    if user and user.username == username:
        session.pop('username')
        db.session.delete(user)
        db.session.commit()

        return redirect('/')


''' FEEDBACK '''

@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def feedback_update(feedback_id):
    if "username" not in session:
        flash("You dont have access to that!", category="danger")
        return redirect('/')

    f = Feedback.query.get_or_404(feedback_id)
    update_f_form = FeedbackForm(obj=f)

    if f.user.username == session['username']:
        if update_f_form.validate_on_submit():
            f.title = update_f_form.title.data.capitalize()
            f.content = update_f_form.content.data
            db.session.commit()
            return redirect(f'/users/{f.user.username}')
        
        
        return render_template('feedback_update.html', form=update_f_form)

@app.route('/feedback/<int:feedback_id>/delete')
def feedback_delete(feedback_id):
    if "username" not in session:
        flash("You dont have access to that!", category="danger")
        return redirect('/')
    
    f = Feedback.query.get_or_404(feedback_id)
    cur_u = User.query.get_or_404(f.user.username)
    db.session.delete(f)
    db.session.commit()
    return redirect(f'/users/{cur_u.username}')

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def feedback_add(username):
    if "username" not in session:
        flash("You must be logged in!", category="danger")
        return redirect('/')
    
    if username != session['username']:
        flash("You cannot add feedback!", category="danger")
        return redirect(f'/users/{username}')
    
    feedback_add_form = FeedbackForm()
    cur_u = User.query.get_or_404(session['username'])

    if username == cur_u.username:
            if feedback_add_form.validate_on_submit():
                title = feedback_add_form.title.data.capitalize()
                content = feedback_add_form.content.data

                new_feedback = Feedback(title=title, content=content, username=username)
                db.session.add(new_feedback)
                db.session.commit()

                return redirect(f'/users/{username}')
            return render_template('feedback_add.html', form=feedback_add_form)


    return redirect(f'/users/{username}')


