from typing import *
from flask import Flask, request
import sqlite3
import time
import math
from lib.value_handlers import * # get functions and class from library



app = Flask(__name__)

@app.route('/login', methods=['GET'])
def login():
    officer_id:Optional[str] = request.args.get("officer_id", None, type=str)
    password:Optional[str] = request.args.get("password", None, type=str)

    if not((officer_id is not None) and (password is not None)):
        return generateStatus(False, "Officer_id or Password Incorrect -> None value received")
        
    password = hash(password)

    conn = sqlite3.connect("./database/stolenVehiclesDatabase.db")
    cursor = conn.execute(f"""
        SELECT API FROM OFFICER_LOGIN WHERE OFFICER_ID=\"{officer_id}\" AND PASSWORD=\"{password}\";
    """)
    res = [row for row in cursor]
    conn.close()

    if (len(res)==0):
        return generateStatus(False, "Officer_id or Password Incorrect -> Entry not found")
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

    api = genAPI_camera(loc_name, loc_x, loc_y, model_number)
    
    conn = sqlite3.connect("./database/stolenVehiclesDatabase.db")
    conn.execute(
        "INSERT INTO CAMERA (MODEL_NUMBER, LOCATION_X, LOCATION_Y, LOCATION_NAME, API) VALUES (?, ?, ?, ?, ?);",
        (model_number, loc_x, loc_y, loc_name, api)
        )
    conn.commit()
    conn.close()
    return generateStatus(True, "Camera Registration Success", {"api_token":api})

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
    return generateStatus(True, "")

@app.route('/insertVehicle', methods=['GET'])
def insertVehicle():
    # test API token; only officers can add vehicle
    officer_api:Optional[str] = request.args.get("api_token", None, type=str)
    t, m = testOfficerAPI(officer_api)
    if (not t):
        return generateStatus(False, m)
    
    vehicle_type:Optional[str] = request.args.get("vehicle_type", None, type=str)
    license_plate_number:Optional[str] = request.args.get("license_plate_number", None, type=str)
    color:Optional[str] = request.args.get("color", None, type=str)
    time_stolen:Optional[int] = request.args.get("time_stolen", None, type=int)

    if ((vehicle_type is None) or (license_plate_number is None) or (color is None) or (time_stolen is None)):
        return generateStatus(False, "Invalid input")
    
    t, m = testLicensePlate(license_plate_number)
    if (not t):
        return generateStatus(False, m)
    
    conn = sqlite3.connect("./database/stolenVehiclesDatabase.db")
    conn.execute("INSERT INTO STOLEN_VEHICLE (V_TYPE, LICENSE_PLATE_NUMBER, COLOR, TIME_STOLEN) VALUES (?, ?, ?, ?);", 
        (vehicle_type, license_plate_number, color, time_stolen))
    conn.commit()
    conn.close()
    return generateStatus(True, "")

@app.route('/removeVehicle', methods=['GET'])
def removeVehicle():
    # test API token; only officers can remove vehicle
    officer_api:Optional[str] = request.args.get("api_token", None, type=str)
    t, m = testOfficerAPI(officer_api)
    if (not t):
        return generateStatus(False, m)

    license_plate_number:Optional[str] = request.args.get("license_plate_number", None, type=str)
    if (license_plate_number is None):
        return generateStatus(False, "License Plate input invalid")
    elif testLicensePlate(license_plate_number)[0]:
        return generateStatus(False, "License plate does not exist")
    else:
        conn = sqlite3.connect("./database/stolenVehiclesDatabase.db")
        conn.execute(f"DELETE FROM STOLEN_VEHICLE WHERE LICENSE_PLATE_NUMBER=\"{license_plate_number}\"")
        conn.commit()
        conn.close()
        return generateStatus(True)

