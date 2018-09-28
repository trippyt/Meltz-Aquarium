import time
import AquariumLights
import logging
from dot3k.menu import MenuOption
logger = logging.getLogger("AquariumLights")

class LightsMenu(MenuOption):
    def __init__(self, aquarium_lights): #Default settings
        self.modes = ['day', 'night', 'off', 'auto', 'toggle']
        self.modes_toggle = AquariumLights.TOGGLE_MODE_STR
        self.mode = 0
        self.running = False
        self.option_time = 0
        self.is_setup = False
        self.lights_control = aquarium_lights
        MenuOption.__init__(self)

    def get_status(self):
        return self._current_status

    def begin(self):
        self.is_setup = False
        self.running = True

    def setup(self, config):
        MenuOption.setup(self, config)
        self.load_options()

    def update_options(self):
        self.set_option('Lights', 'day', str(self.lights_control.day_hour))
        self.set_option('Lights', 'night', str(self.lights_control.night_hour))
        self.set_option('Lights', 'off', str(self.lights_control.off_hour))
        self.set_option('Lights', 'auto', str(self.lights_control.auto))
        self.set_option('Lights', 'toggle', self.modes_toggle[self.lights_control.toggle])


    def load_options(self):
        self.lights_control.day_hour = int(self.get_option('Lights', 'day', str(self.lights_control.day_hour)))
        self.lights_control.night_hour = int(self.get_option('Lights', 'night', str(self.lights_control.night_hour)))
        self.lights_control.off_hour = int(self.get_option('Lights', 'off', str(self.lights_control.off_hour)))
        self.lights_control.auto = self.get_option('Lights', 'auto', str(self.lights_control.auto)) == 'True'
        self.lights_control.toggle = self.modes_toggle.index(self.get_option('Lights', 'toggle', self.modes_toggle[self.lights_control.toggle]))

    def cleanup(self):
        self.running = False
        time.sleep(0.01)
        self.is_setup = False

    def left(self):
        if self.modes[self.mode] == 'auto':
            self.lights_control.auto = not self.lights_control.auto
        elif self.modes[self.mode] == 'toggle':
            self.lights_control.toggle = (self.lights_control.toggle -1) % len(self.modes_toggle)
        elif self.modes[self.mode] == 'day':
            self.lights_control.day_hour = (self.lights_control.day_hour - 1) % 24
        elif self.modes[self.mode] == 'night':
            self.lights_control.night_hour = (self.lights_control.night_hour - 1) % 24
        elif self.modes[self.mode] == 'off':
            self.lights_control.off_hour = (self.lights_control.off_hour - 1) % 24
        else:
            return False
        self.update_options()
        self.option_time = self.millis()
        return True

    def right(self):
        if self.modes[self.mode] == 'auto':
            self.lights_control.auto = not self.lights_control.auto
        elif self.modes[self.mode] == 'toggle':
            self.lights_control.toggle = (self.lights_control.toggle +1) % len(self.modes_toggle)
        elif self.modes[self.mode] == 'day':
            self.lights_control.day_hour = (self.lights_control.day_hour + 1) % 24
        elif self.modes[self.mode] == 'night':
            self.lights_control.night_hour = (self.lights_control.night_hour + 1) % 24
        elif self.modes[self.mode] == 'off':
            self.lights_control.off_hour = (self.lights_control.off_hour + 1) % 24
        self.update_options()
        self.option_time = self.millis()
        return True

    def up(self):
        self.mode = (self.mode - 1) % len(self.modes)
        self.option_time = self.millis()
        return True

    def down(self):
        self.mode = (self.mode + 1) % len(self.modes)
        self.option_time = self.millis()
        return True

    def redraw(self, menu):
        self.update_options()
        if not self.running:
            return False

        if self.millis() - self.option_time > 5000 and self.option_time > 0:
            self.option_time = 0
            self.mode = 0

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

        bottom_row = ''

        if self.modes[self.mode] == 'auto':
            bottom_row = ' Auto ' + chr(5) + ('Y' if self.lights_control.auto else 'N')
        elif self.modes[self.mode] == 'toggle':
            bottom_row = ' Toggle ' + chr(5) + (self.modes_toggle[self.lights_control.toggle])
        elif self.modes[self.mode] == 'day':
            bottom_row = ' Day at ' + chr(5) + str(self.lights_control.day_hour).zfill(2)
        elif self.modes[self.mode] == 'night':
            bottom_row = ' Night at ' + chr(5) + str(self.lights_control.night_hour).zfill(2)
        elif self.modes[self.mode] == 'off':
            bottom_row = ' Off at ' + chr(5) + str(self.lights_control.off_hour).zfill(2)

        menu.write_row(2, chr(4) + bottom_row)