from typing import Union, Optional
from flask import Flask, request
import sqlite3
from lib.value_handlers import * # get functions and class from library



app = Flask(__name__)


@app.route('/login', methods=['GET'])
def login():
    officer_id:Optional[str] = request.args.get("officer_id", None, type=str)
    password:Optional[str] = request.args.get("password", None, type=str)

    if not((officer_id is not None) and (password is not None)):
        return generateStatus(False, "Officer_id or Password Incorrect")
        
    password = hash(str(password))

    conn = sqlite3.connect("./database/stolenVehiclesDatabase.db")
    cursor = conn.execute(f"""
        SELECT API from OFFICER_LOGIN where OFFICER_ID=\"{officer_id}\" and PASSWORD=\"{password}\";
    """)
    res = [row for row in cursor]
    conn.close()

    if (len(res)==0):
        return generateStatus(False, "Officer_id or Password Incorrect")
    else:
        return generateStatus(True, "Login Success", {"API":res[0][0]})
    



# TODO: put car details
# TODO: put officer details
# TODO: put incident report
# TODO: put camera details



# TODO: get from database for alert
# TODO: get from database for testing
# TODO: put in database for alert --> # TODO: human moderator edit