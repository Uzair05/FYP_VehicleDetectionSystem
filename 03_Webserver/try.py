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

print(login("#007", "0000")["api_token"])
print(login("#007", "0000")["api_token"]+"a")

print(testOfficerAPI(login("#007", "0000")["api_token"]))
print(testOfficerAPI(login("#007", "0000")["api_token"]+"a"))