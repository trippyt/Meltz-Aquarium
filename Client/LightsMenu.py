import time
import requests
from dot3k.menu import Menu, MenuOption

# Toggle Modes
OFF = 0
DAY = 1
NIGHT = 2
VALID_TOGGLE_MODES = [OFF, DAY, NIGHT]

TOGGLE_MODE_STR = ['off', 'day', 'night']
MODE_STR_TO_NUM = {'off': OFF, 'night': NIGHT, 'day': DAY}
 
class LightsMenu(MenuOption):
    def __init__(self): #Default settings
        self.session = None
        self.web_login()
        self.running = False
        self.is_setup = False
        self.curr_idx = 0
        MenuOption.__init__(self)
 
    def begin(self):
        self.is_setup = False
        self.running = True
 
    def setup(self, config):
        MenuOption.setup(self, config)
        self.curr_idx = 0
        schedule = self.get_schedule()
        mode_str = schedule[self.curr_idx]
        self.curr_mode = MODE_STR_TO_NUM[mode_str]
       
    def cleanup(self):
        self.running = False
        time.sleep(0.01)
        self.is_setup = False
 
    def left(self):
        self.curr_mode = (self.curr_mode - 1) % len(VALID_TOGGLE_MODES)
        new_sch = self.get_schedule()
        new_sch[self.curr_idx] = TOGGLE_MODE_STR[self.curr_mode]
        self.set_schedule(new_sch)
        return True
       
    def right(self):
        self.curr_mode = (self.curr_mode + 1) % len(VALID_TOGGLE_MODES)
        new_sch = self.get_schedule()
        new_sch[self.curr_idx] = TOGGLE_MODE_STR[self.curr_mode]
        self.set_schedule(new_sch)
        return True

    def up(self):
        self.curr_idx = (self.curr_idx - 1) % len(self.get_schedule())
        self.curr_mode = self.get_schedule()[self.curr_idx]
        return True

    def down(self):
        self.curr_idx = (self.curr_idx + 1) % len(self.get_schedule())
        self.curr_mode = self.get_schedule()[self.curr_idx]
        return True
       
 
    def up(self):
        self.curr_idx = (self.curr_idx - 1) % len(self.get_schedule())
        self.curr_mode = self.lights_control._schedule[ self.curr_idx ]
        return True
 
    def down(self):
        self.curr_idx = (self.curr_idx + 1) % len(self.get_schedule())
        self.curr_mode = self.lights_control._schedule[ self.curr_idx ]
        return True
 
    def redraw(self, menu):
        if not self.running:
            return False
 
        if not self.is_setup:
            menu.lcd.create_char(0, [0, 0, 0, 14, 17, 17, 14, 0])
            menu.lcd.create_char(1, [0, 0, 0, 14, 31, 31, 14, 0])
            menu.lcd.create_char(2, [0, 14, 17, 17, 17, 14, 0, 0])
            menu.lcd.create_char(3, [0, 14, 31, 31, 31, 14, 0, 0])
            menu.lcd.create_char(4, [0, 4, 14, 0, 0, 14, 4, 0])  # Up down arrow
            menu.lcd.create_char(5, [0, 0, 10, 27, 10, 0, 0, 0])  # Left right arrow
            self.is_setup = True
 
        hour = float(time.strftime('%H'))
        print(hour)
        menu.write_row(0, time.strftime('  %a %H:%M:%S  '))
 
        menu.write_row(1, '-' * 16)
 
        if self.idling:
            menu.clear_row(2)
            return True
 
        self.curr_mode = self.get_schedule()[ self.curr_idx ]
 
        bottom_row = ''

        mode_str = TOGGLE_MODE_STR[ int(self.curr_mode) ].upper()
        bottom_row = '{:02}:00 \x05Mode:{}'.format(self.curr_idx, mode_str)
 
        menu.write_row(2, chr(4) + bottom_row)

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