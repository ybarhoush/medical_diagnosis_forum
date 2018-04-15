# Medical diagnosis forum
This is a medical diagnosis forum RESTFUL API. It can be used by patients to ask doctors for help and diagnose the medical situation.

At this step, we have designed the database and implemented the basic calls to the database.
These are methods to create, get, modify and delete users (patients or doctors). As well as messages, profiles and diagnosis status.

# Framework
Python 3.6 is used for this whole project.

# Folders Structure

The code is divided into sub folders as follows. The *db* folder contains all the database dumps, schemas and a backup version of that.
The *medical_forum* folder holds the main module to handle database operations (get, create entries...etc.).
The *test* folder contains the needed *unittests* to test the functionality of different database operation.

# Database setup
We use SQLite 3 and the *database.py* handles the connection.
At this point the database was used only in unittests to test that all logic works well. But to create a database instance and use it with this project you do:
```python
import sqlite3
from medical_forum import database

# Database instance used with unittest for example
DB_PATH = 'db/medical_forum_data_test.db'
ENGINE = database.Engine(DB_PATH)

```

The *ENGINE* instance can be used to clear and connect to the database.

```python

# populate the tables from the .sql file in db folder
ENGINE.populate_tables()
# Connect to db
self.connection = ENGINE.connect()


# To clear all data in db tables
ENGINE.clear()

```

To execute queries
```python
# get connection instance
con = self.connection.con

with con:
    # Cursor and row initialization
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    ## code for executing query
```

# Run tests
To run the unittests use the command for example to test tables schemas, and do the other tests as well by changing the name accordingly.
```bash
python -m test.database_api_tables_tests
```

In the unittests, some methods are being used a lot, like executing queries, so a *utils.py* file is used to make the code better.
The *utils.py* is in *test* folder.

To run the server functional tests; there is one file for testing each resource and its collection
```bash
python -m test_api_diagnosis_and_diagnoses.py
python -m test_api_message_and_messages.py
python -m test_api_user_and_users.py

```