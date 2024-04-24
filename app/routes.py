from app.forms import RegistrationForm, LoginForm, GetNameForm, addHospitalForm, addInsuranceForm, FeedbackForm

from flask import render_template, redirect, url_for, request, flash, session
from app import myapp_obj
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, load_user
from app.__init__ import connection

cursor = connection.cursor()


@myapp_obj.route("/", methods=["GET", "POST"])
@login_required
def home():
    user_location_name = None
    if current_user.is_authenticated:
        user_type = current_user.user_type
        if user_type == "insurance_provider":
            users_insurance_id = current_user.insurance_id
            cursor.execute(
                "SELECT name FROM insurance WHERE insurance_id = %s",
                (users_insurance_id,),
            )  # Fetch all claims that are from the same insurance as the current user
            result = cursor.fetchone()

        elif user_type == "hospital":
            users_hospital_id = current_user.hospital_id
            cursor.execute(
                "SELECT name FROM hospital WHERE hospital_id = %s", (users_hospital_id,)
            )  # Fetch all claims that are from the same hospital as the current user
            result = cursor.fetchone()

        if result:
            user_location_name = result[0]

    return render_template(
        "home.html", title="Home", user_location_name=user_location_name
    )


@myapp_obj.route("/signup", methods=["GET", "POST"])
def signupPage():
    form = RegistrationForm(cursor=cursor)

    if request.method == "POST":
        if form.validate_on_submit():
            # Get data from the form
            username = form.username.data
            email_address = form.email_address.data
            firstname = form.firstname.data
            lastname = form.lastname.data
            password = form.password1.data
            user_type = form.user_type.data
            # Hash the password before storing it
            password_hash = generate_password_hash(password)

            # Insert user data into the database
            sql = "INSERT INTO User (username, firstname, lastname, email_address, password_hash, user_type) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (
                username,
                firstname,
                lastname,
                email_address,
                password_hash,
                user_type,
            )
            cursor.execute(sql, val)
            connection.commit()
            user_id = cursor.lastrowid

            # Create an instance of the User class
            user = User(
                user_id=user_id,
                username=username,
                firstname=firstname,
                lastname=lastname,
                email_address=email_address,
                password_hash=password_hash,
                user_type=user_type,
                insurance_id=None,
                hospital_id=None,
            )

            # Log in the user
            login_user(user)
            flash(
                f"Account created successfully! You are now logged in as {username}",
                category="success",
            )
            return redirect(url_for("getname"))
        if form.errors != {}:  # If there are errors in signing up
            for err_msg in form.errors.values():
                flash(
                    f"There was an error with creating a user: {err_msg}",
                    category="danger",
                )  # flash appropriate error message
    return render_template("signup.html", form=form, title="Signup")


