import mysql.connector
import bcrypt
from datetime import datetime, timedelta, date
from uuid import uuid4

# Database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'NULL',
    'database': 'carculator'
}

# Lockout variables
failed_attempts = 0
lockout_until = None
LOCKOUT_DURATION = 300

# Hardcoded admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = bcrypt.hashpw("123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def connect_db():
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def is_locked_out():
    global lockout_until
    if lockout_until and datetime.now() < lockout_until:
        remaining = (lockout_until - datetime.now()).seconds
        print(f"Too many failed attempts. Try again in {remaining} seconds.")
        return True
    if lockout_until and datetime.now() >= lockout_until:
        reset_lockout()
    return False

def reset_lockout():
    global failed_attempts, lockout_until
    failed_attempts = 0
    lockout_until = None
