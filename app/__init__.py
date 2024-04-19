from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import mysql.connector

myapp_obj = Flask(__name__) 
bcrypt = Bcrypt(myapp_obj)  #flask library to hash passwords for security
login_manager = LoginManager(myapp_obj) 

connection = mysql.connector.connect(  #change details here to match your mysql db
    host="localhost",
    password="", 
    user="root", 
    database="insurance"
)


myapp_obj.config['SECRET_KEY'] = 'abc'     
