# Water Level Sensor
import time
import sys
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_DOWN))