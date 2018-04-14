"""
Create API and APP objects
"""
from flask import Flask, g
from flask_restful import Api
from medical_forum import database_engine
from medical_forum.utils import RegexConverter

APP = Flask(__name__, static_folder="static", static_url_path="/.")
APP.debug = True
APP.config.update({"Engine": database_engine.Engine()})
API = Api(APP)


def add_regex_support_to_routes():
    """
    Add the Regex Converter so we can use regex expressions when we define the routes
    """
    APP.url_map.converters["regex"] = RegexConverter


add_regex_support_to_routes()


@APP.before_request
def connect_db():
    """
    Creates a database connection before the request is proccessed.

    The connection is stored in the application context variable flask.g .
    Hence it is accessible from the request object.
    """

    g.con = APP.config["Engine"].connect()


@APP.teardown_request
def close_connection(exception):
    """
    Closes the database connection
    Check if the connection is created. It migth be exception appear before
    the connection is created.
    """
    if exception is not None:
        print("Got execption on close connection: " + str(exception))
    if hasattr(g, "con"):
        g.con.close()
