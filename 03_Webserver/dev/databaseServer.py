from flask import Flask, request
import typing
import sqlite3

app = Flask(__name__)


@app.route('/login', methods=['GET'])
def login():
    conn = sqlite3.connect("./database/stolenVehiclesDatabase.db")



# TODO: put car details
# TODO: put officer details
# TODO: put incident report
# TODO: put camera details



# TODO: get from database for alert
# TODO: get from database for testing
# TODO: put in database for alert --> # TODO: human moderator edit