from app.forms import (
    RegistrationForm,
    LoginForm,
    PasswordForm,
    GetNameForm,
    addHospitalForm,
    addInsuranceForm,
    FeedbackForm,
    addClaimForm,
    addPatientForm,
    SearchForm
)

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
    access = "default"
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
        if current_user.username == "admin":
            access = "admin"
            

    return render_template(
        "home.html", title="Home", user_location_name=user_location_name, access=access
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


            session['registration_data'] = {
            'username': username,
            'email_address': email_address,
            'firstname': firstname,
            'lastname': lastname,
            'password_hash': password_hash,
            'user_type': user_type
            }
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
                    user_type=user[6],
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


@myapp_obj.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    form = PasswordForm()
    if form.validate_on_submit():
        currentpass = form.currentpass.data
        newpass = form.newpass.data
        userid2 = request.form.get("userid2")
        cursor.execute("SELECT * FROM User WHERE id = %s", (userid2,))
        user = cursor.fetchone()
        if user and check_password_hash(
            user[5], currentpass
        ):  # Assuming password_hash is at index 3
            password_hash = generate_password_hash(newpass)
            cursor.execute(
                "UPDATE User SET password_hash = %s WHERE id = %s",
                (
                    password_hash,
                    userid2,
                ),
            )
            connection.commit()
            flash("Your Password Has Been Changed", category="success")
            return render_template("changepassword.html", form=form)
        else:
            flash("Incorrect Password", category="danger")
            return render_template("changepassword.html", form=form)
    return render_template("changepassword.html", form=form)


@myapp_obj.route("/getname", methods=["GET", "POST"])
def getname():
    form = GetNameForm()
    insurance_names = []
    hospital_names = []
    registration_data = session.get('registration_data')
    user_type = registration_data.get('user_type')
    if form.validate_on_submit():
        insurance_name = form.insurance_name.data
        hospital_name = form.hospital_name.data
        username = registration_data.get('username')
        email_address = registration_data.get('email_address')
        firstname = registration_data.get('firstname')
        lastname = registration_data.get('lastname')
        password_hash = registration_data.get('password_hash')


        # Insert user data into the database and log in user
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
                val = (insurance_id, user_id)
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
                val = (hospital_id, user_id)
                cursor.execute(sql, val)
                connection.commit()
        
        session.pop('registration_data', None)
        # Log in the user
        login_user(user)
        flash(
            f"Account created successfully! You are now logged in as {username}",
            category="success",
        )
        return redirect(url_for("home"))

    cursor.execute("SELECT name FROM insurance")
    # Fetch all rows and store the names in the insurance_names list
    for row in cursor.fetchall():
        insurance_names.append(row[0])
    cursor.execute("SELECT name FROM hospital")
    # Fetch all rows and store the names in the hospital_names list
    for row in cursor.fetchall():
        hospital_names.append(row[0])
    return render_template("getname.html",form=form,insurance_names=insurance_names,hospital_names=hospital_names, user_type=user_type)


@myapp_obj.context_processor
def base():
    form = SearchForm()
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


@myapp_obj.route("/addHospital", methods=["GET", "POST"])
def addHospital():
    form = addHospitalForm()
    if form.validate_on_submit():
        name = form.name.data
        address = form.address.data
        registration_data = session.get('registration_data')
        user_type = registration_data.get('user_type')
        phone_number = form.phone_number.data
        username = registration_data.get('username')
        email_address = registration_data.get('email_address')
        firstname = registration_data.get('firstname')
        lastname = registration_data.get('lastname')
        password_hash = registration_data.get('password_hash')


        # Insert user data into the database and log in user
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

        connection.autocommit = False

        try:
            # Insert hospital data into the database
            sql = (
                "INSERT INTO hospital (name, address, phone_number) VALUES (%s, %s, %s)"
            )
            val = (name, address, phone_number)
            cursor.execute(sql, val)

            # Retrieve the hospital_id of the newly inserted hospital
            sql = "SELECT LAST_INSERT_ID()"
            cursor.execute(sql)
            hospital_id = cursor.fetchone()[0]  # Assuming the hospital_id is the first column in the result

            # Update the User table to set the hospital_id for the current user
            sql = "UPDATE User SET hospital_id = %s WHERE id = %s"
            val = (hospital_id, user_id)
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

        flash(f"Success! {name} has been added", category="success")
        session.pop('registration_data', None)
        # Log in the user
        login_user(user)
        flash(
            f"Account created successfully! You are now logged in as {username}",
            category="success",
        )
        return redirect(url_for("home"))
    return render_template("addHospital.html", form=form)


@myapp_obj.route("/addInsurance", methods=["GET", "POST"])
def addInsurance():
    form = addInsuranceForm()
    if form.validate_on_submit():
        name = form.name.data
        phone_number = form.phone_number.data
        registration_data = session.get('registration_data')
        user_type = registration_data.get('user_type')
        username = registration_data.get('username')
        email_address = registration_data.get('email_address')
        firstname = registration_data.get('firstname')
        lastname = registration_data.get('lastname')
        password_hash = registration_data.get('password_hash')


        # Insert user data into the database and log in user
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
            insurance_id = cursor.fetchone()[0]  # Assuming the insurance_id is the first column in the result

            # Update the User table to set the insurance_id for the current user
            sql = "UPDATE User SET insurance_id = %s WHERE id = %s"
            val = (insurance_id, user_id)
            cursor.execute(sql, val)

            # Commit the transaction
            connection.commit()

        except Exception as e:
            # Rollback the transaction in case of error
            connection.rollback()
            print("Error: ", e)
            flash("An error occurred while adding insurance.", category="danger")
        finally:
            # Ensure the connection is set back to autocommit mode
            connection.autocommit = True

        flash(f"Success! {name} has been added", category="success")
        session.pop('registration_data', None)
        # Log in the user
        login_user(user)
        flash(
            f"Account created successfully! You are now logged in as {username}",
            category="success",
        )
        return redirect(url_for("home"))
    return render_template("addInsurance.html", form=form)


@myapp_obj.route("/logout")
def logoutPage():
    logout_user()
    flash("You have been logged out!", category="info")
    return redirect(url_for("home"))


@myapp_obj.route("/claimpage", methods=["GET", "POST"])
@login_required
def claimpage():

    search_results = session.get('search_results', [])
    search_made = session.get('search_made')

    hospital_names_dict = {}
    user_type = (
        current_user.user_type
    )  # Current users hospital/insurance type & id for query
    if user_type == "insurance_provider":
        users_insurance_id = current_user.insurance_id
        cursor.execute(
            "SELECT * FROM claim WHERE insurance_id = %s", (users_insurance_id,)
        )  # Fetch all claims that are from the same insurance as the current user
        claims = cursor.fetchall()
        cursor.execute(
            "SELECT hospital_id FROM claim WHERE insurance_id = %s",
            (users_insurance_id,),
        )
        hospital_ids = cursor.fetchall()
        for row in hospital_ids:
            hospital_id = row[0]  # Extracting the hospital ID from the fetched row
            cursor.execute(
                "SELECT name FROM hospital WHERE hospital_id = %s", (hospital_id,)
            )
            name = cursor.fetchone()
            if name:
                hospital_names_dict[hospital_id] = name[0]
    insurance_names_dict = {}
    if user_type == "hospital":
        users_hospital_id = current_user.hospital_id
        cursor.execute(
            "SELECT * FROM claim WHERE hospital_id = %s", (users_hospital_id,)
        )  # Fetch all claims that are from the same hospital as the current user
        claims = cursor.fetchall()
        cursor.execute(
            "SELECT insurance_id FROM claim WHERE hospital_id = %s",
            (users_hospital_id,),
        )
        insurance_ids = cursor.fetchall()
        for row in insurance_ids:
            insurance_id = row[0]  # Extracting the insurance ID from the fetched row
            cursor.execute(
                "SELECT name FROM insurance WHERE insurance_id = %s", (insurance_id,)
            )
            name = cursor.fetchone()
            if name:
                insurance_names_dict[insurance_id] = name[0]

    # Initialize a dictionary to store procedure names by their IDs
    procedure_names_dict = {}

    # Execute a single query to fetch all procedure names tied to each claim's procedure_id
    cursor.execute(
        """
        SELECT c.procedure_id, p.name
        FROM claim c
        JOIN `medical_procedure` p ON c.procedure_id = p.procedure_id
    """
    )

    # Fetch all results from the query
    results = cursor.fetchall()

    # Loop through each result to populate the dictionary
    for row in results:
        procedure_id = row[0]  # Extracting the procedure ID from the fetched row
        name = row[1]  # Extracting the procedure name from the fetched row
        procedure_names_dict[procedure_id] = name

    # Extract all unique patient IDs from the claims
    patient_ids = list(
        set(claim[3] for claim in claims)
    )  # Assuming patient_id is at index 3

    # Fetch all patients whose IDs are in the list of patient IDs
    if patient_ids:
        placeholders = ", ".join(["%s"] * len(patient_ids))
        cursor.execute(
            f"SELECT * FROM patient WHERE patient_id IN ({placeholders})",
            tuple(patient_ids),
        )
        patients = cursor.fetchall()
    else:
        patients = []

    # Create a dictionary mapping patient IDs to patient names
    if patients:
        patient_names = {patient[0]: patient[1] for patient in patients}
    else:
        patient_names = {}

    #search functionality to restrict claims to what has been searched:
    if search_results or search_made:
        claims2 = search_results # IMPORTANT --> overrides all claims set to give a limited result set specified by search query
        if claims2:
            claim_ids1 = {claim_ran[0] for claim_ran in claims}
            claim_ids2 = {claim_ran[0] for claim_ran in claims2}
            claims = claim_ids1 & claim_ids2
            # Initialize an empty list to store the results
            all_claims = []
            # Iterate over each claim ID in the intersection set
            for claim_id in claims:
                # Execute the query for each claim ID
                cursor.execute("SELECT * FROM claim WHERE claim_id = %s", (claim_id,))
                # Fetch all results for this claim ID and extend the all_claims list
                all_claims.extend(cursor.fetchall())
            # Now all_claims contains all rows from the claim table where claim_id is in the intersection set
            claims = all_claims
        else:
            claims = []
        session.pop('search_results', None)
        session.pop('search_made', None)


    cursor.execute(
        """
        SELECT comment.comment_id, comment.user_id, comment.claim_id, comment.comment_time, comment.comment_content, User.username
        FROM comment
        JOIN User ON comment.user_id = User.id
    """
    )
    comments = cursor.fetchall()

    if request.method == "POST":
        if (
            request.form.get("deleteclaim") == "Delete Claim"
        ):  # if the delete profile button is clicked
            claim_id = request.form.get("claim_id")
            cursor.execute("SELECT * FROM claim WHERE claim_id = %s", (claim_id,))
            claim = cursor.fetchone()
            if claim:
                claim_id = claim[0]  # Assuming the user ID is at index 0

                #for the edit log 
                sql = "INSERT INTO edit_log (user_id, claim_id, edit_type) VALUES (%s, %s, %s)"
                val = (current_user.id, claim_id, "delete")
                cursor.execute(sql, val)
                connection.commit()

                # delete the claim (foreign key constraint bypassed intentionally)
                cursor.execute("DELETE FROM claim WHERE claim_id = %s", (claim_id,))
                connection.commit()

                flash("Claim Deleted!", category="success")
                return redirect(url_for("claimpage"))  # flash and redirect
            else:
                flash("Claim not found!", category="danger")
        if (
            request.form.get("updatestatus") == "Update Status"
        ):  # Check if the update status button is clicked
            claim_id = request.form.get("claim_id")
            new_status = request.form.get("status")  # Get the new status from the form
            # Check if the claim exists
            cursor.execute("SELECT * FROM claim WHERE claim_id = %s", (claim_id,))
            claim = cursor.fetchone()
            if claim:
                 #first update edit_log
                sql = "INSERT INTO edit_log (user_id, claim_id, edit_type) VALUES (%s, %s, %s)"
                val = (current_user.id, claim_id, "change_status")
                cursor.execute(sql, val)
                connection.commit()

                # Update the claim's status
                cursor.execute(
                    "UPDATE claim SET status = %s WHERE claim_id = %s",
                    (new_status, claim_id),
                )
                connection.commit()
                flash("Claim status updated successfully!", category="success")
                return redirect(url_for("claimpage"))  # Redirect to the claim page
            else:
                flash("Claim not found!", category="danger")
                return redirect(url_for("claimpage"))  # Redirect to the claim page
        if (
            request.form.get("addcomment") == "Add Comment"
        ):  # Check if the update status button is clicked
            claim_id = request.form.get("claim_id")
            comment_content = request.form.get(
                "comment"
            )  # Get the new status from the form
            if comment_content:
                sql = "INSERT INTO comment (user_id, claim_id, comment_content) VALUES (%s, %s, %s)"
                val = (current_user.id, claim_id, comment_content)
                cursor.execute(sql, val)
                connection.commit()
                flash("Comment Added!", category="success")
            else:
                flash("Error!", category="danger")
            return redirect(url_for("claimpage"))
        if (request.form.get("sortOrder") == "asc"):
            claims = sorted(claims, key=lambda x: x[6])
        if (request.form.get("sortOrder") == "desc"):
            claims = sorted(claims, key=lambda x: x[6], reverse=True)

    return render_template(
        "claimpage.html",
        claims=claims,
        patient_names=patient_names,
        hospital_names_dict=hospital_names_dict,
        insurance_names_dict=insurance_names_dict,
        procedure_names_dict=procedure_names_dict,
        comments=comments,
    )


@myapp_obj.route("/patientspage", methods=["GET", "POST"])
@login_required
def patientspage():
    # Execute the query to fetch all patients
    cursor.execute("SELECT * FROM patient")
    patients = cursor.fetchall()

    # Render the template with the patients data
    return render_template("patientspage.html", patients=patients)


@myapp_obj.route("/addclaim", methods=["GET", "POST"])
@login_required
def addclaim():
    form = addClaimForm()
    insurance_names = []
    hospital_names = []

    if form.validate_on_submit():
        insurance_name = form.insurance_name.data
        hospital_name = form.hospital_name.data
        patient_id = form.patient_id.data
        procedure_id = form.procedure_id.data
        date = form.date.data
        total_amount = form.total_amount.data
        covered_amount = form.covered_amount.data
        description = form.description.data
        # userid = current_user.id
        status = "Pending"

        if current_user.user_type == "insurance_provider":
            insurance_id = current_user.insurance_id
            sql = "SELECT hospital_id FROM hospital WHERE name = %s"
            val = (hospital_name,)
            cursor.execute(sql, val)
            result = cursor.fetchone()  # Store the result in a variable
            hospital_id = result[0]
        if current_user.user_type == "hospital":
            hospital_id = current_user.hospital_id
            sql = "SELECT insurance_id FROM insurance WHERE name = %s"
            val = (insurance_name,)
            cursor.execute(sql, val)
            result = cursor.fetchone()  # Store the result in a variable
            insurance_id = result[0]

        # sql = "INSERT INTO claim (hospital_id, insurance_id, patient_id, procedure_id, status, date, total_amount, covered_amount, description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        # val = (hospital_id, insurance_id, patient_id, procedure_id, status, date, total_amount, covered_amount, description)

        connection.autocommit = False
        try:
            sql = "INSERT INTO claim (hospital_id, insurance_id, status, patient_id, procedure_id, date, covered_amount, total_amount, description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (
                hospital_id,
                insurance_id,
                status,
                patient_id,
                procedure_id,
                date,
                covered_amount,
                total_amount,
                description,
            )
            cursor.execute(sql, val)
            connection.commit()
            sql = "SELECT LAST_INSERT_ID()"  #select last created id
            cursor.execute(sql)
            claim_id = cursor.fetchone()[0]
            
            sql = "INSERT INTO edit_log (user_id, claim_id, edit_type) VALUES (%s, %s, %s)"
            val = (current_user.id, claim_id, "create")
            cursor.execute(sql, val)
            connection.commit()

        except Exception as e:
            # Rollback the transaction in case of error
            connection.rollback()
            print("Error: ", e)
        finally:
            # Ensure the connection is set back to autocommit mode
            connection.autocommit = True

        flash(f"Claim Added!", category="success")
        return redirect(url_for("claimpage"))

    cursor.execute("SELECT name FROM insurance")
    # Fetch all rows and store the names in the insurance_names list
    for row in cursor.fetchall():
        insurance_names.append(row[0])
    cursor.execute("SELECT name FROM hospital")
    # Fetch all rows and store the names in the hospital_names list
    for row in cursor.fetchall():
        hospital_names.append(row[0])
    return render_template(
        "addclaim.html",
        form=form,
        insurance_names=insurance_names,
        hospital_names=hospital_names,
    )


