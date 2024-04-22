from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import mysql.connector

myapp_obj = Flask(__name__) #flask object
bcrypt = Bcrypt(myapp_obj)  #flask library to hash passwords instead of storing them as it is
login_manager = LoginManager(myapp_obj) #for login
login_manager.login_view = "loginPage"  #for login
login_manager.login_message_category = "info" #for login

connection = mysql.connector.connect(
    host="localhost",
    password="Hello123!",
    user="root",
    database="insurance"
)


myapp_obj.config['SECRET_KEY'] = 'abc'      #DO NOT CHANGE THIS HEXADECIMAL SECRET_KEY

from app import routes

