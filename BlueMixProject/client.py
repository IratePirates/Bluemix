import time
import json
from sharedLibs import hermod #Messenger Module -  the good messenger gods were already taken...

cmdCount = 0
interval = 20
transmitData = False

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

try:
	print "Configure Device Messenger"
	messenger = hermod.device("./deviceFiles/device.cfg")
	messenger.registerCmdCallback(demoCommandCallback)
	print "Begin to Send Data..."
	while True:

		try:
			if transmitData:
				messenger.fileSend("./deviceFiles/Sample.txt")
				transmitData = False
			else:
				# Additional flow control can be added with a raw_input string
				# example: http://stackoverflow.com/questions/7255463/exit-while-loop-by-user-hitting-enter-key
					# N.B. would require second thread for message control e.g. : http://pymotw.com/2/multiprocessing/basics.html

				messenger.publishEvent(myData=time.sleep(interval), msgType="devStat")
				# Max length of MQTT message is 4kB, currently. This will include MQTT headers(Topic, etc), IoT headers + Timestamp.
					#topic = 'iot-2/evt/'+event+'/fmt/' + msgFormat
					#MQTT payload = JSON encoded (data + datetime.now(pytz.timezone('UTC')))
				#therefore send 2kB chunks + assume success.
		except Exception as err:
			print "failing to run"
			print err

	messenger.disconnect()
except Exception as e:
	print "Exception - %s " %(e)
