
import time
import flask
from flask import request
import datetime
import sqlite3
import numpy as np
import pandas as pd
from hashlib import sha256  # to hash passwords
import random
import math

app = flask.Flask(__name__)


# sha256 hasing
def hash(x):
    return sha256(x.encode('utf-8')).hexdigest().lower()


def levenshteinDistance(s1, s2):
    # calculate levenshtein edit distance between two strings
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(
                    1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


def mergeSort(arr, fn=None):
    if len(arr) <= 1:
        return arr
    else:
        p = len(arr)//2
        larr = mergeSort(arr[:p], fn)
        rarr = mergeSort(arr[p:], fn)
        n_arr = []
        while ((len(larr) > 0) and (len(rarr) > 0)):
            if fn is None:
                if larr[0] < rarr[0]:
                    n_arr.append(larr.pop(0))
                else:
                    n_arr.append(rarr.pop(0))
            else:
                if fn(larr[0]) < fn(rarr[0]):
                    n_arr.append(larr.pop(0))
                else:
                    n_arr.append(rarr.pop(0))
        if len(larr) > 0:
            n_arr.extend(larr)
        if len(rarr) > 0:
            n_arr.extend(rarr)
        return n_arr


# generate status for outputs
def generateStatus(success=True, comment="", excess=None):
    status = {
        "Success": success,
        "Comments": comment,
    }
    if excess:
        for i in excess:
            status[i] = excess[i]
    return status


def getRestaurantRating(restaurant_id):  # Get dataframe from sql query
    con = sqlite3.connect('server_data.db')
    df = pd.read_sql_query(
        f"SELECT RATING, TIME FROM REVIEWPOSTINGS WHERE RESTAURANT_ID = \"{restaurant_id}\"", con=con)
    con.close()
    return df


# Get restaurant rating with logarithmic decay
def getDynamicRating(restaurant_id, time_gap=2_419_200):
    # default time gap is 28 days
    df = getRestaurantRating(restaurant_id)

    if df.shape[0] == 0:
        return 0, {}

    # read dataframe from sql query
    now = df["TIME"].max()  # since latest review
    df["decay_val"] = df["TIME"].apply(lambda x: math.floor((now-x)/time_gap))
    # each degree of review is worth 90% of a new review
    df["rating_val"] = df.apply(
        lambda x: x.RATING*(0.90**x.decay_val), axis=1)

    stats = {}
    for i in df["RATING"]:
        if i in stats:
            stats[i] += 1
        else:
            stats[i] = 1

    # --> dynamic_rating, stats_on_rating
    return df["rating_val"].mean(), stats


@app.route('/login', methods=['GET'])
def login():
    # TODO: regex check for email and passwords
    # TODO: regex clean inputs

    email = request.args.get("email", "", type=str)
    password = request.args.get("password", "", type=str)
    # not recieving plain text; password is hashed
    password = hash(password)

    con = sqlite3.connect('server_data.db')
    cursor = con.execute(
        f"SELECT TOKEN from USERTOKEN where EMAIL =\"{email}\" and PASSWORD = \"{password}\"")
    res = [row for row in cursor]
    con.close()

    if len(res) == 0:
        return generateStatus(False, "Password or Email incorrect")
    # return {"status": "Success", "comment": "", "token": res[0][0]}
    return generateStatus(True, "", {"token": res[0][0]})


@app.route('/signup', methods=['GET'])
def signup():
    # TODO: regex check for email and passwords
    # TODO: regex check for name and phonenumber
    # TODO: regex clean inputs

    email = request.args.get("email", "", type=str)
    password = request.args.get("password", "", type=str)
    if email == "" or password == "":
        return generateStatus(False, "Password or Email incorrect")

    con = sqlite3.connect('server_data.db')
    cursor = con.execute(
        f"""SELECT * 
        FROM USERTOKEN 
        WHERE EMAIL = \"{email}\";"""
    )
    res = [row for row in cursor]
    con.close()
    if len(res) != 0:
        return generateStatus(False, "Email already in use")

    name = request.args.get("name", "", type=str)
    phonenumber = request.args.get("phonenumber", "", type=str)
    if name == "" or phonenumber == "":
        return generateStatus(False, "Name or Phone Number incorrect")

    con = sqlite3.connect('server_data.db')

    token = hash(email+password+str(random.random()))
    con.execute("INSERT INTO USERTOKEN (EMAIL, PASSWORD, TOKEN) values (?,?,?);",
                (email, hash(password), token))
    con.execute("INSERT INTO USERDETAILS (TOKEN, NAME, PHONENUMBER, PROFILE_PICTURE, SCORE, CODE) values (?,?,?,?,?,?);",
                (token, name, phonenumber, None, 0.1, hash(token)[:5]))  # we can update profile picture later

    con.commit()
    con.close()
    return generateStatus(True, "New Account Created")


@app.route('/getRestaurantDetails', methods=['GET'])
def getRestaurantDetails():
    restaurant_id = request.args.get("restaurant_id", -1, type=int)
    if restaurant_id == -1:
        return generateStatus(False, "Restaurant ID not recognized")

    dynamic_rating, stats = getDynamicRating(restaurant_id)

    con = sqlite3.connect("server_data.db")

    cursor = con.execute(
        f"SELECT NAME, PHONENUMBER, ADDRESS, IMAGE, LOGO FROM RESTAURANTDETAILS WHERE RESTAURANT_ID={restaurant_id};")

    res = [row for row in cursor]
    if len(res) == 0:
        con.close()
        return generateStatus(False, "Restaurant ID not recognized")

    name, phone, address, image, logo = None, None, None, None, None
    for row in res:
        name, phone, address, image, logo = row

    con.close()
    return generateStatus(True, "", {
        "name": name,
        "phonenumber": phone,
        "address": address,
        "image_url": image,
        "logo_url": logo,
        "dynamic_rating": dynamic_rating*1.0,
        "stats": stats
    })


@app.route('/ownReviews', methods=['GET'])
def ownReviews():
    # user view own reviews

    user_token = request.args.get("token", "", type=str)
    restaurant_id = request.args.get("restaurant_id", -1, type=int)

    if user_token == "":
        return generateStatus(False, "User Token Invalid")

    if restaurant_id == -1:
        return generateStatus(False, "Restaurant ID Invalid")

    con = sqlite3.connect("./server_data.db")

    cursor = con.execute(
        f"SELECT * FROM USERTOKEN WHERE TOKEN=\"{user_token}\";")
    if len([row for row in cursor]) == 0:
        con.close()
        return generateStatus(False, "User Token Invalid")

    cursor = con.execute(
        f"SELECT NAME FROM RESTAURANTDETAILS WHERE RESTAURANT_ID={restaurant_id}")
    if len([row for row in cursor]) == 0:
        con.close()
        return generateStatus(False, "Restaurant ID Invalid")

    cursor = con.execute(
        f"SELECT * FROM REVIEWPOSTINGS WHERE TOKEN=\"{user_token}\" AND RESTAURANT_ID={restaurant_id}")
    res = [row for row in cursor]
    if len(res) > 0:
        _, _, rating, comment, time = res[0]
        con.close()
        return generateStatus(True, "", {
            "rating": rating,
            "comment": comment,
            "time": str(datetime.datetime.fromtimestamp(time))
        })
    else:
        con.close()
        return generateStatus(True, "", {
            "rating": 0.0,
            "comment": "",
            "time": "0"
        })


@app.route('/findRestaurant', methods=['GET'])
def findRestaurant():
    # TODO: add review(s) to tuple --> can be sorted in app
    name = request.args.get("name", "", type=str)
    if name == "":
        return generateStatus(False, "Invalid Search Request")

    con = sqlite3.connect("./server_data.db")

    cursor = con.execute(
        "SELECT NAME, RESTAURANT_ID, LOGO FROM RESTAURANTDETAILS")

    res = [(res_name, res_id, levenshteinDistance(res_name, name), logo)
           for res_name, res_id, logo in cursor]
    res = mergeSort(res, lambda x: x[2])[:5]  # top 5 results
    if res[0][2] == 0:
        res = [res[0]]

    res_ = {"restaurant": [(res_name, str(res_id), logo)
                           for res_name, res_id, _, logo in res]}

    con.close()
    return generateStatus(True, "", res_)


def calcScore(token: str, rating: int) -> int:
    # assuming token is correct
    con = sqlite3.connect("./server_data.db")
    cursor = con.execute(
        f"SELECT SCORE FROM USERDETAILS WHERE TOKEN=\"{token}\";")
    res = [row for row in cursor]
    score = res[0][0]
    con.close()
    return (rating-2.5)*score+2.5


@app.route('/placeReview', methods=["GET"])
def placeReview():
    user_token = request.args.get("token", "", type=str)
    if user_token == "":
        return generateStatus(False, "Incorrect User Token")
    rest_id = request.args.get("restaurant_id", -1, type=int)
    if rest_id == -1:
        return generateStatus(False, "Incorrect Restaurant ID")

    con = sqlite3.connect("./server_data.db")

    cursor = con.execute(
        f"SELECT * FROM USERTOKEN WHERE TOKEN=\"{user_token}\";")
    if len([row for row in cursor]) == 0:
        return generateStatus(False, "Incorrect User Token")
    cursor = con.execute(
        f"SELECT * FROM RESTAURANTDETAILS WHERE RESTAURANT_ID={rest_id};")
    if len([row for row in cursor]) == 0:
        return generateStatus(False, "Incorrect Restaurant ID")

    rating = request.args.get("rating", -1, type=int)
    food = request.args.get("food_rating", -1, type=int)
    clean = request.args.get("clean_rating", -1, type=int)
    atmos = request.args.get("atmos_rating", -1, type=int)
    serv = request.args.get("service_rating", -1, type=int)
    if (rating == -1) or (food == -1) or (clean == -1) or (atmos == -1) or (serv == -1):
        return generateStatus(False, "Rating Value Incorrect")
    if (rating > 5 or rating < 1) or (food > 5 or food < 1) or (clean > 5 or clean < 1) or (atmos > 5 or atmos < 1) or (serv > 5 or serv < 1):
        return generateStatus(False, "Rating Value Incorrect")

    comment = request.args.get("comment", None, type=str)

    con.execute(
        "INSERT INTO REVIEWPOSTINGS (RESTAURANT_ID, TOKEN, RATING, COMMENT, TIME) VALUES (?, ?, ?, ?, ?);",
        (rest_id, user_token, calcScore(user_token, rating),
         comment, math.floor(time.time()))
    )
    con.execute(
        "INSERT INTO REVIEWBREAKDOWN (RESTAURANT_ID, TOKEN, FOOD_RATING, CLEANLINESS_RATING, ATMOSPHRERE_RATING, SERVICE_RATING) VALUES (?, ?, ?, ?, ?, ?);",
        (rest_id, user_token, food, clean, atmos, serv))
    con.commit()
    con.close()
    return generateStatus(True, "")


@app.route('/updateReview', methods=["GET"])
def updateReview():
    user_token = request.args.get("token", "", type=str)
    if user_token == "":
        return generateStatus(False, "Incorrect User Token")
    rest_id = request.args.get("restaurant_id", -1, type=int)
    if rest_id == -1:
        return generateStatus(False, "Incorrect Restaurant ID")

    con = sqlite3.connect("./server_data.db")

    cursor = con.execute(
        f"SELECT * FROM USERTOKEN WHERE TOKEN=\"{user_token}\";")
    if len([row for row in cursor]) == 0:
        con.close()
        return generateStatus(False, "Incorrect User Token")

    cursor = con.execute(
        f"SELECT * FROM RESTAURANTDETAILS WHERE RESTAURANT_ID={rest_id};")
    if len([row for row in cursor]) == 0:
        con.close()
        return generateStatus(False, "Incorrect Restaurant ID")

    cursor = con.execute(
        f"SELECT * FROM REVIEWPOSTINGS WHERE RESTAURANT_ID={rest_id} AND TOKEN=\"{user_token}\";")
    if len([row for row in cursor]) == 0:
        con.close()
        return generateStatus(False, "No Previous Review Found")

    rating = request.args.get("rating", -1, type=int)
    food = request.args.get("food_rating", -1, type=int)
    clean = request.args.get("clean_rating", -1, type=int)
    atmos = request.args.get("atmos_rating", -1, type=int)
    serv = request.args.get("service_rating", -1, type=int)
    if (rating == -1) or (food == -1) or (clean == -1) or (atmos == -1) or (serv == -1):
        con.close()
        return generateStatus(False, "Rating Value Incorrect")
    if (rating > 5 or rating < 1) or (food > 5 or food < 1) or (clean > 5 or clean < 1) or (atmos > 5 or atmos < 1) or (serv > 5 or serv < 1):
        con.close()
        return generateStatus(False, "Rating Value Incorrect")

    comment = request.args.get("comment", None, type=str)

    con.execute(
        f"DELETE FROM REVIEWPOSTINGS WHERE RESTAURANT_ID={rest_id} AND TOKEN=\"{user_token}\"")
    con.execute(
        f"DELETE FROM REVIEWBREAKDOWN WHERE RESTAURANT_ID={rest_id} AND TOKEN=\"{user_token}\"")

    con.execute(
        "INSERT INTO REVIEWPOSTINGS (RESTAURANT_ID, TOKEN, RATING, COMMENT, TIME) VALUES (?, ?, ?, ?, ?);",
        (rest_id, user_token, calcScore(user_token, rating),
         comment, math.floor(time.time()))
    )
    con.execute(
        "INSERT INTO REVIEWBREAKDOWN (RESTAURANT_ID, TOKEN, FOOD_RATING, CLEANLINESS_RATING, ATMOSPHRERE_RATING, SERVICE_RATING) VALUES (?, ?, ?, ?, ?, ?);",
        (rest_id, user_token, food, clean, atmos, serv))
    con.commit()
    con.close()
    return generateStatus(True, "")


@app.route('/recentReviews', methods=['GET'])
def recentReviews():
    user_token = request.args.get("token", "", type=str)
    if user_token == "":
        return generateStatus(False, "Incorrect User Token")

    rest_id = request.args.get("restaurant_id", -1, type=int)
    if rest_id == -1:
        return generateStatus(False, "Incorrect Restaurant ID")

    con = sqlite3.connect("./server_data.db")
    cursor = con.execute(
        f"SELECT * FROM RESTAURANTDETAILS WHERE RESTAURANT_ID={rest_id};")
    if len([row for row in cursor]) == 0:
        con.close()
        return generateStatus(False, "Incorrect Restaurant ID")

    cursor = con.execute(
        f"SELECT * FROM USERTOKEN WHERE TOKEN=\"{user_token}\";")
    if len([row for row in cursor]) == 0:
        con.close()
        return generateStatus(False, "Incorrect User Token")

    cursor = con.execute(
        f"SELECT TOKEN, RATING, COMMENT, TIME FROM REVIEWPOSTINGS WHERE RESTAURANT_ID={rest_id} AND TOKEN != \"{user_token}\"")

    # [:-5] # 5 most recent reviews
    reviews = mergeSort([row for row in cursor], lambda x: int(x[3]))

    details = []
    for token, rating, comment, time_ in reviews:
        cursor = con.execute(
            f"SELECT NAME FROM USERDETAILS WHERE TOKEN=\"{token}\";")
        res_ = [row for row in cursor]
        name = res_[0][0]
        details.append([name, rating, comment, str(
            datetime.datetime.fromtimestamp(time_))])

    return generateStatus(True, "", {"details": details})

#TODO: test


def getPrefScore(res_id, arr):
    res = None
    with sqlite3.connect("./server_data.db") as con:
        cursor = con.execute(
            f"SELECT FOOD_RATING, CLEANLINESS_RATING, ATMOSPHRERE_RATING, SERVICE_RATING FROM REVIEWBREAKDOWN WHERE RESTAURANT_ID={res_id};")
        res = np.sum(np.multiply(
            np.array([row for row in cursor], dtype=np.int16).reshape(-1, 4),
            np.array(arr).reshape(4, -1)
        ))
        con.close()
    return res


@app.route('/prefReviews', methods=['GET'])
def prefReviews():

    def median_r(x): return x if (x >= 0 and x <= 10) else 5
    food_r = request.args.get("restaurant_id", 5, type=int)
    food_r = median_r(food_r)
    clean_r = request.args.get("restaurant_id", 5, type=int)
    clean_r = median_r(clean_r)
    atmos_r = request.args.get("restaurant_id", 5, type=int)
    atmos_r = median_r(atmos_r)
    serv_r = request.args.get("restaurant_id", 5, type=int)
    serv_r = median_r(serv_r)
    # on a range of [0..10] each rating default is 5
    preferences = np.array([food_r, clean_r, atmos_r, serv_r])

    with sqlite3.connect("./server_data.db") as con:
        cursor = con.execute(f"SELECT RESTAURANT_ID FROM REVIEWBREAKDOWN")
        res = []
        for row in cursor:
            res_id = row[0]
            score = getPrefScore(res_id, preferences)
            res.append([res_id, score])
        con.close()

    res = mergeSort(res_id, lambda x: x[1])[::-1]
    return generateStatus(True, "", res)


@app.route('/verify', methods=['GET'])
def verify():
    verifierToken = request.args.get("token", "", type=str)
    if verifierToken == "":
        return generateStatus(False, "Incorrect User Token")

    con = sqlite3.connect("./server_data.db")

    cursor = con.execute(
        f"SELECT * FROM USERTOKEN WHERE TOKEN=\"{verifierToken}\";")
    if len([row for row in cursor]) == 0:
        con.close()
        return generateStatus(False, "Incorrect User Token")

    code = request.args.get("code", "", type=str)
    if code == "":
        con.close()
        return generateStatus(False, "Incorrect Friend Code")

    cursor = con.execute(
        f"SELECT * FROM USERDETAILS WHERE CODE=\"{code.lower()}\";")
    if len([row for row in cursor]) == 0:
        con.close()
        return generateStatus(False, "Incorrect Friend Code")

    cursor = con.execute(
        f"SELECT TOKEN FROM USERDETAILS WHERE CODE=\"{code.lower()}\";")
    friendToken = [row for row in cursor][0][0]

    # test that not previously verified
    cursor = con.execute(
        f"SELECT * FROM VERIFY WHERE TOKEN=\"{friendToken}\" AND VERIFIER=\"{verifierToken}\";")
    if len([row for row in cursor]) > 0:
        con.close()
        return generateStatus(False, "Already Verified")

    # confirm verification
    con.execute("INSERT INTO VERIFY (VERIFIER, TOKEN) VALUES (?,?);",
                (verifierToken, friendToken))
    # get existing profile score
    cursor = con.execute(
        f"SELECT SCORE FROM USERDETAILS WHERE TOKEN=\"{friendToken}\";")
    score = [row for row in cursor][0][0]
    score = (score + 0.1 if (score + 0.1) <= 1 else 1)
    # update profile score
    con.execute(
        F"UPDATE USERDETAILS SET SCORE={score} WHERE TOKEN=\"{friendToken}\";")
    con.commit()
    con.close()
    return generateStatus(True, "Score Updated")


@app.route('/getcode', methods=['GET'])
def getcode():
    verifierToken = request.args.get("token", "", type=str)
    if verifierToken == "":
        return generateStatus(False, "Incorrect User Token")

    con = sqlite3.connect("./server_data.db")

    cursor = con.execute(
        f"SELECT * FROM USERTOKEN WHERE TOKEN=\"{verifierToken}\";")
    if len([row for row in cursor]) == 0:
        con.close()
        return generateStatus(False, "Incorrect User Token")

    cursor = con.execute(
        f"SELECT CODE FROM USERDETAILS WHERE TOKEN=\"{verifierToken}\";")
    res = [row for row in cursor]
    code = res[0][0]

    con.close()
    return generateStatus(True, "", {"code": code})


app.run(host='0.0.0.0')
