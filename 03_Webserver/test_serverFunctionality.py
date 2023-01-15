import requests
import json
import unittest
import time 
import math


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

def removeVehicle(api_token, license_plate_number):
    req = requests.get("http://127.0.0.1:5000/removeVehicle", params={
        "api_token":api_token,
        "license_plate_number":license_plate_number,
    })
    return json.loads(req.text)

def insertIncident(api_token, license_plate_number, time_stolen):
    req = requests.get("http://127.0.0.1:5000/insertIncidentReport", params={
        "api_token":api_token,
        "license_plate_number":license_plate_number,
        "time_stolen": time_stolen
    })
    return json.loads(req.text)
    
def removeIncident(api_token, license_plate_number):
    req = requests.get("http://127.0.0.1:5000/removeIncidentReport", params={
        "api_token":api_token,
        "license_plate_number":license_plate_number,
    })
    return (json.loads(req.text))

def createAlert(api_token, license_plate_number):
    req = requests.get("http://127.0.0.1:5000/noteLicensePlate", params={
        "api_token":api_token,
        "license_plate_number":license_plate_number
    })
    return json.loads(req.text)
    

class Testing(unittest.TestCase):
    def testLogin(self):
        self.assertTrue(login("#007", "0000")["Success"], "Login should Succeed")
        self.assertFalse(login("#007", "9000")["Success"], "Login should Fail")
        self.assertFalse(login("#001", "0000")["Success"], "Login should Fail")

    def testCameraInsert(self):
        self.camera = insertCamera(login("#007", "0000")["api_token"], "CANON350", 19.8767, -7.8967, "Sha wan drive")

        self.assertTrue(self.camera["Success"], "Camera insert should succeed")
        self.assertNotEqual(self.camera["api_token"], None, "Token api should exist")

        self.res_ = insertCamera("1234567", "CANON350", 19.8797, -7.3967, "Sha wan drive1")
        self.assertFalse(self.res_["Success"], "Camera insert should Fail")
        self.assertFalse("api_token" in self.res_, "Token api should not exist")

    def testInsertOfficer(self):
        self.newOfficer = insertOfficer(login("#007", "0000")["api_token"], "#008", "0001", "Uzair Bin", "Wanchai")
        
        self.assertTrue(self.newOfficer["Success"], "Should be able to register")
        
        self.newOfficer_1 = insertOfficer(login("#008", "0001")["api_token"], "#009", "0002", "Chen Wang", "Wanchai")
        self.assertTrue(self.newOfficer_1["Success"], "Should be able to register")

        self.newOfficer_2 = insertOfficer("abcd", "#010", "0003", "Chen Wang", "Wanchai")
        self.assertFalse(self.newOfficer_2["Success"], "Should fail able to register -> incorrect token")

        #TODO: test for unique inputs
    
    def testInsertVehicle(self):
        self.insertVehicle = insertVehicle(
            login("#008", "0001")["api_token"],
            "car",
            "111244",
            "blue",
            math.floor(time.time())
        )
        self.assertTrue(self.insertVehicle["Success"])

        self.insertVehicle_ = insertVehicle(
            login("#008", "0001")["api_token"],
            "van",
            "111244",
            "green",
            math.floor(time.time())
        )
        self.assertFalse(self.insertVehicle_["Success"])

        self.insertVehicle_ = insertVehicle(
            "##",
            "car",
            "111244",
            "blue",
            math.floor(time.time())
        )
        self.assertFalse(self.insertVehicle_["Success"])

    def testRemoveVehicle(self):
        self.removeVehicle = removeVehicle(
            login("#007", "0000")["api_token"],
            "111244"
        )
        self.assertTrue(self.removeVehicle["Success"])

        self.insertVehicle = insertVehicle(
            login("#008", "0001")["api_token"],
            "car",
            "111244",
            "blue",
            math.floor(time.time())
        )
        self.assertTrue(self.insertVehicle["Success"])

        self.removeVehicle_ = removeVehicle(
            "##",
            "111244"
        )
        self.assertFalse(self.removeVehicle_["Success"])

        self.removeVehicle_ = removeVehicle(
            login("#007", "0000")["api_token"],
            "111247"
        )
        self.assertFalse(self.removeVehicle_["Success"])

    def insertIncidentReport(self):
        self.incident = insertIncident(
            login("#007", "0000"),
            "111244",
            math.floor(time.time())
        )
        self.assertTrue(self.incident["Success"])

        self.incident_ = insertIncident(
            login("#007", "0000"),
            "1112442",
            math.floor(time.time())
        )
        self.assertFalse(self.incident_["Success"])

        self.incident_ = insertIncident(
            "##",
            "111244",
            math.floor(time.time())
        )
        self.assertFalse(self.incident_["Success"])

    def testRemoveIncident(self):
        self.removeIncident_  = removeIncident(
            "##",
            "111244"
        )
        self.assertFalse(self.removeIncident_["Success"])

        self.removeIncident_  = removeIncident(
            login("#008", "0001")["api_token"],
            "11124466"
        )
        self.assertFalse(self.removeIncident_["Success"])

        self.removeIncident  = removeIncident(
            login("#008", "0001")["api_token"],
            "111244"
        )
        self.assertTrue(self.removeIncident["Success"])

    def testAlert(self):
        self.camera = insertCamera(
            login("#007", "0000")["api_token"], 
            "CANON350", 
            19.8667, 
            -7.8962, 
            "Sha wan drive"
        )
        self.assertTrue(self.camera["Success"])
        

        self.assertTrue(
            insertVehicle(
                login("#007", "0000")["api_token"],
                "van",
                "8765",
                "green",
                math.floor(time.time())
            )["Success"])

        insertIncident(
            login("#007", "0000")["api_token"],
            "8765",
            math.floor(time.time())+10
        )

        self.cam_ = createAlert(
            "##",
            "8765"
        )
        self.assertFalse(self.cam_["Success"])

        self.cam_ = createAlert(
            self.camera["api_token"],
            "8764oo"
        )
        self.assertTrue(self.cam_["Success"])
        self.assertEqual(self.cam_["Comments"], "No ID Matched")

        self.cam = createAlert(
            self.camera["api_token"],
            "8765"
        )
        self.assertTrue(self.cam["Success"])
        self.assertEqual(self.cam["Comments"], "ID Matched")
        



if __name__ == '__main__':
    unittest.main()

    # cam = insertCamera(
    #         login("#007", "0000")["api_token"], 
    #         "CANON350", 
    #         19.8667, 
    #         -7.8962, 
    #         "Sha wan drive"
    #     )
        
    # print(cam["api_token"])
    # # print(createAlert(
    # #         cam["api_token"],
    # #         "8765"
    # #     ))

    