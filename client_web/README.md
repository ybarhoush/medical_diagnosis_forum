# Medical diagnosis forum web client

The is a simple web client to manage the Medical diagnosis forum API. It manages
the users (patients and doctors), messages and diagnosis. It is a simple
admin-like panel that has a slightly different view depending on the user type
(patient or doctor).

## Dependiencies

The client uses JavaScript, JQuery and AJAX, along with static HTML and CSS to serve the
users. The HTML pages and JavaScript files are located in static folder.

We use JQuery  library to handle changes in the HTML served, Bootstrap library
to show some nicely prepared views. The libraries are being used directly from
their appropriate CDNs and not stored locally.

## Setup client

The python script *client.py* setup the client by providing the path to the
static files folder, also debug can be enabled from there. Though the client
won't be run alone, but rather the server will initiate it and call it when the
server is being started from the *main.py* in root folder.

## Run client

The client is to be run from a web browser, after having the server started
correctly, go to the link

``` python
http://localhost:5000/medical_forum/client/index.html
```

There will get the main view with (for now) a list of current users, seperated
as patients and doctors. For now, we don't have an isolated login page, but we
show the list of all users. You can also register a new user.

The patients view, will get a view of personal (public and private) profile
information, along with messages that they can delete or add, and a list of
diagnoses assigned to them.

The doctors, will get almost the same, but instead of having a limited list of
diagnoses for example, they get the full list of diagnoses for all patients.