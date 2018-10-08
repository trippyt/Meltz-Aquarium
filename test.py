import time
import requests

        # Toggle Modes
OFF = 0
DAY = 1
NIGHT = 2
VALID_TOGGLE_MODES = [OFF, DAY, NIGHT]

TOGGLE_MODE_STR = ['off', 'day', 'night']
MODE_STR_TO_NUM = {'off': OFF, 'night': NIGHT, 'day': DAY}
 

 
class LightsMenu():
    def __init__(self): #Default settings
        self.session = None
        self.web_login()
        self.running = False
        self.is_setup = False
        self.curr_idx = 0
        self.curr_mode = 0
 
    def begin(self):
        self.is_setup = False
        self.running = True
        
    def right(self):
        self.curr_mode = (self.curr_mode + 1) % len(MODE_STR_TO_NUM)
        new_sch = self.curr_mode
        self.set_schedule(new_sch)
        print("mode + 1")
        return True
    
    def get_schedule(self):
            resp = self.session.get('http://trippyt.hopto.org/schedule')
            if '<form action="/login" method="POST">' in resp.text:
                self.web_login()
                resp = self.session.get('http://trippyt.hopto.org/schedule')
            light_state = resp.json()
            return(light_state['value'])

    def set_schedule(self, new_sch):
        resp = self.session.get('http://trippyt.hopto.org/schedule/schedule')
        if '<form action="/login" method="POST">' in resp.text:
            self.web_login()
            
        light_state = {'value': new_sch}
        self.session.post('http://trippyt.hopto.org/schedule', data=light_state)

    def web_login(self):
        self.session = requests.Session()
        payload = {'username':'admin','password':'password'}
        self.session.post('http://trippyt.hopto.org/login',data=payload)
