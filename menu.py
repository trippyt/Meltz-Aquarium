import sys
import os
import time
import AstralMenu
import webiface
import threading
import logging
import dothat.backlight as backlight
import dothat.lcd as lcd
import dothat.touch as nav
from dot3k.menu import Menu, MenuOption
from time import sleep, time


sys.path.append ('/usr/local/lib/python2.7/dist-packages')
sys.path.append('/home/pi/Pimoroni/displayotron/examples')
sys.path.append('/home/pi/.local/lib/python2.7/site-packages')
sys.path.append('/home/pi/Aquarium/meltz/')

from LightsMenu import LightsMenu
from plugins.clock import Clock
from plugins.graph import IPAddress, GraphTemp, GraphCPU, GraphNetSpeed, GraphSysReboot, GraphSysShutdown
from plugins.text import Text
from MyUtils import Backlight, Contrast

logger = logging.getLogger("AquariumLights")

Bl = Backlight(backlight)

class TimeoutManager():
    def __init__(self):
        self.TIMEOUT = 5
        self.last_button_press = time()

    def button_press(self):
        self.last_button_press = time()
        # turn backlight on
        Bl.update_bl()
        backlight.update()

    def check_timeout(self):
        # check if current time is more than TIMEOUT seconds later than last button press
        if time() - self.last_button_press > self.TIMEOUT:
            # Turn backlight off
            backlight.off()

lights_control = webiface.lights_control
lights_menu = LightsMenu(lights_control)
#Unordered menu
menu = Menu(
    structure={
            'Power Options': {
                'Reboot':GraphSysReboot(),
                'Shutdown':GraphSysShutdown(),
                },
            'Aquarium': {
                'Lighting': {
                    'Control': lights_menu,
                    'Astral Data': AstralMenu.AstralInfo(),
                    }
                },
        'Clock': Clock(backlight),
        'Status': {
            'IP': IPAddress(),
            'CPU': GraphCPU(backlight),
            'Temp': GraphTemp()
        },
        'Settings': {
            'Display': {
                'Contrast': Contrast(lcd),
                'Backlight': Bl
            }
        }
    },
    lcd=lcd,
    input_handler=Text())

tm = TimeoutManager()
nav.bind_defaults(menu)

@nav.on(nav.UP)
def handle_up(pin):
    logger.debug("Up button pressed")
    menu.up()
    tm.button_press()

@nav.on(nav.DOWN)
def handle_down(pin):
    logger.debug("Down button pressed")
    menu.down()
    tm.button_press()

@nav.on(nav.BUTTON)
def handle_button(pin):
    logger.debug("Enter button pressed")
    menu.select()
    tm.button_press()

@nav.on(nav.LEFT)
def handle_left(pin):
    logger.debug("Left button pressed")
    menu.left()
    tm.button_press()

@nav.on(nav.RIGHT)
def handle_right(pin):
    logger.debug("Right button pressed")
    menu.right()
    tm.button_press()

@nav.on(nav.CANCEL)
def handle_cancel(pin):
    logger.debug("Cancel button pressed")
    menu.cancel()
    tm.button_press()

webiface.app.secret_key = os.urandom(12)
webworker = lambda: webiface.app.run(host='0.0.0.0', port=80)
webthread = threading.Thread(target=webworker, daemon=True)
webthread.start()

while True:
    lights_control.check()
    menu.redraw()
    tm.check_timeout()
    sleep(3.0 / 20)
