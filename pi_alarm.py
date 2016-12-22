#!/usr/bin/python
#--------------------------------------
# Rasperry Pi Alarm
#
# Author : Greg McCarthy
# Date   : 14/12/2016
#
#--------------------------------------

#import
import sys
import RPi.GPIO as GPIO
import time
import urllib2
import logging
from subprocess import *
from time import sleep
from datetime import datetime
import datetime as dtm
from datetime import timedelta

def url_get(url):     
        try:
		logger.info(url)                  
                urllib2.urlopen(url)                
        except urllib2.HTTPError as err:
		logger.info("Error - exception")
                logger.info(err.code)
	except Exception:
    		import traceback
    		logger.error('generic exception: ' + traceback.format_exc())

logger = logging.getLogger("pi-alarm")
hdlr = logging.FileHandler("/var/log/pi-alarm.log")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

BEAM  = 25
PATIO_DOOR = 18
PIR_LOUNGE   = 23	# Normally 0 - when triggered goes O/C. So need Pi internal Pull up 	
FRONT_DOOR = 24		# Normally 0 - when triggered goes to 5V

Alarm = ""

GREEN_LED = 0b00000001
RED_LED = 0b00000010


# Main program block

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
		if (Beam_Triggered_State == False):	#So we only trigger once
			logger.info("BEAM Trigger")
			Beam_Triggered_State = True
			url  = "http://controller.home:8080/json.htm?type=command&param=udevice&idx=26&nvalue=4"
			url_get(url)
			BEAM_Time1=dtm.datetime.now()

	# Check if beam normal
	if (GPIO.input(BEAM) == False):
                if (Beam_Normal_State == False):
                        BEAM_Time2=dtm.datetime.now()
                        if ((BEAM_Time2-BEAM_Time1).seconds > 60):        #If triggered only return to normal if 60 secs passed
	                        logger.info("BEAM Normal")
        	                Beam_Normal_State = True
                	        url  = "http://controller.home:8080/json.htm?type=command&param=udevice&idx=26&nvalue=1"
                        	url_get(url)
			
	#======================================================================================================
	
	# Check if door open
	if (GPIO.input(FRONT_DOOR) == True):
		if (FD_Open_State == False):
                        logger.info("FrontDoor Open")
                        FD_Open_State = True	# So we only send alert once
                        url  = "http://controller.home:8080/json.htm?type=command&param=udevice&idx=19&nvalue=4"
                        url_get(url)
			FD_Time1=dtm.datetime.now()

	# Check if door closed
	if (GPIO.input(FRONT_DOOR) == False):
                if (FD_Closed_State == False):
                        FD_Time2=dtm.datetime.now()
                        if ((FD_Time2-FD_Time1).seconds > 60):        #If triggered only return to normal if 60 secs passed
	                        logger.info("FrontDoor Closed")
        	                FD_Closed_State = True
                	        url  = "http://controller.home:8080/json.htm?type=command&param=udevice&idx=19&nvalue=1"
                        	url_get(url)
        
	#======================================================================================================
	
	#Check if door open
	if (GPIO.input(PATIO_DOOR) == True):
                if (Patio_Door_Open_State == False):
                        logger.info("PatioDoor Open")
                        Patio_Door_Open_State = True
                        url  = "http://controller.home:8080/json.htm?type=command&param=udevice&idx=20&nvalue=4"
                        url_get(url)
			PATIO_Time1=dtm.datetime.now()

	#Check if door closed
	if (GPIO.input(PATIO_DOOR) == False):
		if (Patio_Door_Closed_State == False):
                        PATIO_Time2=dtm.datetime.now()
                        if ((PATIO_Time2-PATIO_Time1).seconds > 60):        #If triggered only return to normal if 60 secs passed
 				logger.info("PatioDoor Closed")
                	        Patio_Door_Closed_State = True
                        	url  = "http://controller.home:8080/json.htm?type=command&param=udevice&idx=20&nvalue=1"
                        	url_get(url)

	#======================================================================================================
		
	#Check if PIR Triggered
	if (GPIO.input(PIR_LOUNGE) == True):
                if (Lounge_PIR_Triggered_State == False):
                        logger.info("Lounge PIR Trigger")
                        Lounge_PIR_Triggered_State = True
			Lounge_PIR_Normal_State = False
                        url  = "http://controller.home:8080/json.htm?type=command&param=udevice&idx=25&nvalue=4"
       			url_get(url)
			PIR_Time1=dtm.datetime.now()

	#Check if PIR Normal
        if (GPIO.input(PIR_LOUNGE) == False):
                if (Lounge_PIR_Normal_State == False):
			PIR_Time2=dtm.datetime.now()
			if ((PIR_Time2-PIR_Time1).seconds > 60):	#If triggered only return to normal if 60 secs passed
	                        logger.info("Lounge PIR Normal")
        	                Lounge_PIR_Normal_State = True
                		Lounge_PIR_Triggered_State = False
			        url  = "http://controller.home:8080/json.htm?type=command&param=udevice&idx=25&nvalue=1"
                        	url_get(url)



	#======================================================================================================
	
	#Every 5 mins send a health check
	#Read output from sensors and send to Domoticz
	if datetime.now() > (dt + timedelta(0,300)):
		logger.info("Updating Health")
	        dt = datetime.now()

		GPIO_Val = GPIO.input(FRONT_DOOR)

		if (GPIO_Val ==0):		#If Val is low then value for Domoticz=1, otherwise = 4 (Alarm)
			GPIO_Val = 1
		else:
			GPIO_Val = 4

		url = "http://controller.home:8080/json.htm?type=command&param=udevice&idx=19&nvalue={}".format( GPIO_Val )
        	url_get(url)

		GPIO_Val = GPIO.input(PATIO_DOOR)
   
                if (GPIO_Val ==0):              #If Val is low then value for Domoticz=1, otherwise = 4 (Alarm)
                        GPIO_Val = 1
                else:
                        GPIO_Val = 4

                url = "http://controller.home:8080/json.htm?type=command&param=udevice&idx=20&nvalue={}".format( GPIO_Val )
                url_get(url)

	 	GPIO_Val = GPIO.input(PIR_LOUNGE)
   
                if (GPIO_Val ==0):              #If Val is low then value for Domoticz=1, otherwise = 4 (Alarm)
                        GPIO_Val = 1
                else:
                        GPIO_Val = 4     

                url = "http://controller.home:8080/json.htm?type=command&param=udevice&idx=25&nvalue={}".format( GPIO_Val )
                url_get(url)

 		GPIO_Val = GPIO.input(BEAM)

                if (GPIO_Val ==0):              #If Val is low then value for Domoticz=1, otherwise = 4 (Alarm)
                        GPIO_Val = 1
                else:
                        GPIO_Val = 4     

		url = "http://controller.home:8080/json.htm?type=command&param=udevice&idx=26&nvalue={}".format( GPIO_Val )
                url_get(url)
		logger.info("Finished Updating Health")

	sleep(0.1)