@myapp_obj.route("/addpatient", methods=["GET", "POST"])
@login_required
def addpatient():
    form = addPatientForm()
    if form.validate_on_submit():
        name = form.name.data
        date_of_birth = form.date_of_birth.data
        contact_info = form.contact_info.data
        sql = "INSERT INTO patient (name, date_of_birth, contact_info) VALUES (%s, %s, %s)"
        val = (name, date_of_birth, contact_info)
        cursor.execute(sql, val)
        connection.commit()

        return redirect(url_for("patientspage"))
    # Render the template with the patients data
    return render_template("addpatient.html", form=form)


@myapp_obj.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    if form.validate_on_submit():
        searched = form.searched.data
        search_by = form.search_by.data
        
        # Initialize an empty list to store the search results
        search_results = []
        
        # Perform the search based on the user's input
        if search_by == 'Patient':
            cursor.execute("SELECT * FROM claim WHERE patient_id IN (SELECT patient_id FROM patient WHERE name LIKE %s)", ('%' + searched + '%',))
        elif search_by == 'Hospital':
            cursor.execute("SELECT * FROM claim WHERE hospital_id IN (SELECT hospital_id FROM hospital WHERE name LIKE %s)", ('%' + searched + '%',))
        elif search_by == 'Insurance':
            cursor.execute("SELECT * FROM claim WHERE insurance_id IN (SELECT insurance_id FROM insurance WHERE name LIKE %s)", ('%' + searched + '%',))
        elif search_by == 'Procedure':
            cursor.execute("SELECT * FROM claim WHERE procedure_id IN (SELECT procedure_id FROM medical_procedure WHERE name LIKE %s)", ('%' + searched + '%',))
        else:
            flash('Invalid search criteria.', category='danger')
            return redirect(url_for('claimpage'))

        # Fetch the search results
        search_results = cursor.fetchall()
        session['search_results'] = search_results
        session['search_made'] = True

        #search history functionality
        sql = "INSERT INTO search_history (user_id, search_term, search_by) VALUES (%s, %s, %s)"
        val = (current_user.id, searched, search_by)
        cursor.execute(sql, val)
        connection.commit()
        # Redirect to the claimpage route with the search results
        return redirect(url_for('claimpage', search_results=search_results))
    
    return render_template("base.html", form=form)

