from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request
import random
import string
import datetime
from flask import jsonify

app = Flask(__name__)

### ONLY TO BE USED ON pythonanywhere.com PLATFORM ###

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="****",
    password="****",
    hostname="****",
    databasename="****",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "Users"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    api_token = db.Column(db.String(120), unique=True, nullable=False)

class Field(db.Model):
    __tablename__= "Field"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(db.String(80))
    name = db.Column(db.String(80))
    value = db.Column(db.String(80))
    timestamp = db.Column(db.DateTime)

# Run this only once, after that, comment it
db.create_all()


def get_random_string(length):
    # Random string with the combination of lower and upper case
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

@app.route('/')
def hello_world():
    return jsonify('success\n'), 200

@app.route('/register', methods=['GET'])
def register_user():
    email = request.args.get('email')
    password = request.args.get('pass')

    if password is None or email is None:
        return jsonify('Please input password and email')

    api_token = get_random_string(8)
    user = User(email=email, password=password, api_token=api_token)

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify(api_token)
    except:
        return jsonify('User already registered, use token')

@app.route('/api/add', methods=['GET'])
def add_to_fields():
    if len(request.args) == 0:
        return jsonify('Provide token and fields')

    if request.args.get("token") is None:
        return jsonify('Please add the token')

    email = None
    # get email from token
    try:
        email, = db.session.execute("SELECT email from Users where api_token='{token}'".format(token=request.args.get("token")))
    except ValueError:
        return jsonify('Invalid token')

    for arg in request.args:
        if arg != "token":
            try:
                field = Field(owner=email[0],
                        name=arg,
                        value=request.args.get(arg),
                        timestamp=datetime.datetime.now())
                db.session.add(field)
                db.session.commit()
            except:
                continue
    return jsonify('succes'), 200

@app.route('/api/get', methods=['GET'])
def get_fields(last=False):
    if len(request.args) == 0:
        return jsonify('Provide token and fields')

    if request.args.get("token") is None:
        return jsonify('Please add the token')

    if len(request.args) == 1 and request.args.get("token") is not None:
        return jsonify('Please proive fields')

    email = None
    # get email from token
    try:
        email, = db.session.execute("SELECT email from Users where api_token='{token}'".format(token=request.args.get("token")))
    except ValueError:
        return jsonify('Invalid token')

    values = dict()

    for arg in request.args:
        if arg != "token":
            values[arg] = []
            if last is True:
                result = db.session.execute("SELECT value, timestamp from Field where owner='{email}' and name='{name}' ORDER BY ID DESC LIMIT 1".format(email=email[0], name=arg))
            else:
                result = db.session.execute("SELECT value, timestamp from Field where owner='{email}' and name='{name}'".format(email=email[0], name=arg))
            for row in result:
                values[arg].append((row[0], row[1]))
    if last is True:
        last_message = "\"{"
        for arg in request.args:
            if arg != "token":
                last_message += arg
                last_message += "="
                last_message += str(values[arg][0][0])
                last_message += "&"
        return last_message[:-1] + "}\"\n"
    else:
        return jsonify(values), 200
    
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
    try:
        email, = db.session.execute("SELECT email from Users where api_token='{token}'".format(token=request.args.get("token")))
    except ValueError:
        return jsonify('Invalid token')
    
    for arg in request.args:
        if arg != "token":
            try:
                db.session.execute("DELETE FROM Field where owner='{email}' and name='{name}'".format(email=email[0], name=arg))
            except:
                continue
    return '1\n'
                
@app.route('/api/get/last', methods=['GET'])
def get_last_field():
    return get_fields(last=True)


