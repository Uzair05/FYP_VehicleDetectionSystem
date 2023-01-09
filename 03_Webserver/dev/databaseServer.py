from flask import Flask, request
import typing
import sqlite3

app = Flask(__name__)




# TODO: put car details
# TODO: put officer details
# TODO: put incident report
# TODO: put camera details

@app.route('/props', methods=['GET'])
def props():
    pass



# TODO: get from database for alert
# TODO: get from database for testing
# TODO: put in database for alert --> # TODO: human moderator edit