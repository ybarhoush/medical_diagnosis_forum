/**
 * @fileOverview Forum administration dashboard. It utilizes the Forum API to
                 handle user information (retrieve user list, edit user profile,
                 as well as add and remove new users form the system). It also
                 permits to list and remove user's messages.
 * @author <a href="mailto:ivan.sanchez@oulu.fi">Ivan Sanchez Milara</a>
 * @author <a href="mailto:mika.oja@oulu.fi">Mika Oja</a>
 * @author <a href="mailto:assam.boudjelthia@oulu.fi">Assam Boudjelthia</a>"
 * @version 1.1
 *
**/


var DEBUG_ENABLE = true;
const MASONJSON = 'application/vnd.mason+json';
const PLAINJSON = 'application/json';
const FORUM_USER_PROFILE = '/profiles/users';
const FORUM_MESSAGE_PROFILE = '/profiles/messages';
const FORUM_MESSAGE_DIAGNOSIS = '/profiles/diagnoses';
const DEFAULT_DATATYPE = 'json';
const ENTRYPOINT_USERS = '/medical_forum/api/users/';
const ENTRYPOINT_MESSAGES = '/medical_forum/api/messages/';
const ENTRYPOINT_DIAGNOSES = '/medical_forum/api/diagnoses/';

const USER_ICON = 'glyphicon glyphicon-user';
const DOCTOR_ICON = 'glyphicon glyphicon-grain';
const DELETE_ICON = 'glyphicon glyphicon-trash';
const EDIT_ICON = 'glyphicon glyphicon-pencil';
const ADD_DIAG_ICON = 'glyphicon glyphicon-tags';

/**** START RESTFUL CLIENT****/

/**** Description of the functions that call Forum API by means of jQuery.ajax()
      calls. We have implemented one function per link relation in both
profiles. Since we are not interesting in the whole API functionality, some of
the functions does not do anything. Hence, those link relations are ignored
****/


/**
 * Sends an AJAX GET request to retrive the list of all the diagnoses of the
 *application
 *
 * ONSUCCESS=> Show diagnoses in the #diagnoses_list section.
 *             After processing the response it utilizes the method {@link
 #appendDiagnosisToList} to append the user to the list.Each user is an anchor
 *pointing to the respective user url. ONERROR => Show an alert to the user.
 *
 * @param {string} [apiurl = ENTRYPOINT] - The url of the Diagnoses instance.
 **/
function getDiagnoses(apiurl) {
    apiurl = apiurl || ENTRYPOINT_DIAGNOSES;
    return $.ajax({
            url: apiurl,
            dataType: DEFAULT_DATATYPE
        })
        .always(function () {
            $('#diagnoses_list').empty();
        })
        .done(function (data, textStatus, jqXHR) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED RESPONSE: data:', data, '; textStatus:', textStatus);
            }

            diagnoses = data.items;
            for (var i = 0; i < diagnoses.length; i++) {
                var diagnosis = diagnoses[i];
                appendUserToList(diagnosis['@controls'].self.href, diagnosis)
            }

            var create_ctrl = data['@controls']['medical_forum:add-user']

            if (create_ctrl.schema) {
                createFormFromSchema(
                    create_ctrl.href, create_ctrl.schema, 'new_user_form');
            } else if (create_ctrl.schemaUrl) {
                $.ajax({
                        url: create_ctrl.schemaUrl,
                        dataType: DEFAULT_DATATYPE
                    })
                    .done(function (data, textStatus, jqXHR) {
                        createFormFromSchema(create_ctrl.href, data, 'new_user_form');
                    })
                    .fail(function (jqXHR, textStatus, errorThrown) {
                        if (DEBUG_ENABLE) {
                            console.log(
                                'RECEIVED ERROR: textStatus:', textStatus,
                                ';error:', errorThrown);
                        }
                        alert('Could not fetch form schema.  Please, try again');
                    });
            }
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED ERROR: textStatus:', textStatus,
                    ';error:', errorThrown);
            }
            alert('Could not fetch the list of users.  Please, try again');
        });
}

/**
 * This function is the entrypoint to the Forum API.
 *
 * Associated rel attribute: Users Mason+JSON and users-all
 *
 * Sends an AJAX GET request to retrive the list of all the users of the
 *application
 *
 * ONSUCCESS=> Show users in the #patients_list and #doctors_list.
 *             After processing the response it utilizes the method {@link
 *#appendUserToList} to append the user to the list. Each user is an anchor
 *pointing to the respective user url. ONERROR => Show an alert to the user.
 *
 * @param {string} [apiurl = ENTRYPOINT] - The url of the Users instance.
 **/
function getUsers(apiurl) {
    apiurl = apiurl || ENTRYPOINT_USERS;
    $('#mainContent').hide();
    return $.ajax({
            url: apiurl,
            dataType: DEFAULT_DATATYPE
        })
        .always(function () {
            // Remove old list of users
            // clear the form data hide the content information(no selected)
            $('#patients_list').empty();
            $('#doctors_list').empty();
            $('#mainContent').hide();
        })
        .done(function (data, textStatus, jqXHR) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED RESPONSE: data:', data, '; textStatus:', textStatus);
            }

            users = data.items;
            for (var i = 0; i < users.length; i++) {
                var user = users[i];
                appendUserToList(user['@controls'].self.href, user)
            }

            var create_ctrl = data['@controls']['medical_forum:add-user']

            if (create_ctrl.schema) {
                createFormFromSchema(
                    create_ctrl.href, create_ctrl.schema, 'new_user_form');
            } else if (create_ctrl.schemaUrl) {
                $.ajax({
                        url: create_ctrl.schemaUrl,
                        dataType: DEFAULT_DATATYPE
                    })
                    .done(function (data, textStatus, jqXHR) {
                        createFormFromSchema(create_ctrl.href, data, 'new_user_form');
                    })
                    .fail(function (jqXHR, textStatus, errorThrown) {
                        if (DEBUG_ENABLE) {
                            console.log(
                                'RECEIVED ERROR: textStatus:', textStatus,
                                ';error:', errorThrown);
                        }
                        alert('Could not fetch form schema.  Please, try again');
                    });
            }
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED ERROR: textStatus:', textStatus,
                    ';error:', errorThrown);
            }
            alert('Could not fetch the list of users.  Please, try again');
        });
}

