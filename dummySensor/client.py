import time
import os, json
import ibmiotf.application
from datetime import datetime

client = None

#def myCommandCallback(cmd):
#	if cmd.event == "light":
#		print command

try:
	print ("Parsing Config")
	options = ibmiotf.application.ParseConfigFile("/home/pi/dummySensor/device.cfg")
	print "...parsed"
	options["deviceId"] = options["id"]
	options["id"] = "aaa" + options["id"]
	client = ibmiotf.application.Client(options)
	client.connect()
	print ("Connected...")
#	client.deviceEventCallback = myCommandCallback
#	client.subscribeToDeviceEvents(event="light")

	print "Begin to Send Data..."
	
	while True:
		time.sleep(20)
		myData = str(datetime.now())
		print "Publishing mayflyTime %s" %(myData)
		client.publishEvent("raspberrypi", options["deviceId"], "mayflyTime", "json", myData)
		print "Loop Fnished"
except ibmiotf.ConnectException as e:
	print e
