from crypt import methods
from sre_parse import FLAGS
from flask import Flask, request
import sqlite3

app = Flask(__name__)


@app.route('/props', methods=['GET'])
def props():
    pass