/*** RELATIONS USED IN MESSAGES AND USERS PROFILES ***/

/**
 * This client does not support this functionality.
 *
 * Associated rel attribute: messages-all
 *
 * @param {string} apiurl - The url of the Messages list.
 * // TODO: THE CLIENT DOES NOT KNOW HOW TO HANDLE LIST OF MESSAGES
 **/
function messages_all(apiurl) {
    return;
}

/*** FUNCTIONS FOR MESSAGE PROFILE ***/

/*** Note, the client is mainly utilized to manage users, not to manage
messages ***/


/**
 * This client does not support this functionality.
 *
 * Associated rel attribute: reply
 *
 * @param {string} apiurl - The url of the parent message.
 * @param {object} body - An associative array with the new message
 *
 **/
function reply(apiurl, body) {
    return; // THE CLIENT DOES NOT KNOW HOW TO ADD A NEW MESSAGE
}

/**
 * Sends an AJAX request to remove a message from the system. Utilizes the
 *DELETE method.
 *
 * Associated rel attribute: delete (in Message profile)
 * ONSUCCESS=>
 *          a) Inform the user with an alert.
 *          b) Go to the initial state by calling the function {@link
 *#reloadUserData} *
 *
 * ONERROR => Show an alert to the user
 *
 * @param {string} apiurl - The url of the Message
 *
 **/

function delete_message(apiurl) {
    if (DEBUG_ENABLE) {
        console.log('Triggered delete_message');
    }

    return $
        .ajax({
            url: apiurl,
            type: 'DELETE',

        })
        .done(function (data, textStatus, jqXHR) {
            alert('Message deleted successfully');
            reloadUserData();
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            var error = jqXHR.responseJSON['@error'];
            alert(
                'ERROR DELETING MESSAGE: ' + error['@messages'][0],
                error['@message']);
        });
}

function edit_message(apiurl, body) {
    if (DEBUG_ENABLE) {
        console.log('Triggered edit_message');
    }

    return $
        .ajax({
            url: apiurl,
            type: 'PUT',
            data: JSON.stringify(body),
            processData: false,
            contentType: PLAINJSON
        })
        .done(function (data, textStatus, jqXHR) {
            alert('Message edited successfully');
            reloadUserData();
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            var error = jqXHR.responseJSON['@error'];
            alert(
                'ERROR EDITING MESSAGE: ' + error['@messages'][0],
                error['@message']);
        });
}

/**
 * This client does not support this functionality.
 *
 * Associated rel attribute: author
 *
 * @param {string} apiurl - The url of the User instance.
 **/
function author(apiurl) {
    return; // THE CLIEND DOES NOT KNOW TO HANDLE THIS RELATION.
}

/**
 * This client does not support this functionality.
 *
 * Associated rel attribute: collection (message_profile)
 *
 * @param {string} apiurl - The url of the Messages list.
 **/
function collection_messages(apiurl) {
    return; // THE CLIENT DOES NOT KNOW HOW TO HANDLE A LIST OF MESSAGES
}

/**
 * This client does not support this functionality.
 *
 * Associated rel attribute: in-reply-to
 *
 * @param {string} apiurl - The url of the Message
 **/
function in_reply_to(apiurl) {
    return; // THE CLIENT DOES NOT KNOW HOW TO REPRESENT A HIERARHCY OF MESSAGEs
}

/**
 * Sends an AJAX request to retrieve message information Utilizes the GET
 *method.
 *
 * Associated rel attribute: self (in message profile)
 *
 * ONSUCCESS=>
 *          a) Extract message information from the response body. The response
 *             utilizes a HAL format.
 *          b) Show the message headline and articleBody in the UI. Call the
 *helper method {@link appendMessageToList}
 *
 * ONERROR => Show an alert to the user
 *
 * @param {string} apiurl - The url of the Message
 *
 **/

function get_message(apiurl) {
    $.ajax({
            url: apiurl,
            dataType: DEFAULT_DATATYPE
        })
        .done(function (data, textStatus, jqXHR) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED RESPONSE: data:', data, '; textStatus:', textStatus);
            }
            appendMessageToList(data);
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED ERROR: textStatus:', textStatus,
                    ';error:', errorThrown);
            }
            alert('Cannot get information from message: ' + apiurl);
        });
}


function get_diagnosis(apiurl) {
    $.ajax({
            url: apiurl,
            dataType: DEFAULT_DATATYPE
        })
        .done(function (data, textStatus, jqXHR) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED RESPONSE: data:', data, '; textStatus:', textStatus);
            }
            appendDiagnosisToList(data);
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED ERROR: textStatus:', textStatus,
                    ';error:', errorThrown);
            }
            alert('Cannot get information from message: ' + apiurl);
        });
}

/*** FUNCTIONS FOR USER PROFILE ***/

