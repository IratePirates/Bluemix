import datetime
import json
import select, sys

import threading

from sharedLibs import hermod #Messenger Module -  the good messenger gods were already taken...

cmdCount = 0
interval = 20
transmitData = False
messenger = None

def demoCommandCallback(cmd):
	try:
		global cmdCount, interval
		global transmitData

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
		elif cmd.command == "transmitData":
			transmitData = True
		else:
			print "Command received: cmd -'%s' ; body -'%s'" %(cmd.command, json.dump(cmd.data))
			print "Invalid Command"
		cmdCount = cmdCount + 1
	except Exception as err:
		print "Command Callback Err - %s " %(err)

def publish_status_on_interval():
	try:
		if messenger:
			t = threading.Timer(interval, publish_status_on_interval)
			t.start()
			messenger.publishEvent(myData=str(datetime.datetime.utcnow()), msgType="devStat")
		else:
			print"No Messenger Attached."
	except Exception as err:
		print "Error Scheduling Status update - %s " %(err)

try:
	print "Configure Device Messenger"
	messenger = hermod.device("./clientFiles/device.cfg")
	messenger.registerCmdCallback(demoCommandCallback)

	print "Begin to Send Data..."
	publish_status_on_interval()

	print "I'm doing stuff. Press Enter to stop me!"

	while True:
		try:
			#os.system('cls' if os.name == 'nt' else 'clear')
			if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
				line = raw_input()
				print "Pausing transmissions"
				#Do command line control Stuff in here...
				break
			else:
				if transmitData:
					messenger.fileSend("./clientFiles/Sample.txt")
					transmitData = False
		except Exception as err:
			print "failing to run"
			print err

	messenger.disconnect()
except Exception as e:
	print "Exception - %s " %(e)
finally:
	messenger.disconnect()
	messenger = None
	print "Enter pressed- exiting"
