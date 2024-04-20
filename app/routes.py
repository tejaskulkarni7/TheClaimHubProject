from app.forms import RegistrationForm, LoginForm

from flask import render_template, redirect, url_for, request, flash, session
from app import myapp_obj
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, load_user
from app.__init__ import connection


cursor = connection.cursor()


@myapp_obj.route("/signup", methods=['GET', 'POST'])
def signupPage():
    form = RegistrationForm(cursor=cursor)

    if request.method == 'POST':
        if form.validate_on_submit():
            # Get data from the form
            username = form.username.data
            email_address = form.email_address.data
            firstname = form.firstname.data
            lastname = form.lastname.data
            password = form.password1.data
            # Hash the password before storing it
            password_hash = generate_password_hash(password)

            # Insert user data into the database
            sql = "INSERT INTO User (username, firstname, lastname, email_address, password_hash) VALUES (%s, %s, %s, %s, %s)"
            val = (username, firstname, lastname, email_address, password_hash)
            cursor.execute(sql, val)
            connection.commit()
            user_id = cursor.lastrowid

            # Create an instance of the User class
            user = User(user_id=user_id, username=username, firstname = firstname, lastname = lastname, email_address=email_address, password_hash=password_hash)

            # Log in the user
            login_user(user)
            flash(f'Account created successfully! You are now logged in as {username}', category='success')
        if form.errors != {}: #If there are errors in signing up
            for err_msg in form.errors.values():
                flash(f'There was an error with creating a user: {err_msg}', category='danger') #flash appropriate error message
    return render_template('signup.html', form=form, title='Signup')