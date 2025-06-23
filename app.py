from flask import Flask, redirect, render_template, session, flash
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

            if register_form.admin_code.data and register_form.admin_code.data == '123':
                is_admin = True
            else:
                is_admin = False
            
            new_user = User.register(username, password, email, first_name, last_name, is_admin)

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

        try:
            if login_form.validate_on_submit():
                username = login_form.form_username.data
                password = login_form.form_password.data 

                user = User.authenticate(username, password)

                if user:
                    session['username'] = user.username    
                    return redirect(f'/users/{username}')

            return render_template('user_login.html', form=login_form)
        except Exception as e:
            flash(f'Error Loggin in, error: {e}', category='danger')
            return redirect('/')

    flash('You are logged in.' , category="warning")
    return redirect(f'/users/{session["username"]}')

@app.route('/users/<username>')
def user(username):
    if "username" not in session:
        flash("You are not logged in!", category="danger")
        return redirect("/")
    try:
        cur_u = User.query.get_or_404(username)
        u_feedback = cur_u.feedback.order_by(Feedback.title).all()
    except Exception as e:
        flash(f'Error getting data, error: {e}', category='danger')
        return redirect('/')

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
    
    try:
        u = User.query.get_or_404(username)
        cur_u = User.query.get_or_404(session['username'])
    except Exception as e:
        flash(f'Error getting data, error: {e}', category='danger')
        return redirect(f'/users/{username}')

    if cur_u.is_admin == True and username != cur_u.username:
        db.session.delete(u)
        db.session.commit()
        return redirect(f'/users/{cur_u.username}')
    if u and u.username == cur_u.username:
        session.pop('username')
        db.session.delete(u)
        db.session.commit()
        return redirect('/')


''' FEEDBACK '''

@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def feedback_update(feedback_id):
    if "username" not in session:
        flash("You dont have access to that!", category="danger")
        return redirect('/')

    try:
        f = Feedback.query.get_or_404(feedback_id)
        update_f_form = FeedbackForm(obj=f)
        cur_u = User.query.get_or_404(session['username'])
    except Exception as e:
        flash(f'Error getting data, error: {e}', category='danger')
        return redirect('/')  

    if f.user.username == session['username'] or cur_u.is_admin == True:
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
    try:
        f = Feedback.query.get_or_404(feedback_id)
        f_user = User.query.get_or_404(f.user.username)
        cur_u = User.query.get_or_404(session['username'])
    except Exception as e:
        flash(f'Error getting data, error: {e}', category='danger')
        return redirect('/')

    if f and f_user and cur_u:
        if cur_u.is_admin == True and cur_u.username != f_user.username:
            db.session.delete(f)
            db.session.commit()
            return redirect(f'/users/{f_user.username}')
        if cur_u.username == f_user.username:
            db.session.delete(f)
            db.session.commit()
            return redirect(f'/users/{cur_u.username}')

    return redirect('/')

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def feedback_add(username):
    if "username" not in session:
        flash("You must be logged in!", category="danger")
        return redirect('/')

    try:
        feedback_add_form = FeedbackForm()
        cur_u = User.query.get_or_404(session['username'])
    except Exception as e:
        flash(f'Error getting data, error: {e}', category='danger')
        return redirect(f'/users/{username}')
    
    if username != session['username'] and cur_u.is_admin == False:
        flash("You cannot add feedback!", category="danger")
        return redirect(f'/users/{username}')

    if username == cur_u.username or cur_u.is_admin == True:
        if feedback_add_form.validate_on_submit():
            title = feedback_add_form.title.data.capitalize()
            content = feedback_add_form.content.data

            new_feedback = Feedback(title=title, content=content, username=username)
            db.session.add(new_feedback)
            db.session.commit()

            return redirect(f'/users/{username}')
        return render_template('feedback_add.html', form=feedback_add_form)
    return redirect(f'/users/{username}')

''' 404 PAGE '''
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

''' 401 PAGE '''
@app.errorhandler(401)
def unauthorized(error):
    return render_template('401.html'), 401