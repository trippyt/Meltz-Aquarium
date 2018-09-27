import time
import AquariumLights
from dot3k.menu import MenuOption
 
class LightsMenu(MenuOption):
    def __init__(self, aquarium_lights): #Default settings
        self.running = False
        self.is_setup = False
        self.lights_control = aquarium_lights
        self.curr_idx = 0
        self.curr_val = self.lights_control._schedule[ self.curr_idx ]
        MenuOption.__init__(self)
 
    def begin(self):
        self.is_setup = False
        self.running = True
 
    def setup(self, config):
        MenuOption.setup(self, config)
        self.curr_idx = 0
        self.curr_val = self.lights_control._schedule[ self.curr_idx ]
       
    def cleanup(self):
        self.running = False
        time.sleep(0.01)
        self.is_setup = False
 
    def left(self):
        val = (self.curr_val - 1) % len(AquariumLights.VALID_TOGGLE_MODES)
        sch = self.lights_control._schedule
        sch[ self.curr_idx ] = val
        self.lights_control.schedule = sch
        return True
       
    def right(self):
        val = (self.curr_val + 1) % len(AquariumLights.VALID_TOGGLE_MODES)
        sch = self.lights_control._schedule
        sch[ self.curr_idx ] = val
        self.lights_control.schedule = sch
        return True
       
 
    def up(self):
        self.curr_idx = (self.curr_idx - 1) % len(self.lights_control._schedule)
        self.curr_val = self.lights_control._schedule[ self.curr_idx ]
        return True
 
    def down(self):
        self.curr_idx = (self.curr_idx + 1) % len(self.lights_control._schedule)
        self.curr_val = self.lights_control._schedule[ self.curr_idx ]
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
 
        self.curr_val = self.lights_control._schedule[ self.curr_idx ]
 
        bottom_row = ''

        mode_str = AquariumLights.TOGGLE_MODE_STR[ self.curr_val ].upper()
        bottom_row = '{:02}:00 \x05Mode:{}'.format(self.curr_idx, mode_str)
 
        menu.write_row(2, chr(4) + bottom_row)
