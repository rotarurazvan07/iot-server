# Module Imports
"""
sudo apt-get install mariadb-server
sudo apt-get install mariadb-client

pip3 install mariadb

pip3 install flask

sudo systemctl restart mariadb.service
sudo systemctl restart mysql.service
"""

import mariadb
import sys
from flask import Flask
from flask import request
import random
import string
import datetime
from flask import jsonify

app = Flask(__name__)

# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user="****",
        password="****",
        host="****",
        port=3306,
        database="****",
        autocommit=True
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)
# Get Cursor
db = conn.cursor()

db.execute("CREATE TABLE IF NOT EXISTS User (" + \
                    "user_id bigint auto_increment primary key," + \
                    "email varchar(128) UNIQUE," + \
                    "password varchar(128)," + \
                    "api_token varchar(128) UNIQUE) ENGINE=InnoDB")
    
db.execute("CREATE TABLE IF NOT EXISTS Field (" + \
                    "field_id bigint auto_increment primary key," + \
                    "owner varchar(128)," + \
                    "name varchar(128)," + \
                    "value varchar(128)," + \
                    "timestamp DATETIME) ENGINE=InnoDB")

def get_random_string(length):
    # Random string with the combination of lower and upper case
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

@app.route('/')
def hello_world():
    return jsonify('success'), 200

@app.route('/register', methods=['GET'])
def register_user():
    email = request.args.get('email')
    password = request.args.get('pass')

    if password is None or email is None:
        return jsonify('Please input password and email')

    api_token = get_random_string(30)
    try:
        db.execute("INSERT INTO User (email, password, api_token) VALUES (?,?,?)",
                   (email,password, api_token))

        return jsonify(api_token)
    except:
        return jsonify("User already exists, use token")

@app.route('/recover/password', methods=['GET'])
def recover_password():
    
    if request.args.get("email") is None:
        return jsonify('Please add the email')
    if request.args.get("token") is None:
        return jsonify('Please add the token')
    db.execute("SELECT password FROM User WHERE email=? and api_token=?",(request.args.get("email"),request.args.get("token")))
    
    try:
        return jsonify([password for (password,) in db][0])
    except:
        return jsonify("Wrong email or token")

@app.route('/recover/token', methods=['GET'])
def recover_token():
    if request.args.get("email") is None:
        return jsonify('Please add the email')
    
    if request.args.get("pass") is None:
        return jsonify('Please add the password')
    
    db.execute("SELECT api_token FROM User WHERE email=? and password=?",(request.args.get("email"),request.args.get("pass")))
    
    try:
        return jsonify([api_token for (api_token,) in db][0])
    except:
        return jsonify("Wrong email or password");

@app.route('/api/add', methods=['GET'])
def add_to_fields():
    if len(request.args) == 0:
        return jsonify('Provide token and fields')

    if request.args.get("token") is None:
        return jsonify('Please add the token')

    email = None
    
    # get email from token
    db.execute("SELECT email from User where api_token=?", (request.args.get("token"),))

    try:
        email = [user_email for (user_email,) in db][0]
    except IndexError:    
        return jsonify("Wrong token")

    for arg in request.args:
        if arg != "token":
            db.execute("INSERT INTO Field (owner, name, value, timestamp) VALUES (?,?,?,?)",(email,arg,request.args.get(arg),datetime.datetime.now()))
            
    return_message = "\"{"
    for arg in request.args:
        if arg != "token":
            db.execute("SELECT COUNT(*) FROM Field where owner=? and name=?",(email,arg))
            return_message += arg + "=" + str([row for row in db][0][0]) + "&"
    return_message = return_message[:-1] + "}\"\n"
    return return_message, 200


@app.route('/api/get', methods=['GET'])
def get_fields(last=False):
    if len(request.args) == 0:
        return jsonify('Provide token and fields')

    if request.args.get("token") is None:
        return jsonify('Please add the token')

    if len(request.args) == 1 and request.args.get("token") is not None:
        return jsonify('Please provide fields')

    email = None
    
    # get email from token
    db.execute("SELECT email from User where api_token=?", (request.args.get("token"),))

    try:
        email = [user_email for (user_email,) in db][0]
    except IndexError:    
        return jsonify("Wrong token")

    values = dict()
    for arg in request.args:
        if arg != "token":
            
            values[arg] = []
            try:
                if last is True:
                    db.execute("SELECT value, timestamp from Field where owner=? and name=? ORDER BY field_id DESC LIMIT 1",(email, arg))
                else:
                    db.execute("SELECT value, timestamp from Field where owner=? and name=?",(email,arg))
                for row in db:
                    values[arg].append((row[0], row[1]))
            except:
                continue
  
    
    if last is True:
        last_message = "\"{"
        for arg in request.args:
            if arg != "token":
                    last_message += arg
                    last_message += "="
                    
                    try:
                        last_message += str(values[arg][0][0])
                    except IndexError:
                        last_message += "/"
                
                    last_message += "&"
        return last_message[:-1] + "}\"\n"
    else:
        return jsonify(values), 200

@app.route('/api/get/last', methods=['GET'])
def get_last_field():
    return get_fields(last=True)

@app.route('/api/clear', methods=['GET'])
def clear_field():
    if len(request.args) == 0:
        return jsonify('Provide token and fields')

    if request.args.get("token") is None:
        return jsonify('Please add the token')

    if len(request.args) == 1 and request.args.get("token") is not None:
        return jsonify('Please provide fields')

    email = None
    
    # get email from token
    db.execute("SELECT email from User where api_token=?", (request.args.get("token"),))

    try:
        email = [user_email for (user_email,) in db][0]
    except IndexError:    
        return jsonify("Wrong token")
    
    for arg in request.args:
        if arg != "token":
            try:
                db.execute("DELETE FROM Field where owner=? and name=?",(email,arg))
            except:
                continue
    
    db.execute("OPTIMIZE TABLE Field")
    return '1\n'

if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True)