/**
 * Sends an AJAX GET request to retrieve information related to user history.
 *
 * Associated rel attribute: messages-history
 *
 * ONSUCCESS =>
 *   a.1) Check the number of messages received (data.items)
 *   a.2) Add the previous value to the #messagesNumber input element (located
 *in #userHeader section). b.1) Iterate through all messages. b.2) For each
 *message in the history, access the message information by calling the
 *corresponding Message instance (call {@link get_message}) The url of the
 *message is obtained from the href attribute of the message item. ONERROR =>
 *    a)Show an *alert* informing the user that the target user history could
 *not be retrieved b)Deselect current user calling {@link #deselectUser}.
 * @param {string} apiurl - The url of the History instance.
 **/
function messages_history(apiurl) {
    if (DEBUG_ENABLE) {
        console.log('Retrieving the user history information');
    }

    apiurl = apiurl || ENTRYPOINT_USERS;
    return $.ajax({
            url: apiurl,
            dataType: DEFAULT_DATATYPE
        })
        .done(function (data, textStatus, jqXHR) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED RESPONSE: data:', data, '; textStatus:', textStatus);
            }
            var messages = data.items;
            $('#messagesNumber')[0].innerHTML = messages.length.toString();
            for (var i = 0; i < messages.length; i++) {
                var message = messages[i];
                console.log(message);
                // Extract message url, headline and articleBody
                get_message(message['@controls'].self.href);
            }
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED ERROR: textStatus:', textStatus,
                    ';error:', errorThrown);
            }
            // Inform user about the error using an alert message.
            $('#messagesNumber')[0].innerHTML = 0;
            alert('No messages were fetched!');
        });
}

function diagnoses_history(apiurl) {
    if (DEBUG_ENABLE) {
        console.log('Retrieving the user history information');
    }

    apiurl = apiurl || ENTRYPOINT_USERS;
    return $.ajax({
            url: apiurl,
            dataType: DEFAULT_DATATYPE
        })
        .done(function (data, textStatus, jqXHR) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED RESPONSE: data:', data, '; textStatus:', textStatus);
            }
            var diagnoses = data.items;
            $('#diagnosesNumber')[0].innerHTML = diagnoses.length.toString();
            for (var i = 0; i < diagnoses.length; i++) {
                var diagnosis = diagnoses[i];
                get_diagnosis(diagnosis['@controls'].self.href);
            }
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED ERROR: textStatus:', textStatus,
                    ';error:', errorThrown);
            }
            // Inform user about the error using an alert message.
            $('#messagesNumber')[0].innerHTML = 0;
            alert('Could not fetch the list of diagnoses.');
        });
}

/**
 * Sends an AJAX request to delete an user from the system. Utilizes the DELETE
 *method.
 *
 * Associated rel attribute: delete (User profile)
 *
 *ONSUCCESS =>
 *    a)Show an alert informing the user that the user has been deleted
 *    b)Reload the list of users: {@link #getUsers}
 *
 * ONERROR =>
 *     a)Show an alert informing the user that the new information was not
 *stored in the databse
 *
 * @param {string} apiurl - The url of the intance to delete.
 **/
function delete_user(apiurl) {
    $.ajax({
            url: apiurl,
            type: 'DELETE',
        })
        .done(function (data, textStatus, jqXHR) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED RESPONSE: data:', data, '; textStatus:', textStatus);
            }
            alert('The user information has been deleted from the database');
            // Update the list of users from the server.
            getUsers();
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED ERROR: textStatus:', textStatus,
                    ';error:', errorThrown);
            }
            alert('The user information could not be deleted from the database');
        });
}

/**
 * This client does not support handling public user information
 *
 * Associated rel attribute: public-data
 *
 * @param {string} apiurl - The url of the Public profile instance.
 **/
function public_data(apiurl) {
    return; // THE CLIENT DOES NOT SHOW USER PUBLIC DATA SUCH AVATAR OR IMAGE
}

/**
 * Sends an AJAX request to retrieve the restricted profile information:
 * {@link
 *http://medical_forumapp.docs.apiary.io/#reference/users/users-private-profile/get-user's-restricted-profile
 *| User Restricted Profile}
 *
 * Associated rel attribute: private-data
 *
 * ONSUCCESS =>
 *  a) Extract all the links relations and its corresponding URLs (href)
 *  b) Create a form and fill it with attribute data (semantic descriptors)
 *coming from the request body. The generated form should be embedded into
 *#user_restricted_form. All those tasks are performed by the method {@link
 *#fillFormWithMasonData} b.1) If "user:edit" relation exists add its href to
 *the form action attribute. In addition make the fields editables and use
 *template to add missing fields. c) Add buttons to the previous generated form.
 *      c.1) If "user:delete" relation exists show the #deleteUserRestricted
 *button c.2) If "user:edit" relation exists show the #editUserRestricted button
 *
 * ONERROR =>
 *   a)Show an alert informing the restricted profile could not be retrieved and
 *     that the data shown in the screen is not complete.
 *   b)Unselect current user and go to initial state by calling {@link
 *#deselectUser}
 *
 * @param {string} apiurl - The url of the Restricted Profile instance.
 **/
