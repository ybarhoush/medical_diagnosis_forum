# Medical diagnosis forum

This is a medical diagnosis forum RESTFUL API. It can be used by patients to ask doctors for help and diagnose the medical situation.

At this step, we have designed the database and implemented the basic calls to the database.
These are methods to create, get, modify and delete users (patients or doctors). As well as messages, profiles and diagnosis status.
 The documentation of the API can be found on this apiary.io link: https://medicalforumapp.docs.apiary.io/#

## Framework

Python 3.6 is used for this whole project. We use Flask framework for all the API impelementation. We use the vnd.mason+json as a hypermedia type for the different requests and responses. The server by default will run on localhost on port 5000. In the server can be started with the *main.py* file in the root folder. It only starts the server of this medical forum using the line of code:

```python
APP.run(debug=True)
```

## Folders Structure

The code is divided into sub folders as follows. The *db* folder contains all the database dumps, schemas and a backup version of that.
The *medical_forum* folder holds the main module to handle database operations (get, create entries...etc.) and API implementation for different resources and their connections return codes and error handling events. The resources are divided as each concept in a seperate python file for organization. So, Users and User resources are in the file *user_resource.py* and so on. The file *api.py* create and initiate the API instance using Flask module, and *resources.py* adds the routes to the different resources and different redirections.
The *test* folder contains the needed *unittests* to test the functionality of different database operation.

## Database setup

We use SQLite 3 and the *database_engine.py* and *database_connection.py* handles the connection.
At this point the database was used only in unittests to test that all logic works well. But to create a database instance and use it with this project you do:

```python
import sqlite3
from medical_forum import database_engine

# Database instance used with unittest for example
DB_PATH = 'db/medical_forum_data_test.db'
ENGINE = database_engine.Engine(DB_PATH)
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
    cursor = con.cursor()

    ## code for executing query
```

## Forum Structure

The medical forum has the followings resources: users & user, messages & message, diagnoses & diagnosis and public & restricted user profiles. Also, keep in mind that the users have a type, either a doctor or a patient.

## API links

*/medical-forum/api/resouce_name*, for example /medical-forum/api/messages: which will list all the users registered in the database.

## Run tests

To run the unittests use the command for example to test tables schemas, and do
the other tests as well by changing the name accordingly.

```bash
python -m unittest tests.test_name
```

In the unittests, some methods are being used a lot, like executing queries, so a *utils.py* file is used to make the code better.
The *utils.py* is in *test* folder.

To run the server functional tests; there is one file for testing each resource
and its collection

```bash
python -m unittest tests.test_api_diagnosis_and_diagnoses
python -m unittest tests.test_api_message_and_messages
python -m unittest tests.test_api_user_and_users

```
