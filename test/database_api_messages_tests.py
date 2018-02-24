"""
Created on 24.02.2018

Database API testing unit for messages related methods from medical_forum/database.py.

@author: Issam
"""

# Importing required modules
import sqlite3, unittest

# Import the database of medical_forum
from medical_forum import database

# Database file path to be used for testing only and create database instance
DB_PATH = 'db/medical_forum_test.db'
ENGINE = database.Engine(DB_PATH)