function private_data(apiurl) {
    return $
        .ajax({
            url: apiurl,
            dataType: DEFAULT_DATATYPE,
        })
        .done(function (data, textStatus, jqXHR) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED RESPONSE: data:', data, '; textStatus:', textStatus);
            }
            var user_links = data['@controls'];
            var schema, resource_url = null;
            if ('edit' in user_links) {
                resource_url = user_links['edit'].href;
                schema = user_links['edit'].schema;
                if (user_links['edit'].schema) {
                    $form = createFormFromSchema(
                        resource_url, schema, 'user_restricted_form');
                    $('#editUserRestricted').show();
                    fillFormWithMasonData($form, data);
                } else if (user_links['edit'].schemaUrl) {
                    $.ajax({
                            url: user_links['edit'].schemaUrl,
                            dataType: DEFAULT_DATATYPE
                        })
                        .done(function (schema, textStatus, jqXHR) {
                            $form = createFormFromSchema(
                                resource_url, schema, 'user_restricted_form');
                            $('#editUserRestricted').show();
                            fillFormWithMasonData($form, data);
                        })
                        .fail(function (jqXHR, textStatus, errorThrown) {
                            if (DEBUG_ENABLE) {
                                console.log(
                                    'RECEIVED ERROR: textStatus:', textStatus,
                                    ';error:', errorThrown);
                            }
                            alert('Could not fetch form schema.  Please, try again');
                        });
                } else {
                    alert('Form schema not found');
                }
            }
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED ERROR: textStatus:', textStatus,
                    ';error:', errorThrown);
            }
            // Show an alert informing that I cannot get info from the user.
            alert(
                'Cannot extract all the information about this user from the server');
            deselectUser();
        });
}

/**
 * Sends an AJAX request to create a new user {@link
 *http://docs.pwpforum2017appcompleteversion.apiary.io/#reference/users/user}
 *
 * Associated link relation: add_user
 *
 *  ONSUCCESS =>
 *       a) Show an alert informing the user that the user information has been
 *modified b) Append the user to the list of users by calling {@link
 *#appendUserToList}
 *          * The url of the resource is in the Location header
 *          * {@link #appendUserToList} returns the li element that has been
 *added. c) Make a click() on the added li element. To show the created user's
 *information.
 *
 * ONERROR =>
 *      a) Show an alert informing that the new information was not stored in
 *the databse
 *
 * @param {string} apiurl - The url of the User instance.
 * @param {object} user - An associative array containing the new user's information
 *
 **/
function add_user(apiurl, user) {
    var userData = JSON.stringify(user);
    var username = user.username;
    return $
        .ajax({
            url: apiurl,
            type: 'POST',
            data: userData,
            processData: false,
            contentType: PLAINJSON
        })
        .done(function (data, textStatus, jqXHR) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED RESPONSE: data:', data, '; textStatus:', textStatus);
            }
            alert('User successfully added');
            $user = appendUserToList(jqXHR.getResponseHeader('Location'), user);
            $user.children('a').click();
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED ERROR: textStatus:', textStatus,
                    ';error:', errorThrown);
            }
            alert('Could not create new user:' + jqXHR.responseJSON.message);
        });
}

/**
 * Get user information.
 *
 * Associated rel attribute: up
 *
 * @param {string} apiurl - The url of the User instamce
 **/
function up(apiurl) {
    return; // We do not process this information.
}

/**
 * Sends an AJAX request to modify the restricted profile of a user, using PUT
 *
 * NOTE: This is NOT utilizied in this application.
 *
 * Associated rel attribute: edit (user profile)
 *
 * ONSUCCESS =>
 *     a)Show an alert informing the user that the user information has been
 *modified ONERROR => a)Show an alert informing the user that the new
 *information was not stored in the databse
 *
 * @param {string} apiurl - The url of the intance to edit.
 * @param {object} body - An associative array containing the new data of the
 *  target user
 *
 **/
function edit_user(apiurl, body) {
    $.ajax({
            url: apiurl,
            type: 'PUT',
            data: JSON.stringify(body),
            processData: false,
            contentType: PLAINJSON
        })
        .done(function (data, textStatus, jqXHR) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED RESPONSE: data:', data, '; textStatus:', textStatus);
            }
            alert('User information have been modified successfully');
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED ERROR: textStatus:', textStatus,
                    ';error:', errorThrown);
            }
            var error_message = $.parseJSON(jqXHR.responseText).message;
            alert('Could not modify user information;\r\n' + error_message);
        });
}

/**
 * Sends an AJAX request to retrieve information related to a User {@link
 *http://docs.pwpforum2017appcompleteversion.apiary.io/#reference/users/user}
 *
 * Associated link relation:self (inside the user profile)
 *
 *  ONSUCCESS =>
 *              a) Fill basic user information: username and registrationdate.
 *                  Extract the information from the attribute input
 *              b) Extract associated link relations from the response
 *                    b.1) If user:delete: Show the #deleteUser button. Add the
 *href to the #user_form action attribute. b.2) If user:edit: Show the #editUser
 *button. Add the href to the #user_form action attribute. b.3) If
 *user:restricted data: Call the function {@link #private_data} to extract the
 *information of the restricted profile b.4) If user:messages: Call the function
 *{@link #messages_history} to extract the messages history of the current user.
 **
 *
 * ONERROR =>   a) Alert the user
 *              b) Unselect the user from the list and go back to initial state
 *                (Call {@link deleselectUser})
 *
 * @param {string} apiurl - The url of the User instance.
 **/
