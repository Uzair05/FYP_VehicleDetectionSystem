import requests
import json
import unittest

from dev.lib.value_handlers import *

def login(officer_id, password):
    req = requests.get("http://127.0.0.1:5000/login",params={
        "officer_id":officer_id,
        "password":password
    })
    return json.loads(req.text)

def insertCamera(api_token, model, locx, locy, locn):
    req = requests.get("http://127.0.0.1:5000/insertCamera", params={
        "api_token": api_token,
        "model_number":model,
        "location_x":locx,
        "location_y":locy,
        "location_name":locn
    })
    return json.loads(req.text)

def insertOfficer(api_token, officer_id, password, name, district):
    req = requests.get("http://127.0.0.1:5000/insertOfficer", params={
        "api_token":api_token,
        "officer_id":officer_id,
        "password":password,
        "name":name,
        "district":district
    })
    return json.loads(req.text)

def insertVehicle(api_token, vehicle_type, license_plate_number, color, time_stolen):
    req = requests.get("http://127.0.0.1:5000/insertVehicle", params={
        "api_token":api_token,
        "vehicle_type":vehicle_type,
        "license_plate_number":license_plate_number,
        "color":color,
        "time_stolen":time_stolen
    })
    return json.loads(req.text)

def insertIncident(api_token, license_plate_number, time_stolen):
    req = requests.get("http://127.0.0.1:5000/insertIncidentReport", params={
        "api_token":api_token,
        "license_plate_number":license_plate_number,
        "time_stolen": time_stolen
    })
    return json.loads(req.text)
    
def createAlert(api_token, license_plate_number):
    req = requests.get("http://127.0.0.1:5000/noteLicensePlate", params={
        "api_token":api_token,
        "license_plate_number":license_plate_number
    })
    return json.loads(req.text)

login_api = login("#007", "0000")["api_token"]
camera_api = insertCamera(login_api, "CASIO", 0.9878, -7.8967, "Shawan Drive")["api_token"]

insertVehicle(login_api, "Car", "55aa", "blue", 10000)
insertIncident(login_api, "55aa", 10009)

insertVehicle(login_api, "Car", "5545", "blue", 10000)
insertIncident(login_api, "5545", 10009)

insertVehicle(login_api, "Car", "55ui", "blue", 10000)
insertIncident(login_api, "55ui", 10009)

insertVehicle(login_api, "Car", "5645", "blue", 10000)
insertIncident(login_api, "5645", 10009)


print(createAlert(camera_api, "55458"))
print(createAlert(camera_api, "5545"))

