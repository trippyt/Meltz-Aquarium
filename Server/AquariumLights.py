import time
from datetime import datetime
import logging
import pickle, os
try:
    import RPi.GPIO as GPIO
except:
    import dummyGPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(5,GPIO.OUT)

# Toggle Modes
OFF = 0
DAY = 1
NIGHT = 2
VALID_TOGGLE_MODES = [OFF, DAY, NIGHT]

TOGGLE_MODE_STR = ['off', 'day', 'night']

log_file = "/home/pi/Meltz-Aquarium/Server/Logs/logfile{}.log".format(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
#log_file = "/home/pi/Meltz-Aquarium/Server/Logs/logfile{}.log".format(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
# "logfile{}.log".format(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
logger = logging.getLogger("AquariumLights")

handler = logging.FileHandler(log_file)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

for i in range(1):
    logger.info("This is a test!")


class LightControl(object):
    def __init__(self):  # Default settings
    # if file doesn't exist, these are defaults
        if not os.path.isfile('pickle.dat'):
            self._auto = True
            self._toggle = OFF
            self._current_status = 'unknown'
            self._schedule = [OFF for i in range(24)]

            #saves defaults to a file
            with open('pickle.dat', 'wb') as file:
                data = (self.get_state())
                pickle.dump(data, file)
        # otherwise, load from a file
        else:
            with open('pickle.dat', "rb") as file:
                data = pickle.load(file)
                self._auto = data['auto']
                self._toggle = data['toggle']
                self._current_status = 'unknown' # what about this?
                self._schedule = data['schedule']
        

    @property
    def schedule(self):
        return [TOGGLE_MODE_STR[i] for i in self._schedule]

    @schedule.setter
    def schedule(self, new_val):
        logger.debug('set schedule ' + str(new_val))

        # checks input length
        if len(new_val) != 24:
            raise(Exception('Schedule length must be 24, but had a length of {}!'.format(new_val)))

        # converts input to list of 0,1,2
        if isinstance(new_val[0], str):
            if new_val[0] in TOGGLE_MODE_STR:
                # new_val is "off", "night", "day"
                self._schedule = [TOGGLE_MODE_STR.index(mode.lower()) for mode in new_val]
            else:
                # new_val is "0", "1", "2"
                self._schedule = [int(i)%len(TOGGLE_MODE_STR) for i in new_val]
        elif isinstance(new_val[0], int):
            # new_val is 0, 1, 2
            self._schedule = [i%len(TOGGLE_MODE_STR) for i in new_val]
        else:
            raise(Exception('Unknown format of Schedule array'))

        # storing schedule data
        # first needa fetch it
        data = ""
        with open('pickle.dat', "rb") as file:
            data = pickle.load(file)
            data['schedule'] = self._schedule # rewriting existing with current
        # storing
        with open('pickle.dat', "wb") as file:
            pickle.dump(data, file)

    @property
    def auto(self):
        return self._auto

    @auto.setter
    def auto(self, new_val):
        self._auto = bool(int(new_val) and True)
        # storing auto mode data
        # first needa fetch it
        data = ""
        with open('pickle.dat', "rb") as file:
            data = pickle.load(file)
            data['auto'] = self._auto # rewriting existing with current
        # storing
        with open('pickle.dat', "wb") as file:
            pickle.dump(data, file)

    @property
    def toggle(self):
        return self._toggle

    @toggle.setter
    def toggle(self, new_val):
        # varifying the input
        if int(new_val) not in VALID_TOGGLE_MODES:
            raise(Exception('AquariumLights: Invalid toggle mode!'))

        # setting
        self._toggle = int(new_val)

        # storing
        # first needa fetch it
        data = ""
        with open('pickle.dat', "rb") as file:
            data = pickle.load(file)
            data['toggle'] = self._toggle # rewriting existing with current

        # storing toggle mode data
        with open('pickle.dat', "wb") as file:
            pickle.dump(data, file)

    def get_state(self):
        return {'auto': self._auto,
                'toggle': self._toggle,
                'schedule': self._schedule
                }

    def get_config_state(self):
        return {'auto': self._auto,
                'toggle': TOGGLE_MODE_STR[self._toggle],
                'schedule': [TOGGLE_MODE_STR[i] for i in self._schedule]
                }

    def daylights_on(self): #Activates Daylights
        if self._current_status != 'day':
            self._current_status = 'day'
            GPIO.output(13,0)
            GPIO.output(5,1)
            GPIO.output(13,1)
            print("DayLights: On")
            logger.debug("Day Mode is Active")

    def nightlights_on(self): #Activates Nightlights
        if self._current_status != 'night':
            self._current_status = 'night'
            GPIO.output(13,0)
            GPIO.output(5,1)
            GPIO.output(13,0)
            print("NightLights: On")
            logger.debug("Night Mode is Active")

    def lights_off(self): # Deactivates any light mode
        if self._current_status != 'off':
            self._current_status = 'off'
            GPIO.output(5,0)
            print("Lights: Off")
            logger.debug("Off Mode is Active")

    def check(self):
        if self._auto == True:
            print('Auto Mode')
            self.light_logic()
        elif self._toggle == OFF:
            print('Toggle Mode Off')
            self.lights_off()
        elif self._toggle == DAY:
            print('Toggle Mode Day')
            self.daylights_on()
        elif self._toggle == NIGHT:
            print('Toggle Mode Night')
            self.nightlights_on()

    def light_logic(self):
        hour = int(time.strftime('%H'))

        if self._schedule[hour] == DAY:
            self.daylights_on()
        elif self._schedule[hour] == NIGHT:
            self.nightlights_on()
        else:
            self.lights_off()
            print('Hour not found in any range!')