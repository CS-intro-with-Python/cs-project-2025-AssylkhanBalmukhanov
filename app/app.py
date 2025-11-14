from flask import Flask, jsonify, render_template, request
import pandas as pd
import random
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "Server is running! API and Docker are verified."


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)