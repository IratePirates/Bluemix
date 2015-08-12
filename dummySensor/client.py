import time
import json
import ibmiotf.device
from datetime import datetime
import uuid

client = None
interval = 5
cmdCount = 0
evCount = 0

def myCommandCallback(cmd):
	try:
		global cmdCount, interval
		
		if cmd.command == "setInterval":
			if 'interval' not in cmd.data:
				print("Error - command is missing require parameter: 'interval'")
			else:
				 interval = cmd.data['interval']
		elif cmd.command == "print":
			if 'message' not in cmd.data:
				print("Debug Message missing field: 'message'")
			else:
				print "Command received-  '%s' " %(cmd.data['message'])
		else:
			print "Command received: cmd -'%s' ; body -'%s'" %(cmd.command, json.dump(cmd.data))
			print "Invalid Command"
		cmdCount = cmdCount + 1
	except Exception as err:
		print "Command Callback Err - %s " %(err)

try:
	print ("Parsing Config")
	options = ibmiotf.device.ParseConfigFile("/home/pi/dummySensor/device.cfg")
	client = ibmiotf.device.Client(options)
	client.connect()
	client.commandCallback = myCommandCallback

	print "Begin to Send Data..."
	while True:
		try:
			time.sleep(interval)
			myQoSLevel=2
			myData = str(datetime.now())
			client.publishEvent("mayflyTime", "json", myData, myQoSLevel)
			print "Publishing evCount: %d ; cmdCount: %d" %(evCount, cmdCount)
			evCount = evCount + 1
		except Exception as err:
			print "failing to run"
			print err
	
	client.disconnect()
except Exception as e:
	print "Exception - %s " %(e)