function get_user(apiurl) {
    return $
        .ajax({
            url: apiurl,
            dataType: DEFAULT_DATATYPE,
            processData: false,
        })
        .done(function (data, textStatus, jqXHR) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED RESPONSE: data:', data, '; textStatus:', textStatus);
            }
            // Set right url to the user form
            $('#user_form').attr('action', apiurl);
            // Fill basic information from the user_basic_form
            $('#username').val(data.username || '??');
            $('#userID').val(data.user_id);
            $('#registrationDate').val(getDate(data.reg_date || 0));
            $('#messagesNumber').text('??');
            $('#userType').val(data.user_type == 0 ? 'Patient' : 'Doctor');

            if (data.user_type == 1) {
                $('#DoctorSpeciality').parent().show();
                $('#DoctorSpeciality').val(data.speciality || '??');
            } else {
                $('#DoctorSpeciality').parent().hide();
            }

            // Extract user information
            var user_links = data['@controls'];
            if ('medical_forum:delete' in user_links) {
                resource_url =
                    user_links['medical_forum:delete'].href; // User delete link
                $('#deleteUser').show();
            }
            // Extracts urls from links. I need to get if the different links in the
            // response.
            if ('medical_forum:private-data' in user_links) {
                var private_profile_url =
                    user_links['medical_forum:private-data'].href;
            }
            if ('medical_forum:messages-history' in user_links) {
                var messages_url = user_links['medical_forum:messages-history'].href;
                // cut out the optional query parameters. this solution is not pretty.
                messages_url = messages_url.slice(0, messages_url.indexOf('{?'));
            }

            // fill new message actions
            $('#newMessageAuthor').val(data.username);
            console.log(data.username);
            $('#NewMessageForm').attr('action', data['@controls']["medical_forum:messages-all"].href);

            if (data.user_type == 1 &&
                'medical_forum:diagnoses-all' in user_links) {
                var diagnoses_url = user_links['medical_forum:diagnoses-all'].href;
            } else if (
                data.user_type == 0 &&
                'medical_forum:diagnoses-history' in user_links) {
                var diagnoses_url =
                    user_links['medical_forum:diagnoses-history'].href;
            }

            // Fill the user profile with restricted user profile. This method
            // Will call also to the list of messages.
            if (private_profile_url) {
                private_data(private_profile_url);
            }
            // Get the history link and ask for history.
            if (messages_url) {
                if (data.user_type == 0)
                    messages_history(messages_url);
                else
                    messages_history(user_links['medical_forum:messages-all'].href);
                $('#diagnoses_list').empty();
                $('#diagnosesNumber').text('??');
                if (diagnoses_url) diagnoses_history(diagnoses_url);
            }

            // delete(data.username);
            // delete(data.reg_date);
            // delete(data.user_type);
            // delete(data.speciality);
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED ERROR: textStatus:', textStatus,
                    ';error:', errorThrown);
            }
            // Show an alert informing that I cannot get info from the user.
            alert(
                'Cannot extract information about this user from the forum service.');
            // Deselect the user from the list.
            deselectUser();
        });
}

/**** END RESTFUL CLIENT****/

/**** UI HELPERS ****/

/**** This functions are utilized by rest of the functions to interact with the
      UI ****/

/**
 * Append a new user to the #patients_list and #doctors_list. It appends a new
 *<li> element in the #patients_list and #doctors_list using the information
 *received in the arguments.
 *
 * @param {string} url - The url of the User to be added to the list
 * @param {string} user - the User to be added to the list
 * @returns {Object} The jQuery representation of the generated <li> elements.
 **/
function appendUserToList(url, user) {
    var user_icon = USER_ICON;
    if (user.user_type == 1) user_icon = DOCTOR_ICON;
    var $user = $('<li class="nav-item">')
        .html(
            '<a class= "user_link nav-link" href="' + url +
            '"><span class="' + user_icon + '"></span>  ' +
            user.username + '</a>');
    user.user_type == 0 ? $('#patients_list').append($user) :
        $('#doctors_list').append($user);
    return $user;
}

/**
 * Populate a form with the <input> elements contained in the <i>schema</i>
 *input parameter. The action attribute is filled in with the <i>url</i>
 *parameter. Values are filled with the default values contained in the
 *template. It also marks inputs with required property.
 *
 * @param {string} url - The url of to be added in the action attribute
 * @param {Object} schema - a JSON schema object ({@link http://json-schema.org/})
 * which is utlized to append <input> elements in the form
 * @param {string} id - The id of the form is gonna be populated
 **/
function createFormFromSchema(url, schema, id) {
    $form = $('#' + id);
    $form.attr('action', url);
    // Clean the forms
    $form_content = $('.form_content', $form);
    $form_content.empty();
    $('input[type=\'button\']', $form).hide();
    if (schema.properties) {
        var props = schema.properties;
        Object.keys(props).forEach(function (key, index) {
            if (props[key].type == 'object') {
                appendObjectFormFields($form_content, key, props[key]);
            } else {
                appendInputFormField(
                    $form_content, key, props[key], schema.required.includes(key));
            }
        });
    }
    return $form;
}

/**
 * Private class used by {@link #createFormFromSchema}
 *
 * @param {jQuery} container - The form container
 * @param {string} The name of the input field
 * @param {Object} object_schema - a JSON schema object ({@link http://json-schema.org/})
 * which is utlized to append properties of the input
 * @param {boolean} required- If it is a mandatory field or not.
 **/
function appendInputFormField($container, name, object_schema, required) {
    var input_id = name;
    var prompt = object_schema.title;
    var desc = object_schema.description;

    $input = $('<input type="text" class="form-control"></input>');
    $input.addClass('editable');
    $input.attr('name', name);
    $input.attr('id', input_id);
    $label_for = $('<label class="col-sm-4 col-form-label"></label>');
    $label_for.attr('for', input_id);
    $label_for.text(prompt);

    $container.append($label_for);
    $container.append($input);

    // $container.append($('<div class="form-group
    // row"></div>').append($label_for, $('<div
    // class="col-sm-8"></dive>').append($input)));

    if (desc) {
        $input.attr('placeholder', desc);
    }
    if (required) {
        $input.prop('required', true);
        $label = $('label[for=\'' + $input.attr('id') + '\']');
        $label.append('*');
    }
}

