import random
import requests
import json
import sqlite3

url_ = "http://10.66.89.32:5000"
id = [{
    "email": "u30@gmail.com",
    "password":"boogaloo",
    "name":"Gaeul",
    "phonenumber":"90897867"
},{
    "email": "u31@gmail.com",
    "password":"boogaloo",
    "name":"Jotaro",
    "phonenumber":"90897867"
},{
    "email": "u32@gmail.com",
    "password":"boogaloo",
    "name":"Esidisi",
    "phonenumber":"90897867"
},{
    "email": "u33@gmail.com",
    "password":"boogaloo",
    "name":"Joseph",
    "phonenumber":"90897867"
},{
    "email": "u34@gmail.com",
    "password":"boogaloo",
    "name":"Uzair",
    "phonenumber":"90897867"
},{
    "email": "u35@gmail.com",
    "password":"boogaloo",
    "name":"Kaiser",
    "phonenumber":"90897867"
},{
    "email": "u36@gmail.com",
    "password":"boogaloo",
    "name":"Caesar",
    "phonenumber":"90897867"
},{
    "email": "u37@gmail.com",
    "password":"boogaloo",
    "name":"Jupiter",
    "phonenumber":"90897867"
},{
    "email": "u38@gmail.com",
    "password":"boogaloo",
    "name":"Jonathan",
    "phonenumber":"90897867"
},{
    "email": "u39@gmail.com",
    "password":"boogaloo",
    "name":"Wahmu",
    "phonenumber":"90897867"
}]

# Create new Accounts
for i in id:
    tok = requests.get(
        url=f"{url_}/signup",
        params={
            "email":i["email"],
            "password":i["password"],
            "name":i["name"],
            "phonenumber":i["phonenumber"]
        })
    if not json.loads(tok.text)["Success"]:
        print(f"Failure:\t{json.loads(tok.text)['Comments']}")

# Login all accounts
for i in id:
    tok = requests.get(
        url=f"{url_}/login",
        params={
            "email":i["email"],
            "password":i["password"]
        })
    if not json.loads(tok.text)["Success"]:
        print(f"Failure:\t{json.loads(tok.text)['Comments']}")

    i["token"] = json.loads(tok.text)["token"]

# get verification code for all accounts
for i in id:
    tok = requests.get(
        url=f"{url_}/getcode",
        params={
            "token":i["token"]
        })
    if not json.loads(tok.text)["Success"]:
        print(f"Failure:\t{json.loads(tok.text)['Comments']}")
    i["code"] = json.loads(tok.text)["code"]

# verify each other
for i in id:
    for j in id:
        tok = requests.get(
            url=f"{url_}/verify",
            params={
                "token": i["token"],
                "code": j["code"]
            })
        if not json.loads(tok.text)["Success"]:
            print(f"Failure:\t{json.loads(tok.text)['Comments']}")



# # test scores
# con = sqlite3.connect("./server_data.db")
# cursor = con.execute("SELECT SCORE FROM USERDETAILS")
# print([row for row in cursor], end="\n\n\n")
# con.close()



random.seed(245)

comments = [
    "Food was good, but could be better",
    "Service was great",
    "Nice view",
    "Very convinient service",
    "Must try their new product",
    "The new branch location is close to my university",
    "Food is too salty",
    "I like their new menu"
]

for i in id:
    for restID in range(1,11,1):
        tok = requests.get(
            url=f"{url_}/placeReview",
            params={
                "token":i["token"],
                "restaurant_id": restID,
                "rating": random.randint(1,5),
                "food_rating": random.randint(1,5),
                "clean_rating": random.randint(1,5),
                "atmos_rating": random.randint(1,5),
                "service_rating": random.randint(1,5),
                "comment": comments[random.randint(0,len(comments)-1)]
            })


# print(id)

















# tok = requests.get(
#     url="http://10.66.85.186:5000/login",
#     params={
#         "email":"u35@gmail.com",
#         "password":"boogaloo"
#     })

# token = json.loads(tok.text)["token"]

# re = requests.get(
#     url="http://10.66.85.186:5000/ownReviews",
#     params={
#         "token":token,
#         "restaurant_id":4
#     }
# )

# print(re.text)

# re = requests.get(
#     url="http://10.66.85.186:5000/getRestaurantDetails",
#     params={
#         "token":token,
#         "restaurant_id":1
#     }
# )

# print(re.text)


# # re = requests.get(
# #     url="http://10.66.85.186:5000/updateReview",
# #     params={
# #         "token":token,
# #         "restaurant_id":1,
# #         "comment":"Chef was nice",
# #         "rating":5,
# #         "food_rating":3,
# #         "clean_rating":3,
# #         "atmos_rating":4,
# #         "service_rating":5
# #     }
# # )

# re = requests.get(
#     url="http://10.66.85.186:5000/recentReviews",
#     params={
#         "token":token,
#         "restaurant_id":1
#     }
# )

# print(re.text)

# # re = requests.get(
# #     url="http://10.66.85.186:5000/recentReviews",
# #     params={
# #         "restaurant_id":4
# #     }
# # )

# # print(re.text)