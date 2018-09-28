import sys
import time
import logging
sys.path.append ('/usr/local/lib/python2.7/dist-packages')
sys.path.append('/home/pi/.local/lib/python2.7/site-packages')
from dot3k.menu import Menu, MenuOption
from astral import Astral
import datetime

a = Astral()
a.solar_depression = 'civil'
city = a['London']
logger = logging.getLogger("AquariumLights")
class AstralInfo(MenuOption):
    def __init__(self):
        self._sun_rise = None
        self._sun_set = None
        MenuOption.__init__(self)

    def begin( self ):
        self.set_times()

    def set_times(self):
        now = datetime.datetime.now()
        sun = city.sun(date=now.date(), local=True)
        self._sun_rise = sun['sunrise'].time()
        self._sun_set = sun['sunset'].time()
        dateSTR = datetime.datetime.now().strftime("%H:%M:%S" )
        logger.debug('SunRise at:{}'.format(str(self._sun_rise)))
        logger.debug('SunSet at:{}'.format(str(self._sun_set)))

    def redraw(self, menu):
        menu.write_row(0, "Lights {}".format(str(datetime.datetime.now().time())[:8]))
        menu.write_row(1, "R:{}".format(str(self._sun_rise)))
        menu.write_row(2, "S:{}".format(str(self._sun_set)))
        

        

    