/**
 * Private class used by {@link #createFormFromSchema}. Appends a subform to
 *append input
 *
 * @param {jQuery} $container - The form container
 * @param {string} The name of the input field
 * @param {Object} object_schema - a JSON schema object ({@link http://json-schema.org/})
 * which is utlized to append properties of the input
 * @param {boolean} required- If it is a mandatory field or not.
 **/
function appendObjectFormFields($container, name, object_schema) {
    $div = $('<div class="subform form-group"></div>');
    $div.attr('id', name);
    Object.keys(object_schema.properties).forEach(function (key, index) {
        if (object_schema.properties[key].type == 'object') {
            // only one nested level allowed therefore do nothing
        } else {
            appendInputFormField($div, key, object_schema.properties[key], false);
        }
    });
    $container.append($div);
}

/**
 * Populate a form with the content in the param <i>data</i>.
 * Each data parameter is going to fill one <input> field. The name of each
 *parameter is the <input> name attribute while the parameter value attribute
 *represents the <input> value. All parameters are by default assigned as
 * <i>readonly</i>.
 *
 * NOTE: All buttons in the form are hidden. After executing this method
 *adequate buttons should be shown using $(#button_name).show()
 *
 * @param {jQuery} $form - The form to be filled in
 * @param {Object} data - An associative array formatted using Mason format ({@link https://tools.ietf.org/html/draft-kelly-json-hal-07})
 **/
function fillFormWithMasonData($form, data) {
    console.log('filling form with mason data');
    $('.form_content', $form).children('input').each(function () {
        if (data[this.id]) {
            $(this).attr('value', data[this.id]);
        }
    });

    $('.form_content', $form)
        .children('.subform')
        .children('input')
        .each(function () {
            var parent = $(this).parent()[0];
            if (data[parent.id][this.id]) {
                $(this).attr('value', data[parent.id][this.id]);
            }
        });
}

/**
 * Serialize the input values from a given form (jQuery instance) into a
 * JSON document.
 *
 * @param {Object} $form - a jQuery instance of the form to be serailized
 * @returs {Object} An associative array in which each form <input> is converted
 * into an element in the dictionary.
 **/
function serializeFormTemplate($form) {
    var envelope = {};
    var $inputs = $form.find('.form_content input');
    $inputs.each(function () {
        envelope[this.id] = $(this).val();
    });

    ClearSpecialityForNonDoctor(envelope);
    return envelope;
}

function serializeMessageForm($form) {
    var envelope = {};
    var $inputs = $form.find('input');
    $inputs.each(function () {
        envelope[this.name] = $(this).val();
    });
    $inputs = $form.find('textarea');
    $inputs.each(function () {
        envelope[this.name] = $(this).val();
    });
    return envelope;
}

function ClearSpecialityForNonDoctor(envelope) {
    if (envelope['user_type'] == 0) {
        console.log('changing the speciality');
        envelope['speciality'] = '';
    }
}

/**
 * Add a new .message HTML element in the to the #messages_list <div> element.
 * The format of the generated HTML is the following:
 * @example
 *  //<div class='message'>
 *  //        <form action='#'>
 *  //            <div class="commands">
 *  //                <input type="button" class="editButton editMessage"
 *value="Edit"/>
 *  //                <input type="button" class="deleteButton deleteMessage"
 *value="Delete"/>
 *  //             </div>
 *  //             <div class="form_content">
 *  //                <input type=text class="headline">
 *  //                <input type="textarea" class="articlebody">
 *  //             </div>
 *  //        </form>
 *  //</div>
 *
 * @param {string} url - The url of the created message
 * @param {string} headline - The title of the new message
 * @param {string} articlebody - The body of the crated message.
 **/