@myapp_obj.route("/login", methods=["GET", "POST"])
def loginPage():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        cursor.execute("SELECT * FROM User WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[5], password):
            login_user(
                User(
                    user_id=user[0],
                    username=user[1],
                    firstname=user[2],
                    lastname=user[3],
                    email_address=user[4],
                    password_hash=user[5],
                    insurance_id=user[7],
                    hospital_id=user[8],
                )
            )

            flash(f"Success logging in, Logged in as: {username}", category="success")
            return redirect(url_for("home"))
        else:
            flash(
                "Username or Password does not match! Please try again",
                category="danger",
            )

    return render_template("login.html", title="Login", form=form)


@myapp_obj.route("/getname", methods=["GET", "POST"])
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
            result = cursor.fetchone()  # Store the result in a variable
            insurance_id = (
                result[0] if result else None
            )  # Check if result is not None before accessing its elements

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
            result = cursor.fetchone()  # Store the result in a variable
            hospital_id = (
                result[0] if result else None
            )  # Check if result is not None before accessing its elements

            if hospital_id:
                sql = "UPDATE User SET hospital_id = %s WHERE id = %s"
                val = (hospital_id, userid)
                cursor.execute(sql, val)
                connection.commit()

        flash(f"Success!", category="success")
        return redirect(url_for("home"))

    cursor.execute("SELECT name FROM insurance")
    # Fetch all rows and store the names in the insurance_names list
    for row in cursor.fetchall():
        insurance_names.append(row[0])
    cursor.execute("SELECT name FROM hospital")
    # Fetch all rows and store the names in the hospital_names list
    for row in cursor.fetchall():
        hospital_names.append(row[0])
    return render_template(
        "getname.html",
        form=form,
        insurance_names=insurance_names,
        hospital_names=hospital_names,
    )


@myapp_obj.context_processor
def base():
    form = GetNameForm()
    return dict(form=form)


@myapp_obj.route("/infopage", methods=["GET", "POST"])
@login_required
def infopage():
    form = FeedbackForm()
    if form.validate_on_submit():
        user_id = current_user.id
        feedback_content = form.feedback.data

        sql = "INSERT INTO feedback (user_id, feedback_content) VALUES (%s, %s)"
        val = (user_id, feedback_content)
        cursor.execute(sql, val)
        connection.commit()
        flash("Feedback received!", category="success")
        return render_template("home.html", form=form)
    return render_template("infopage.html", form=form)


@myapp_obj.route("/profilepage", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        if (
            request.form.get("deleteprofile") == "Delete Profile"
        ):  # if the delete profile button is clicked
            userid2 = request.form.get("userid2")
            cursor.execute("SELECT * FROM User WHERE id = %s", (userid2,))
            user = cursor.fetchone()
            if user:
                user_id = user[0]  # Assuming the user ID is at index 0
                cursor.execute("DELETE FROM User WHERE id = %s", (user_id,))
                connection.commit()
                flash("Profile Deleted!", category="success")
                return redirect(url_for("logoutPage"))  # flash and redirect
            else:
                flash("User not found!", category="danger")
        if request.form.get("changepassword") == "Change Password":
            return redirect(url_for("changepassword"))
    return render_template("profilepage.html")

@myapp_obj.route('/addHospital', methods=["GET", "POST"])
def addHospital():
    form = addHospitalForm()
    if form.validate_on_submit():
        name = form.name.data
        address = form.address.data
        phone_number = form.phone_number.data

        connection.autocommit = False

        try:
            # Insert hospital data into the database
            sql = "INSERT INTO hospital (name, address, phone_number) VALUES (%s, %s, %s)"
            val = (name, address, phone_number)
            cursor.execute(sql, val)
            
            # Retrieve the hospital_id of the newly inserted hospital
            sql = "SELECT LAST_INSERT_ID()"
            cursor.execute(sql)
            hospital_id = cursor.fetchone()[0] # Assuming the hospital_id is the first column in the result
            
            # Update the User table to set the hospital_id for the current user
            sql = "UPDATE User SET hospital_id = %s WHERE id = %s"
            val = (hospital_id, current_user.id)
            cursor.execute(sql, val)
            
            # Commit the transaction
            connection.commit()
        except Exception as e:
            # Rollback the transaction in case of error
            connection.rollback()
            print("Error: ", e)
        finally:
            # Ensure the connection is set back to autocommit mode
            connection.autocommit = True

        flash(f'Success! {name} has been added', category='success')
        return redirect(url_for('home'))
    return render_template('addHospital.html', form=form)

from flask import flash, redirect, render_template, url_for
from flask_login import current_user

@myapp_obj.route('/addInsurance', methods=["GET", "POST"])
def addInsurance():
    form = addInsuranceForm()
    if form.validate_on_submit():
        name = form.name.data
        phone_number = form.phone_number.data

        # Start a transaction by setting autocommit to False
        connection.autocommit = False

        try:
            # Insert insurance data into the database
            sql = "INSERT INTO insurance (name, phone_number) VALUES (%s, %s)"
            val = (name, phone_number)
            cursor.execute(sql, val)
            
            # Retrieve the insurance_id of the newly inserted insurance
            sql = "SELECT LAST_INSERT_ID()"
            cursor.execute(sql)
            insurance_id = cursor.fetchone()[0] # Assuming the insurance_id is the first column in the result
            
            # Update the User table to set the insurance_id for the current user
            sql = "UPDATE User SET insurance_id = %s WHERE id = %s"
            val = (insurance_id, current_user.id)
            cursor.execute(sql, val)
            
            # Commit the transaction
            connection.commit()

            flash(f'Success! {name} has been added', category='success')
            return redirect(url_for('home'))
        except Exception as e:
            # Rollback the transaction in case of error
            connection.rollback()
            print("Error: ", e)
            flash('An error occurred while adding insurance.', category='danger')
        finally:
            # Ensure the connection is set back to autocommit mode
            connection.autocommit = True

    return render_template('addInsurance.html', form=form)
