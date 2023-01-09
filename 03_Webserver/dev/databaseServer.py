from flask import Flask, request
import typing
import sqlite3

app = Flask(__name__)


@app.route('/props', methods=['GET'])
def props():
    pass
