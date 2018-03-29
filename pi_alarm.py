#!/usr/bin/python
#--------------------------------------
# Rasperry Pi Alarm
#
# Author : Greg McCarthy
# Date   : 24/03/2018
# Version 1.2
#
#--------------------------------------

import sys
import RPi.GPIO as GPIO
import time
#import urllib2
#import httplib
import logging
from subprocess import *
from time import sleep
from datetime import datetime
import datetime as dtm
from datetime import timedelta

import paho.mqtt.client as mqtt
import time

logger = logging.getLogger("pi-alarm")
hdlr = logging.FileHandler("/var/log/pi-alarm.log")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

BEAM  = 25
PATIO_DOOR = 18
PIR_LOUNGE   = 23       # Normally 0 - when triggered goes O/C. So need Pi internal Pull up
FRONT_DOOR = 24         # Normally 0 - when triggered goes to 5V

def onDisconnect(client, userdata, rc):
        print("disonnected")

def onConnect(self, client, userdata, rc):
        print("connected")

# Main program block

client = mqtt.Client(client_id="alarmcontroller")
client.on_connect = onConnect
client.on_disconnect = onDisconnect
client.connect("openhab2.home", 1883, 60)
client.loop_start()

Lounge_PIR_Triggered_State = False
Lounge_PIR_Normal_State = False

Patio_Door_Open_State = False
Patio_Door_Closed_State = False

FD_Closed_State = False
FD_Open_State = False

Beam_Triggered_State = False
Beam_Normal_State = False



GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers

GPIO.setup(BEAM, GPIO.IN)
GPIO.setup(PATIO_DOOR, GPIO.IN)
GPIO.setup(PIR_LOUNGE, GPIO.IN)
GPIO.setup(FRONT_DOOR, GPIO.IN)

GPIO.setup(BEAM, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PATIO_DOOR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIR_LOUNGE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(FRONT_DOOR, GPIO.IN, pull_up_down=GPIO.PUD_UP)


sleep(5)



  # Main Loop

try:
  logger.info("Starting pi-alarm")
  dt = datetime.now()
  PIR_Time1=dtm.datetime.now()
  BEAM_Time1=dtm.datetime.now()
  FD_Time1=dtm.datetime.now()
  PATIO_Time1=dtm.datetime.now()


  while True:

        # Check if beam triggered
        if (GPIO.input(BEAM) == True):
                if (Beam_Triggered_State == False):     #So we only trigger once
                        logger.info("BEAM Trigger")
                        Beam_Triggered_State = True
                        Beam_Normal_State = False
                        client.publish("garage/beam", "OPEN")
                        BEAM_Time1=dtm.datetime.now()

        # Check if beam normal
        if (GPIO.input(BEAM) == False):
                if (Beam_Normal_State == False):
                        BEAM_Time2=dtm.datetime.now()
                        if ((BEAM_Time2-BEAM_Time1).seconds > 60):        #If triggered only return to normal if 60 secs passed
                                logger.info("BEAM Normal")
                                Beam_Normal_State = True
                                Beam_Triggered_State = False
                                client.publish("garage/beam", "CLOSED")
				
        #======================================================================================================

        # Check if door open
        if (GPIO.input(FRONT_DOOR) == True):
                if (FD_Open_State == False):
                        logger.info("FrontDoor Open")
                        FD_Open_State = True    # So we only send alert once
                        FD_Closed_State = False
                        client.publish("lounge/frontdoor", "OPEN")
                        FD_Time1=dtm.datetime.now()

        # Check if door closed
        if (GPIO.input(FRONT_DOOR) == False):
                if (FD_Closed_State == False):
                        FD_Time2=dtm.datetime.now()
                        if ((FD_Time2-FD_Time1).seconds > 60):        #If triggered only return to normal if 60 secs passed
                                logger.info("FrontDoor Closed")
                                FD_Closed_State = True
                                FD_Open_State = False
                                client.publish("lounge/frontdoor", "CLOSED")

        #======================================================================================================

        #Check if door open
        if (GPIO.input(PATIO_DOOR) == True):
                if (Patio_Door_Open_State == False):
                        logger.info("PatioDoor Open")
                        Patio_Door_Open_State = True
                        Patio_Door_Closed_State = False
                        client.publish("lounge/door", "OPEN")
                        PATIO_Time1=dtm.datetime.now()

        #Check if door closed
        if (GPIO.input(PATIO_DOOR) == False):
                if (Patio_Door_Closed_State == False):
                        PATIO_Time2=dtm.datetime.now()
                        if ((PATIO_Time2-PATIO_Time1).seconds > 60):        #If triggered only return to normal if 60 secs passed
                                logger.info("PatioDoor Closed")
                                Patio_Door_Closed_State = True
                                Patio_Door_Open_State = False
                                client.publish("lounge/door", "CLOSED")

        #======================================================================================================

        #Check if PIR Triggered
        if (GPIO.input(PIR_LOUNGE) == True):
                if (Lounge_PIR_Triggered_State == False):
                        logger.info("Lounge PIR Trigger")
                        Lounge_PIR_Triggered_State = True
                        Lounge_PIR_Normal_State = False
                        client.publish("lounge/pir", "OPEN")

        #Check if PIR Normal
        if (GPIO.input(PIR_LOUNGE) == False):
                if (Lounge_PIR_Normal_State == False):
                        PIR_Time2=dtm.datetime.now()
                        if ((PIR_Time2-PIR_Time1).seconds > 60):        #If triggered only return to normal if 60 secs passed
                                logger.info("Lounge PIR Normal")
                                Lounge_PIR_Normal_State = True
                                Lounge_PIR_Triggered_State = False
                                client.publish("lounge/pir", "CLOSED")


        #======================================================================================================
#
#       #Every 5 mins send a health check
#       #Read output from sensors and send to Domoticz
        if datetime.now() > (dt + timedelta(0,300)):
                logger.info("Updating Health")
                dt = datetime.now()

                GPIO_Val = GPIO.input(FRONT_DOOR)

                if (GPIO_Val ==0):              #If Val is low then value for Domoticz=1, otherwise = 4 (Alarm)
                        client.publish("lounge/frontdoor", "CLOSED")
                else:
                        client.publish("lounge/frontdoor", "OPEN")

                GPIO_Val = GPIO.input(PATIO_DOOR)

                if (GPIO_Val ==0):              #If Val is low then value for Domoticz=1, otherwise = 4 (Alarm)
                        client.publish("lounge/door", "CLOSED")
                else:
                        client.publish("lounge/door", "OPEN")


                GPIO_Val = GPIO.input(PIR_LOUNGE)

                if (GPIO_Val ==0):              #If Val is low then value for Domoticz=1, otherwise = 4 (Alarm)
                        client.publish("lounge/pir", "CLOSED")
                else:
                        client.publish("lounge/pir", "OPEN")

                GPIO_Val = GPIO.input(BEAM)

                if (GPIO_Val ==0):              #If Val is low then value for Domoticz=1, otherwise = 4 (Alarm)
                        client.publish("garage/beam", "CLOSED")
                else:
                        client.publish("garage/beam", "OPEN")

                logger.info("Finished Updating Health")

        sleep(0.1)

except Exception as e:
        logging.exception("message")

#finally:
        GPIO.cleanup()
        logger.info("Exiting")

   
