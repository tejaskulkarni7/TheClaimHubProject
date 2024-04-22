from app import login_manager
from flask_login import UserMixin
import mysql.connector
from app.__init__ import connection




class User(UserMixin):
    def __init__(self, user_id, username, firstname, lastname, email_address, password_hash, user_type, insurance_id, hospital_id):
        self.id = user_id
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.email_address = email_address
        self.password_hash = password_hash
        self.user_type = user_type
        self.insurance_id = insurance_id
        self.hospital_id = hospital_id

        
@login_manager.user_loader
def load_user(user_id):
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM User WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    if user_data:
        user = User(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4], user_data[5], user_data[6], user_data[7], user_data[8])
        
        cursor.close()
        return user
    cursor.close()
    return None