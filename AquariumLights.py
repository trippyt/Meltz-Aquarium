import time
from datetime import datetime
import logging
import pickle
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

log_file = "/home/pi/Aquarium/meltz/Logs/logfile{}.log".format(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
#log_file = r"c:\temp\aqlog.log"
logger = logging.getLogger("AquariumLights")

handler = logging.FileHandler(log_file)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

for i in range(1):
    logger.info("This is a test!")


class LightControl(object):
    def __init__(self): #Default settings
        self._auto = True
        self._toggle = OFF
        self._day_hour = 7
        self._night_hour = 21
        self._off_hour = 23
        self._current_status = 'unknown'
        self._schedule = [OFF for i in range(24)]
        

    @property
    def schedule(self):
        return [TOGGLE_MODE_STR[i] for i in self._schedule]

    @schedule.setter
    def schedule(self, new_val):
        logger.debug('set schedule ' + str(new_val))
        if len(new_val) != 24:
            raise(Exception('Schedule length must be 24!'))

        if isinstance(new_val[0], str):
            if new_val[0] in TOGGLE_MODE_STR:
                # schedule array is "off", "night", "day"
                self._schedule = [TOGGLE_MODE_STR.index(mode.lower()) for mode in new_val]
            else:
                # schedule array is "0", "1", "2"
                self._schedule = [int(i)%len(TOGGLE_MODE_STR) for i in new_val]
        elif isinstance(new_val[0], int):
            # schedule array is 0, 1, 2
            self._schedule = [i%len(TOGGLE_MODE_STR) for i in new_val]
        else:
            raise(Exception('Unknown format of Schedule array'))

    @property
    def auto(self):
        return self._auto

    @auto.setter
    def auto(self, new_val):
        self._auto = bool(int(new_val) and True)

    @property
    def toggle(self):
        return self._toggle

    @toggle.setter
    def toggle(self, new_val):
        if int(new_val) not in VALID_TOGGLE_MODES:
            raise(Exception('AquariumLights: Invalid toggle mode!'))

        self._toggle = int(new_val)

    @property
    def day_hour(self):
        return self._day_hour

    @day_hour.setter
    def day_hour(self, new_val):
        if int(new_val) >= 24:
            raise(Exception('AquariumLights: Invalid day_hour!'))

        self._day_hour = int(new_val)
        self.schedule_range()

    @property
    def night_hour(self):
        return self._night_hour

    @night_hour.setter
    def night_hour(self, new_val):
        if int(new_val) >= 24:
            raise(Exception('AquariumLights: Invalid night_hour!'))

        self._night_hour = int(new_val)
        self.schedule_range()

    @property
    def off_hour(self):
        return self._off_hour

    @off_hour.setter
    def off_hour(self, new_val):
        if int(new_val) >= 24:
            raise(Exception('AquariumLights: Invalid off_hour!'))

        self._off_hour = int(new_val)
        self.schedule_range()

    def schedule_range(self):
    # set up schedule based on day_hour, night_hour, off_hour
        if self._day_hour <= self._night_hour <= self._off_hour:
            self._schedule = [OFF for i in range(0, self._day_hour)] +\
                             [DAY for i in range(self._day_hour, self._night_hour)] +\
                             [NIGHT for i in range(self._night_hour, self._off_hour)] +\
                             [OFF for i in range(self._off_hour, 24)]
        elif self._day_hour <= self._off_hour <= self._night_hour:
            self._schedule = [NIGHT for i in range(0, self._day_hour)] +\
                             [DAY for i in range(self._day_hour, self._off_hour)] +\
                             [OFF for i in range(self._off_hour, self._night_hour)] +\
                             [NIGHT for i in range(self._night_hour, 24)]
        elif self._off_hour <= self._day_hour <= self._night_hour:
            self._schedule = [NIGHT for i in range(0, self._off_hour)] +\
                             [OFF for i in range(self._off_hour, self._day_hour)] +\
                             [DAY for i in range(self._day_hour, self._night_hour)] +\
                             [NIGHT for i in range(self._night_hour, 24)]


    def get_config_state(self):
        return {'auto': self._auto,
                'toggle': TOGGLE_MODE_STR[self._toggle],
                'day_hour': self._day_hour,
                'night_hour': self._night_hour,
                'off_hour': self._off_hour,
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