@app.route('/insertIncidentReport', methods=["GET"])
def insertIncidentReport():
    # test API token; only officers can add incident report
    officer_api:Optional[str] = request.args.get("api_token", None, type=str)
    t, m = testOfficerAPI(officer_api)
    if (not t):
        return generateStatus(False, m)

    #must insert vehicle before creating incident report
    license_plate_number:Optional[str] = request.args.get("license_plate_number", None, type=str)
    time_stolen:Optional[int] = request.args.get("time_stolen", None, type=int)
    if ((license_plate_number is None) or (time_stolen is None)):
        return generateStatus(False, "Invalid Input")

    stolenVehicleID = getVehicleID_from_License(license_plate_number)
    if (stolenVehicleID is None):
        return generateStatus(False, "License plate does not exist")
    officerID = getOfficerID_from_API(officer_api)
    if (officerID is None):
        return generateStatus(False, "Officer ID does not exist")

    conn = sqlite3.connect("./database/stolenVehiclesDatabase.db")
    conn.execute(
        "INSERT INTO INCIDENT_REPORT (SV_ID, OFFICER_ID, TIME_FILED) VALUES (?, ?, ?);",
        (stolenVehicleID, officerID, time_stolen)
        )
    conn.commit()
    conn.close()
    return generateStatus(True, "")

@app.route('/removeIncidentReport', methods=["GET"])
def removeIncidentReport():
    # test API token; only officers can add incident report
    officer_api:Optional[str] = request.args.get("api_token", None, type=str)
    t, m = testOfficerAPI(officer_api)
    if (not t):
        return generateStatus(False, m)

    #must insert vehicle before creating incident report
    license_plate_number:Optional[str] = request.args.get("license_plate_number", None, type=str)
    if (license_plate_number is None):
        return generateStatus(False, "Invalid Input")

    stolenVehicleID = getVehicleID_from_License(license_plate_number)
    if (stolenVehicleID is None):
        return generateStatus(False, "License plate does not exist")
    officerID = getOfficerID_from_API(officer_api)
    if (officerID is None):
        return generateStatus(False, "Officer ID does not exist")

    
    conn = sqlite3.connect("./database/stolenVehiclesDatabase.db")
    conn.execute(
        f"DELETE FROM INCIDENT_REPORT WHERE SV_ID={stolenVehicleID} AND OFFICER_ID=\"{officerID}\";"
        )
    conn.commit()
    conn.close()
    return generateStatus(True, "")

@app.route("/testLicensePlate", methods=["GET"])
def testLicensePlate():
    time_ = math.floor(time.time()) #note time alert was recieved
    # test API token; only cameras can test for properties
    camera_api:Optional[str] = request.args.get("api_token", None, type=str)
    
    t, m = testCameraAPI(camera_api)
    if (not t): return generateStatus(False, m)

    cameraID = getCameraID_from_API(camera_api)
    if cameraID is None: return generateStatus(False, "Camera ID not found")
    
    license_plate_number:Optional[str] = request.args.get("license_plate_number", None, type=str)
    if (license_plate_number is None): return generateStatus(False, "Incorrect Input")
    
    
    threshold = 2 #edit threshold for edit distance
    res = sortByEditDistance(license_plate_number)
    res_:str = ""
    if (res[0][1] == 0):
        res_ = res[0][0]
    else:
        res_ = ";".join([i[0] for i in res if i[1]<=threshold])
    
    if (len(res_)>0):
        conn = sqlite3.connect("./database/stolenVehiclesDatabase.db")
        conn.execute(
            "INSERT INTO SUSPECT (POSSIBLE_SV_ID, CAMERA_ID, TIME_CAUGHT) VALUES (?, ?, ?);",
            (res_, cameraID, time_)
        )
        conn.commit()
        conn.close()
    return generateStatus(True, "")

    
app.run(host='0.0.0.0')



#TODO: insertOfficer Unique check







# DONE: put incident report --> DONE: Test for (vehicle); DONE: Test for (officer)
# DONE: remove incident report 


# DONE: put camera details
# DONE: put officer details
# DONE: officer login
# DONE: put car details
# DONE: remove car details

# DONE: Test for (camera)
# DONE: get from database for alert
# DONE: get from database for testing
# DONE: put in database for alert --> # TODO: human moderator edit
