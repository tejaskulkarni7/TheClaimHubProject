from app.forms import RegistrationForm, LoginForm, GetNameForm

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
            user = User(user_id=user_id, username=username, firstname = firstname, lastname = lastname, email_address=email_address, password_hash=password_hash, insurance_id=None, hospital_id=None)

            # Log in the user
            login_user(user)
            flash(f'Account created successfully! You are now logged in as {username}', category='success')
        if form.errors != {}: #If there are errors in signing up
            for err_msg in form.errors.values():
                flash(f'There was an error with creating a user: {err_msg}', category='danger') #flash appropriate error message
    return render_template('signup.html', form=form, title='Signup')


@myapp_obj.route("/login", methods=['GET', 'POST'])
def loginPage():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        cursor.execute("SELECT * FROM User WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[5], password): # Assuming password_hash is at index 3
            login_user(User(user_id=user[0], username=user[1], firstname=user[2], lastname=user[3], email_address=user[4], password_hash=user[5], insurance_id=user[7], hospital_id=user[8]))

            flash(f'Success logging in, Logged in as: {username}', category='success')
            return redirect(url_for('home'))
        else:
            flash('Username or Password does not match! Please try again', category='danger')

    return render_template('login.html', title='Login', form=form)


@myapp_obj.route('/getname', methods=["GET", "POST"])
def getname():
    form = GetNameForm()
    insurance_names = []
    hospital_names = []
    if form.validate_on_submit():
        insurance_name = form.insurance_name.data
        hospital_name = form.hospital_name.data
        userid = current_user.id

        # Fetch the ID of the selected insurance
        if insurance_name is not None:
            sql = "SELECT insurance_id FROM insurance WHERE name = %s"
            val = (insurance_name,)
            cursor.execute(sql, val)
            result = cursor.fetchone() # Store the result in a variable
            insurance_id = result[0] if result else None # Check if result is not None before accessing its elements

            if insurance_id:
                sql = "UPDATE User SET insurance_id = %s WHERE id = %s"
                val = (insurance_id, userid)
                cursor.execute(sql, val)
                connection.commit()

        # Fetch the ID of the selected hospital
        if hospital_name is not None:
            sql = "SELECT hospital_id FROM hospital WHERE name = %s"
            val = (hospital_name,)
            cursor.execute(sql, val)
            result = cursor.fetchone() # Store the result in a variable
            hospital_id = result[0] if result else None # Check if result is not None before accessing its elements

            if hospital_id:
                sql = "UPDATE User SET hospital_id = %s WHERE id = %s"
                val = (hospital_id, userid)
                cursor.execute(sql, val)
                connection.commit()

        flash(f'Success!', category='success')
        return redirect(url_for('home'))
    
    cursor.execute("SELECT name FROM insurance")
    # Fetch all rows and store the names in the insurance_names list
    for row in cursor.fetchall():
        insurance_names.append(row[0])
    cursor.execute("SELECT name FROM hospital")
    # Fetch all rows and store the names in the hospital_names list
    for row in cursor.fetchall():
        hospital_names.append(row[0])
    return render_template("getname.html", form=form, insurance_names=insurance_names, hospital_names=hospital_names)