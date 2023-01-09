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
        
    password = hash(password)

    conn = sqlite3.connect("./database/stolenVehiclesDatabase.db")
    cursor = conn.execute(f"""
        SELECT API from OFFICER_LOGIN where OFFICER_ID=\"{officer_id}\" and PASSWORD=\"{password}\";
    """)
    res = [row for row in cursor]
    conn.close()

    if (len(res)==0):
        return generateStatus(False, "Officer_id or Password Incorrect")
    else:
        # update api token for each login.
        api = genAPI(password, officer_id)
        conn = sqlite3.connect("./database/stolenVehiclesDatabase.db")
        conn.execute(f"UPDATE OFFICER_LOGIN SET API=\"{api}\" WHERE OFFICER_ID=\"{officer_id}\"")
        conn.commit()
        conn.close()
        return generateStatus(True, "Login Success", {"api_token":api})
    
@app.route('/insertCamera', methods=['GET'])
def insertCamera():
    officer_api:Optional[str] = request.args.get("api_token", None, type=str)
    t, m = testOfficerAPI(officer_api)
    if (not t):
        return generateStatus(False, m)

    model_number:Optional[str] = request.args.get("model_number", None, type=str)
    loc_x:Optional[float] = request.args.get("location_x", None, type=float)
    loc_y:Optional[float] = request.args.get("location_y", None, type=float)
    loc_name:Optional[str] = request.args.get("location_name", None, type=str)

    if ((loc_x is None) or (loc_y is None) or (loc_name is None)):
        return generateStatus(False, "Invalid Input")

    api = genAPI_camera()
    
    conn = sqlite3.connect("./database/stolenVehiclesDatabase.db")
    conn.execute(
        "INSERT INTO CAMERA (MODEL_NUMBER, LOCATION_X, LOCATION_Y, LOCATION_NAME, API) VALUES (?, ?, ?, ?, ?);",
        (model_number, loc_x, loc_y, loc_name)
        )
    conn.commit()
    conn.close()
    return generateStatus(True, "")

@app.route('/insertOfficer', methods=['GET'])
def insertOfficer():
    officer_api:Optional[str] = request.args.get("api_token", None, type=str)
    t, m = testOfficerAPI(officer_api)
    if (not t):
        return generateStatus(False, m)

    officer_id:Optional[str] = request.args.get("officer_id", None, type=str)
    password:Optional[str] = request.args.get("password", None, type=str)
    if ((officer_id is None) or (password is None)):
        return generateStatus(False, "Invalid Email or Password")
    

    name:Optional[str] = request.args.get("name", None, type=str)
    district:Optional[str] = request.args.get("district", None, type=str)
    if ((name is None) or (district is None)):
        return generateStatus(False, "Invalid Name or District")

    password = hash(password)
    api = genAPI(password, officer_id)

    conn = sqlite3.connect("./database/stolenVehiclesDatabase.db")
    conn.execute(
        "INSERT INTO OFFICER (OFFICER_ID, NAME, DISTRICT) VALUES (?, ?, ?);", 
        (officer_id, name, district)
    )
    conn.commit()
    conn.execute(
        "INSERT INTO OFFICER_LOGIN (OFFICER_ID, PASSWORD, API) VALUES (?, ?, ?);", 
        (officer_id, password, api)
    )
    conn.commit()
    conn.close()

    
    

           
    
    # conn = sqlite3.connect("./database/stolenVehiclesDatabase.db")
    # conn.execute(
    #     "INSERT INTO CAMERA (MODEL_NUMBER, LOCATION_X, LOCATION_Y, LOCATION_NAME) VALUES (?, ?, ?, ?);",
    #     (model_number, loc_x, loc_y, loc_name)
    #     )
    # conn.commit()
    # conn.close()
    return generateStatus(True, "")





# TODO: put car details
# TODO: remove car details
# TODO: put incident report --> TODO: Test for (camera|vehicle); DONE: Test for (officer)
# TODO: remove incident report 


# DONE: put camera details
# DONE: put officer details
# DONE: officer login


# TODO: get from database for alert
# TODO: get from database for testing
# TODO: put in database for alert --> # TODO: human moderator edit