except Exception as e:
    	logging.exception("message")

#finally:
	GPIO.cleanup()
	logger.info("Exiting") 


def switch_triggered(MySwitch):
	if (MySwitch & 0b00000001) != 0:
		Alarm = "Door 1"
		urllib2.urlopen("http://controller.home:8080/json.htm?type=command&param=udevice&idx=19&nvalue=4").read()       #Door 1
		DOOR1 = True
	if (MySwitch & 0b00000010) != 0:
                Alarm = Alarm + "Door 2"
		urllib2.urlopen("http://controller.home:8080/json.htm?type=command&param=udevice&idx=20&nvalue=4").read()       #Door 2
		DOOR2 = True
	if (MySwitch & 0b00000100) != 0:
                Alarm = Alarm + "Door 3"
		urllib2.urlopen("http://controller.home:8080/json.htm?type=command&param=udevice&idx=21&nvalue=4").read()       #Door 3
		DOOR3= True
	if (MySwitch & 0b00001000) != 0:
                Alarm = Alarm + "Garage Door 1"
                urllib2.urlopen("http://controller.home:8080/json.htm?type=command&param=udevice&idx=22&nvalue=4").read()       #Garage Door 1 
		GARAGE_DOOR1 = True
       	if (MySwitch & 0b00010000) != 0:
                Alarm = Alarm + "Garage Door 2"
                urllib2.urlopen("http://controller.home:8080/json.htm?type=command&param=udevice&idx=23&nvalue=4").read()       #Garage Door 2  
		GARAGE_DOOR2 = True
       	if (MySwitch & 0b00100000) != 0:
                Alarm = Alarm + "Garage Door 3"
                urllib2.urlopen("http://controller.home:8080/json.htm?type=command&param=udevice&idx=24&nvalue=4").read()       #Garage Door 3  
		GARAGE_DOOR3 = True
       	if (MySwitch & 0b01000000) != 0:
                Alarm = Alarm + "PIR 1"
                urllib2.urlopen("http://controller.home:8080/json.htm?type=command&param=udevice&idx=25&nvalue=4").read()       #PIR 1  
		PIR1 = True
       	if (MySwitch & 0b10000000) != 0:
                Alarm = Alarm + "PIR 1"
                urllib2.urlopen("http://controller.home:8080/json.htm?type=command&param=udevice&idx=26&nvalue=4").read()       #PIR 2  
		PIR2 = True





