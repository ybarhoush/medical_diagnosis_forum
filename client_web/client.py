"""
Web client initialization for the medical forum
"""

from flask import Flask

APP = Flask(__name__, static_folder='static', static_url_path='')
APP.debug = True