function appendMessageToList(data) {
    var $message = $('<div>').addClass('message').html(
        '' +
        '<form action=\'' + data['@controls'].self.href + '\'>' +
        '       <div class=\'commands section\'>' +
        '            <button  class=\'deleteButton deleteMessage btn\' title=\'Remove message\'>' +
        '                     <span class=\'' + DELETE_ICON + '\' ></span>' +
        '            </button>' +
        '            <button  class=\'editButton editMessage btn\' title=\'Edit message\'>' +
        '                     <span class=\'' + EDIT_ICON + '\' ></span>' +
        '            </button>' +
        '            <button data-toggle=\'collapse\' href=\'#NewDiagnosis\' ' +
        '                   class=\'btn\' title=\'Add diagnosis\'>' +
        '                     <span class=\'' + ADD_DIAG_ICON + '\' ></span>' +
        '            </button>' +
        '       </div>' +
        '       <div class=\'form_content row\'>' +
        '           <input type=\'text\' name=\'headline\' class=\'headline form-control editable' +
        '                   font-weight-bold\' value=\'' + data.headline + '\'/>' +
        '           <textarea class=\'articlebody form-control\' name=\'articleBody\' rows=\'3\'>' + data.articleBody +
        '           </textarea>' +
        '       </div>' +
        '</form>' +

        '<div id=\'NewDiagnosis\' class=\'collapse\'>' +
        '   <form id=\'NewDiagnosisForm\' action=\'' + data['@controls']['medical_forum:add-diagnosis-with-user'].href + '\'>' +
        '       <div class=\'text-center row\'>' +
        '           <h4>Add new diagnosis</h4>' +
        '       </div>' +
        '       <div class=\'form-group row\'>' +
        '           <label for=\'NewDiagnosisUserID\' class=\'col-sm-2 col-form-label\'>UserID </label>' +
        '           <div class=\'col-sm-10\'>' +
        // data['@controls']['medical_forum:add-diagnosis-with-user'].user_id
        '               <input type=\'text\' name=\'user_id\' id=\'NewDiagnosisUserID\' value=\'' + $('#userID').val() + '\'class=\'form-control\' readonly>' +
        '           </div>' +
        '       </div>' +
        '       <div class=\'form-group row\'>' +
        '           <label for=\'NewDiagnosisDisease\' class=\'col-sm-2 col-form-label\'>Disease </label>' +
        '           <div class=\'col-sm-10\'>' +
        '               <input type=\'text\' name=\'disease\' id=\'NewDiagnosisDisease\' class=\'form-control\'>' +
        '           </div>' +
        '       </div>' +
        '       <div class=\'form-group row\'>' +
        '           <label for=\'NewDiagnosisBody\' class=\'col-sm-2 col-form-label\'>Description </label>' +
        '           <div class=\'col-sm-10\'>' +
        '               <textarea id=\'NewDiagnosisBody\' name=\'diagnosis_description\'' +
        '                   placeholder=\'Diagnosis description\' class=\'form-control editable\' rows=\'3\'>' +
        '               </textarea>' +
        '           </div>' +
        '       </div>' +
        '       <div class=\'col-md-4 text-center\'>' +
        '           <button id=\'addDiagnosis\' class=\'addButton addDiagnosis glyphicon glyphicon-send btn btn-primary\' ' +
        '               title=\'Send diagnosis\'> Send</button>' +
        '       </div>' +
        '   </form>' +
        '</div>'
    );

    $('#messages_list').append($message);
}

function appendDiagnosisToList(data) {
    var $diagnosis =
        $('<div>')
        .addClass('diagnosis')
        .html(
            '' +
            '<form action=\'' + data['@controls'].self.href + '>' +
            '   <div class=\'row\'>' +
            '       <div class=\'form_content col-md-8\'>' +
            '           <label type=\'text\' class=\'headline form-control-plaintext font-weight-bold\'>' +
            'User ID: ' + data.user_id + '</label>' +
            '       <div class=\'col-md-8\'>' +
            '           <label type=\'text\' class=\'headline form-control-plaintext font-weight-bold\'>' +
            'Disease: ' + data.disease + '</label>' +
            '           <div class=\'articlebody form-control-plaintext\' readonly=\'readonly\'>' +
            data.diagnosis_description + '</div>' +
            '       </div>' +
            '       <div class=\'commands col-md-4\'>' +
            '       </div>' +
            '   </div>' +
            '</form>');

    $('#diagnoses_list').append($diagnosis);
}

/**
 * Helper method to be called before showing new user data information
 * It purges old user's data and hide all buttons in the user's forms (all forms
 * elements inside teh #userData)
 *
 **/
function prepareUserDataVisualization() {
    $('#userProfile .form_content').empty();
    $('#userData .commands input[type=\'button\']').hide();
    $('#userData input[type=\'text\']').val('??');
    $('#messages_list').empty();
    $('#newUser').hide();
    $('#userData').show();
    $('#mainContent').show();
}

/**
 * Helper method to visualize the form to create a new user (#new_user_form)
 * It hides current user information and purge old data still in the form. It
 * also shows the #createUser button.
 **/
function showNewUserForm() {
    deselectUser();
    $('#userData').hide();
    var form = $('#new_user_form')[0];
    form.reset();
    $('input[type=\'button\']', form).show();
    $('#newUser').show();
    $('#mainContent').show();
}

/**
 * Helper method that unselects any user from the #patients_list and
 *#doctors_list and go back to the initial state by hiding the "#mainContent".
 **/
function deselectUser() {
    $('#patients_list li.active').removeClass('active');
    $('#doctors_list li.active').removeClass('active');
    $('#mainContent').hide();
}

/**
 * Helper method to reload current user's data by making a new API call
 * Internally it makes click on the href of the active user.
 **/
function reloadUserData() {
    $('#patients_list li.active a').click();
    $('#doctors_list li.active a').click();
}

/**
 * Transform a date given in a UNIX timestamp into a more user friendly string
 *
 * @param {number} timestamp - UNIX timestamp
 * @returns {string} A string representation of the UNIX timestamp with the
 * format: 'dd.mm.yyyy at hh:mm:ss'
 **/
function getDate(timestamp) {
    var date = new Date(timestamp * 1000);
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var seconds = date.getSeconds();
    var day = date.getDate();
    var month = date.getMonth() + 1;
    var year = date.getFullYear();

    return day + '.' + month + '.' + year + ' at ' + hours + ':' + minutes + ':' +
        seconds;
}
/**** END UI HELPERS ****/

/**** BUTTON HANDLERS ****/

/**
 * Shows in #mainContent the #new_user_form. Internally it calls to {@link
 *#showNewUserForm}
 **/
function handleShowUserForm(event) {
    if (DEBUG_ENABLE) {
        console.log('Triggered handleShowUserForm');
    }
    showNewUserForm();
    return false;
}

/**
 * Uses the API to delete the currently active user.
 **/
function handleDeleteUser(event) {
    if (DEBUG_ENABLE) {
        console.log('Triggered handleDeleteUser');
    }
    var userUrl = $(this).closest('form').attr('action');
    delete_user(userUrl);
    return false;
}

