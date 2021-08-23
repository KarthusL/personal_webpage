import json
# from twilio.rest import Client
from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify
from datetime import timedelta
from flask_simple_geoip import SimpleGeoIP
from flask_sqlalchemy import SQLAlchemy
import time
import requests

# basic app config
app = Flask(__name__)
app.secret_key = "super secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(seconds=30)

# database setup
db = SQLAlchemy(app)

# simple_geoip setup
app.config.update(GEOIPIFY_API_KEY='at_vYWXCMrBCR2BQu7NsmpMYs73rrP7F')
simple_geoip = SimpleGeoIP(app)

# twillow setup
# with open('twillow_auth') as f:
#     twillow_auth = json.load(f)
# account_sid = twillow_auth["account_sid"]
# auth_token = twillow_auth["auth_token"]
# client = Client(account_sid, auth_token)

# abuseipdb setup
url = 'https://api.abuseipdb.com/api/v2/check'


@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        process_message(request.form["name"], request.form["email"], request.form["msg"])
    print("---home---")
    # parse_geo_info()
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
    is_white_list, abuse_score = check_abuse_ip(ip_address)
    if is_white_list is True or abuse_score < 25:
        send_text_message(city, ip_address)
        process_location(city, ip_address)


def check_abuse_ip(ip_address):
    querystring = {
        'ipAddress': ip_address,
        'maxAgeInDays': '180'
    }
    headers = {
        'Accept': 'application/json',
        'Key': 'aed2d305737f998e1e97d056a0e35399622bdd8078f98eca014be4089b1b636e686eb44ea1bd1133'
    }
    response = requests.request(method='GET', url=url, headers=headers, params=querystring)
    decodedResponse = json.loads(response.text)
    is_white_list = decodedResponse["data"]["isWhitelisted"]
    abuse_score = decodedResponse["data"]["abuseConfidenceScore"]
    print(json.dumps(decodedResponse, sort_keys=True, indent=4))
    return is_white_list, abuse_score


def process_location(city, ip_address):
    location = Location(city, ip_address)
    db.session.add(location)
    db.session.commit()


@app.route("/location", methods=["POST", "GET"])
def location_database():
    all_locations = Location.query.filter(Location.city != "Hong Kong").all()
    return render_template("location.html", all_locations=all_locations)


def send_text_message(city, ip_address):
    call = client.messages.create(body=city + ip_address, to="+8615810751695", from_="+19388883198")
    print("message sent")
    print(call.sid)


@app.errorhandler(500)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


if __name__ == "__main__":
    db.create_all()
    app.run(host="0.0.0.0", port=80, debug=True)
    # app.run(host="127.0.0.1", debug=True)
    app.run(debug=True)
