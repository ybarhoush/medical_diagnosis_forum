"""
Main medical forum server
"""

from medical_forum.resources import APP

if __name__ == '__main__':
    # Debug true activates automatic code reloading and improved error messages
    APP.run(debug=True)
