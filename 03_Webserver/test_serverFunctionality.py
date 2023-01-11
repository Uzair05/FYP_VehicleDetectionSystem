import requests
import json
import unittest

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

class Testing(unittest.TestCase):
    def testLogin(self):
        self.assertTrue(login("#007", "0000")["Success"], "Login should Succeed")
        self.assertFalse(login("#007", "9000")["Success"], "Login should Fail")
        self.assertFalse(login("#001", "0000")["Success"], "Login should Fail")

    def testCameraInsert(self):
        self.res = insertCamera(login("#007", "0000")["api_token"], "CANON350", 19.8767, -7.8967, "Sha wan drive")

        self.assertTrue(self.res["Success"], "Camera insert should succeed")
        self.assertNotEqual(self.res["api_token"], None, "Token api should exist")

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




if __name__ == '__main__':
    unittest.main()