/**
 * Uses the API to update the user's restricted profile with the form attributes
 *in the present form.
 **/
function handleEditUserRestricted(event) {
    if (DEBUG_ENABLE) {
        console.log('Triggered handleDeleteUserRestricted');
    }
    var $form = $('#user_restricted_form');
    var body = serializeFormTemplate($form);
    console.log(body);
    var user_restricted_url = $('#user_restricted_form').attr('action');
    edit_user(user_restricted_url, body);
    return false;
}

/**
 * Uses the API to create a new user with the form attributes in the present
 *form.
 **/
function handleCreateUser(event) {
    if (event.click) {
        console.log('Triggered handleCreateUser');
    }
    var $form = $(this).closest('form');
    var template = serializeFormTemplate($form);
    var url = $form.attr('action');
    add_user(url, template);
    return false; // Avoid executing the default submit
}

/**
 * Uses the API to retrieve user's information from the clicked user. In
 *addition, this function modifies the active user in the #patients_list and
 *#doctors_list (removes the .active class from the old user and add it to the
 *current user)
 **/
function handleGetUser(event) {
    if (DEBUG_ENABLE) {
        console.log('Triggered handleGetUser');
    }
    event.preventDefault();

    $('#patients_list li.active').removeClass('active');
    $('#doctors_list li.active').removeClass('active');
    $(this).parent().addClass('active');

    prepareUserDataVisualization();
    var href = ($(this)).attr('href');
    get_user(href);

    return false;
}

/**
 * Uses the API to delete the associated message
 **/
function handleDeleteMessage(event) {
    // event.preventDefault();
    if (DEBUG_ENABLE) {
        console.log('Triggered handleDeleteMessage');
    }
    event.preventDefault();
    var messageUrl = $(this).closest('form').attr('action');
    console.log("message to delete url: " + messageUrl);
    delete_message(messageUrl);
}

function handleEditMessage(event) {
    if (DEBUG_ENABLE) {
        console.log('Triggered handleEditMessage');
    }
    event.preventDefault();
    var messageUrl = $(this).closest('form').attr('action');
    console.log("message to edit url: " + messageUrl);

    var body = serializeMessageForm($(this).closest('form'));
    console.log(body);
    edit_message(messageUrl, body);
}

function handleAddMessage(event) {
    if (DEBUG_ENABLE) {
        console.log('Triggered handleAddMessage');
    }
    event.preventDefault();
    var messageUrl = $("#NewMessageForm").attr('action');

    var body = serializeMessageForm($("#NewMessageForm"));
    body['author'] = $("#newMessageAuthor").val();
    addMessage(messageUrl, body);
    console.log(body);
}

function handleAddDiagnosis(event) {
    if (DEBUG_ENABLE) {
        console.log('Triggered handleAddDiagnosis');
    }

    event.preventDefault();
    var diagnosisUrl = $("#NewDiagnosisForm").attr('action');
    var body = serializeMessageForm($("#NewDiagnosisForm"));
    body['user_id'] = $("#userID").val();
    var messageurl = $("#NewDiagnosisForm").parent().parent().find('form').attr('action');
    body['message_id'] = messageurl.match(/\d{1,3}/)['0'];
    console.log("url dgs: ", diagnosisUrl);
    console.log(body);
    addDiagnosis(diagnosisUrl, body);
}

function addDiagnosis(apiurl, body) {
    return $
        .ajax({
            url: apiurl,
            type: 'POST',
            data: JSON.stringify(body),
            processData: false,
            contentType: PLAINJSON
        })
        .done(function (data, textStatus, jqXHR) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED RESPONSE: data:', data, '; textStatus:', textStatus);
            }
            alert('Diagnosis successfully added');
            reloadUserData();
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED ERROR: textStatus:', textStatus,
                    ';error:', errorThrown);
            }
            alert('Could not create new Diagnosis:' + jqXHR.responseJSON.message);
        });
}

function addMessage(apiurl, body) {

    var messageData = JSON.stringify(body);
    return $
        .ajax({
            url: apiurl,
            type: 'POST',
            data: messageData,
            processData: false,
            contentType: PLAINJSON
        })
        .done(function (data, textStatus, jqXHR) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED RESPONSE: data:', data, '; textStatus:', textStatus);
            }
            alert('Message successfully added');
            reloadUserData();
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            if (DEBUG_ENABLE) {
                console.log(
                    'RECEIVED ERROR: textStatus:', textStatus,
                    ';error:', errorThrown);
            }
            alert('Could not create new message:' + jqXHR.responseJSON.message);
        });
}

/**** END BUTTON HANDLERS ****/

// This method is executed when the webpage is loaded.
$(function () {
    $('#addUserButton').click(handleShowUserForm);
    $('#deleteUser').click(handleDeleteUser);
    $('#editUserRestricted').click(handleEditUserRestricted);
    $('#deleteUserRestricted').click(handleDeleteUser);
    $('#createUser').click(handleCreateUser);

    $('#messages_list').on('click', '.deleteMessage', handleDeleteMessage);
    $('#messages_list').on('click', '.editMessage', handleEditMessage);
    $('#messages').on('click', '#addMessage', handleAddMessage);
    $('#messages_list').on('click', '.addDiagnosis', handleAddDiagnosis);
    $('#patients_list').on('click', 'li a', handleGetUser);
    $('#doctors_list').on('click', 'li a', handleGetUser);

    getUsers(ENTRYPOINT_USERS);
});