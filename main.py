import json
from flask_simple_geoip import SimpleGeoIP
from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
import time

# from pip._vendor import requests

app = Flask(__name__)
app.secret_key = "super secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(seconds=30)
db = SQLAlchemy(app)
app.config.update(GEOIPIFY_API_KEY='at_NyEEpM3A5sHPdCu2a7JYhjnemm2be')
# Initialize the extension
simple_geoip = SimpleGeoIP(app)


# database model
class Messages(db.Model):
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    msg = db.Column(db.String(100))
    time = db.Column('time', db.Float, primary_key=True)

    def __init__(self, name, email, msg):
        self.name = name
        self.email = email
        self.msg = msg
        self.time = int(time.time())


@app.route("/", methods=["POST", "GET"])
def home():
    print("********")
    if request.method == "POST":
        process_message(request.form["name"], request.form["email"], request.form["msg"])
    return render_template("index.html")


def process_message(name, email, msg):
    msg = Messages(name, email, msg)
    db.session.add(msg)
    db.session.commit()


@app.route("/database", methods=["POST", "GET"])
def message_database():
    all_messages = Messages.query.filter_by().all()
    return render_template("database.html", all_messages=all_messages)


@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    # print(jsonify({'ip': request.remote_addr}), 200)
    geoip_data = simple_geoip.get_geoip_data()
    return jsonify(data=geoip_data)
    # return render_template("get_my_ip.html")


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
