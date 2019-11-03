from flask import Flask, request, redirect, render_template, make_response, session, send_from_directory
from flask_socketio import SocketIO
import MySQLdb
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


@app.route("/board")
def board():
    return render_template("chat.html")


@socketio.on("connect")
def clientConn():
    res = query("SELECT * FROM contestants", [])
    for r in res:
        json2 = {}
        json2['contID'] = r[0]
        json2['contName'] = r[1]
        json2['totalRaised'] = r[2]
        socketio.emit("newContestant", json2)
    return ""


@app.route("/adddonation", methods=['GET', 'POST'])
def addDonation():
    res = query("SELECT * FROM contestants WHERE id = %s", request.form['contID'])
    query("INSERT INTO donations (donateTo, amount, notes) VALUES (%s,%s,%s)", [request.form['contID'], request.form['amount'], request.form['notes']])
    newTotal = int(res[0][2]) + int(request.form['amount'])
    query("UPDATE contestants SET totalraised = %s WHERE id = %s", [newTotal, request.form['contID']])
    json = {}
    #json['contName'] = request.form['contName']
    json['contID'] = request.form['contID']
    json['newAmount'] = newTotal
    json['donatedAmount'] = request.form['amount']
    socketio.emit("updateTotal", json)
    return ""


# Misc Functions

def query(query, values):
    conn.ping(True)
    cur = conn.cursor()
    cur.execute(query, values)
    conn.commit()
    return cur.fetchall()


def convertSQLDateTimeToTimestamp(value):
    return time.mktime(time.strptime(value, '%Y-%m-%d %H:%M:%S'))


def encrypt_password(password):
    return pwd_context.encrypt(password)


def check_encrypted_password(password, hashed):
    return pwd_context.verify(password, hashed)


if __name__ == '__main__':
    conn = MySQLdb.connect(host=Config.host,  # your host, usually localhost
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
