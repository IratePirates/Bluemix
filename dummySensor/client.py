import time
import json
import os
import ibmiotf.device
from datetime import datetime

client = None
interval = 10
cmdCount = 0
evCount = 0
transmitData = False

def sendStatusEvent(client):
	global evCount

	myQoSLevel=2
	myData = str(datetime.now())
	client.publishEvent("mayflyTime", "json", myData, myQoSLevel)
	print "Publishing evCount: %d ; cmdCount: %d" %(evCount, cmdCount)
	evCount = evCount + 1

def sendPacketFragged(client, path="/home/pi/dummySensor/Sample.txt", bufferSize = 2048):
	global evCount
	global transmitData

	try:
		if transmitData:
			#open text file
			fileSize = os.path.getsize(path)
			totalChunks = (fileSize / bufferSize) + (fileSize % bufferSize > 0) # Hacky Ceiling Function
			print "Opening File- %s ; size %s; \n   bufferSize %s ; chunks required - %s ;" %(path, str(fileSize), str(bufferSize), str(totalChunks))
			sampleFile = open(path, 'r', bufferSize)
			dataSrc=[]
			print "Starting Data collection"
			for chunk in range(0 , totalChunks) :
				dataSrc.append(sampleFile.read(bufferSize))
			print "Data collected"
			print dataSrc[0]
			print dataSrc[totalChunks-1]

			#Send Fragments
			myQoSLevel=2
			for i in range(0 , totalChunks) :
				pktNum =i+1

				myData = {	'pkt' : pktNum, 'totpkt' : totalChunks, \
							'payload':dataSrc[i]}
				client.publishEvent("DataFrag", "json", myData, myQoSLevel)

				print "Publishing Data Fragmented as Event pkt %i of %i, evCount: %d ; cmdCount: %d" \
					%(pktNum, totalChunks, evCount, cmdCount)

				evCount = evCount + 1
				transmitData = False
		else:
			print "Called without data to send?"
	except Exception as err:
		print "Data Send Err - %s " %(err)

def myCommandCallback(cmd):
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
	print ("Parsing Config")
	options = ibmiotf.device.ParseConfigFile("/home/pi/dummySensor/device.cfg")
	client = ibmiotf.device.Client(options)
	client.connect()
	client.commandCallback = myCommandCallback

	print "Begin to Send Data..."
	while True:
		try:
			if transmitData:
				sendPacketFragged(client)
			else:
				# Additional flow control can be added with a raw_input string
				# example: http://stackoverflow.com/questions/7255463/exit-while-loop-by-user-hitting-enter-key
					# N.B. would require second thread for message control e.g. : http://pymotw.com/2/multiprocessing/basics.html
				time.sleep(interval)
				sendStatusEvent(client)
				# Max length of MQTT message is 4kB, currently. This will include MQTT headers(Topic, etc), IoT headers + Timestamp.
					#topic = 'iot-2/evt/'+event+'/fmt/' + msgFormat
					#MQTT payload = JSON encoded (data + datetime.now(pytz.timezone('UTC')))
				#therefore send 2kB chunks + assume success.
		except Exception as err:
			print "failing to run"
			print err

	client.disconnect()
except Exception as e:
	print "Exception - %s " %(e)
