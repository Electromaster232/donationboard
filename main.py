from flask import Flask, request, redirect, render_template, make_response, session, send_from_directory
from flask_socketio import SocketIO
import mysql.connector
import random
import time
from passlib.context import CryptContext
import secrets
from config import Config


app = Flask(__name__)
app.config['SECRET_KEY'] = 'odL1}0a=}E:ybjfY.%rH"Ys5?6;J<^'
socketio = SocketIO(app)


@app.route("/")
def home():
    return render_template("index.html")


@socketio.on("connect")
def onConnect():
    all = query("SELECT * FROM contestants ORDER BY totalraised ASC", [])
    index = 1
    for x in all:
        json2 = {}
        print(x[0])
        json2['contID'] = x[0]
        json2['place'] = index
        socketio.emit("updatePlace", json2)
        index = index + 1
        json = {}
         # json['contName'] = request.form['contName']
        json['contID'] = x[0]
        json['newAmount'] = x[2]
        json['donatedAmount'] = x[2]
        socketio.emit("updateTotal", json)

@app.route("/board")
def board():
    return render_template("chat.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/adddonation", methods=['GET', 'POST'])
def addDonation():
    res = query("SELECT * FROM contestants WHERE id = %s", [request.form['contID']])
    query("INSERT INTO donations (donateTo, amount, notes) VALUES (%s,%s,%s)", [request.form['contID'], request.form['amount'], "None"])
    newTotal = int(res[0][2]) + int(request.form['amount'])
    query("UPDATE contestants SET totalraised = %s WHERE id = %s", [newTotal, request.form['contID']])
    all = query("SELECT * FROM contestants ORDER BY totalraised ASC", [])
    index = 1
    for x in all:
        json2 = {}
        print(x[0])
        json2['contID'] = x[0]
        json2['place'] = index
        socketio.emit("updatePlace", json2)
        index = index + 1
    json = {}
    #json['contName'] = request.form['contName']
    json['contID'] = request.form['contID']
    json['newAmount'] = newTotal
    json['donatedAmount'] = request.form['amount']
    socketio.emit("updateTotal", json)
    return ""


# Misc Functions

def query(query, values):
    cnx.ping(True)
    cur = cnx.cursor()
    cur.execute(query, values)
    try:
        res = cur.fetchall()
    except mysql.connector.errors.InterfaceError:
        cnx.commit()
        return
    return res


def convertSQLDateTimeToTimestamp(value):
    return time.mktime(time.strptime(value, '%Y-%m-%d %H:%M:%S'))


def encrypt_password(password):
    return pwd_context.encrypt(password)


def check_encrypted_password(password, hashed):
    return pwd_context.verify(password, hashed)


if __name__ == '__main__':
    cnx = mysql.connector.connect(host=Config.host,  # your host, usually localhost
                         user=Config.user,  # your username
                         passwd=Config.passwd,  # your password
                         db=Config.db)
    random.seed()
    pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=30000
    )
    joined = {}
    sockettokens = {}
    socketio.run(app)
