import sys
import os
import time
import threading
import AquariumLights
from flask import Flask, flash, redirect, render_template, request, session, abort, jsonify, redirect, url_for
from sqlalchemy.orm import sessionmaker
from tabledef import *
import logging

logger = logging.getLogger("AquariumLights")

lights_control = AquariumLights.LightControl()

engine = create_engine('sqlite:///tutorial.db', echo=True)

app = Flask('Flask')
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(logger)

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.route('/login', methods=['POST'])
def do_admin_login():
 
    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])
 
    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(User).filter(User.username.in_([POST_USERNAME]), User.password.in_([POST_PASSWORD]) )
    result = query.first()
    if result:
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return redirect(url_for('main'))

@app.route("/")
def main():
    if not session.get('logged_in'):
        return render_template('login.html')

    app.logger.debug('hello')
    templateData = {
        'config_state': lights_control.get_config_state()
    }
    templateDate["config_state"]["toggle"] = lights_control.TOGGLE_MODE_STR[templateDate["config_state"]["toggle"]]
    templateDate["config_state"]["schedule"] = [lights_control.TOGGLE_MODE_STR[i] for i in templateDate["config_state"]["schedule"]]
    # Pass the template data into the template main.html and return it to the user
    return render_template('main.html', **templateData)

# The function below is executed when someone requests a URL with the pin number and action in it:
@app.route("/<key>", methods=["GET", "POST"])
def handleattr(key):
    if not session.get('logged_in'):
        return render_template('login.html')

    value = ''

    if key == 'favicon.ico':
        return 'None'

    if not hasattr(lights_control, key):
        raise InvalidUsage( 'Invalid attribute name {}'.format(key) )

    if request.method == "GET":
        value = lights_control.get_config_state().get(key,'Unknown')
        app.logger.debug("GET Key: {}, value: {}".format(key, value))
        return jsonify({'value': value})

    elif request.method == "POST":
        if len(request.form.getlist('value[]')) > 0:
            new_val = [i for i in request.form.getlist('value[]')]
        elif len(request.form.getlist('value')) > 1:
            new_val = [i for i in request.form.getlist('value')]
        else:
            new_val = request.form.get('value',None)
        app.logger.debug("POST Key: {}, value: {}".format(key, new_val))
        setattr(lights_control, key, new_val)
        return jsonify('success')

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return main()

def periodic_check_handler(wait_time):
    """
    Function to periodically call lights_control.check()
    """
    while True:
        time.sleep(wait_time)
        lights_control.check()

if __name__ == "__main__":
    app.debug = True
    app.secret_key = os.urandom(12)
    check_thread = threading.Thread(target=periodic_check_handler, args=(1,), daemon=True)
    check_thread.start()
    try:
        app.run(host='0.0.0.0', port=80, debug=True)
    except Exception:
        import traceback
        traceback.print_exc(file=open('/home/pi/Meltz-Aquarium/Server/Logs/error.log', 'w'))