import json
from twilio.rest import Client
from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify
from datetime import timedelta
from flask_simple_geoip import SimpleGeoIP
from flask_sqlalchemy import SQLAlchemy
import time

app = Flask(__name__)
app.secret_key = "super secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(seconds=30)
db = SQLAlchemy(app)
app.config.update(GEOIPIFY_API_KEY='at_NyEEpM3A5sHPdCu2a7JYhjnemm2be')
# Initialize the extension
simple_geoip = SimpleGeoIP(app)
account_sid = "ACfa14eee3628aa0aaaccbef4f66466f35"
auth_token = "082d316e544b61a4ca29bcc52e2d1c47"
client = Client(account_sid, auth_token)


@app.route("/", methods=["POST", "GET"])
def home():
    print("********")
    if request.method == "POST":
        process_message(request.form["name"], request.form["email"], request.form["msg"])
    parse_geo_info()
    return render_template("index.html")


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


def process_message(name, email, msg):
    msg = Messages(name, email, msg)
    db.session.add(msg)
    db.session.commit()


@app.route("/database", methods=["POST", "GET"])
def message_database():
    all_messages = Messages.query.filter_by().all()
    return render_template("database.html", all_messages=all_messages)


# database model
class Location(db.Model):
    city = db.Column(db.String(100))
    ip_address = db.Column(db.String(100))
    time = db.Column('time', db.Float, primary_key=True)

    def __init__(self, city, ip_address):
        self.city = city
        self.ip_address = ip_address
        self.time = int(time.time())


def parse_geo_info():
    geoip_data = simple_geoip.get_geoip_data()
    location_info = jsonify(data=geoip_data)
    info = json.loads(location_info.get_data())
    print(info)
    city = info["data"]["location"]["city"]
    ip_address = info["data"]["ip"]
    country = info["data"]["location"]["country"]
    region = info["data"]["location"]["region"]
    process_location(city, ip_address)


def process_location(city, ip_address):
    location = Location(city, ip_address)
    db.session.add(location)
    db.session.commit()
    send_text_message(city, ip_address)


@app.route("/location", methods=["POST", "GET"])
def location_database():
    all_locations = Location.query.filter(Location.city != "Hong Kong").all()
    return render_template("location.html", all_locations=all_locations)


def send_text_message(city, ip_address):
    if city != "Hone Kong" and city is not None:
        call = client.messages.create(body=city + ip_address, to="+8615810751695", from_="+19388883198")
        print(call.sid)


if __name__ == "__main__":
    db.create_all()
    app.run(host="0.0.0.0", port=80, debug=True)
    # app.run(debug=True)
