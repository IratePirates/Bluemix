#!/usr/bin/python2.7
import os
import ibmiotf.application
#import ibmiotf.device
from flask import Flask

client = None
options = None
evCount = 0
cmdCount = 0

#flags to control
expectingDataFlag = False
rxData= []

app = Flask(__name__)

deviceId = os.getenv("DEVICE_ID")
port = os.getenv('VCAP_APP_PORT', '5000')

def myStatusCallback(status):
	try:
		global evCount, cmdCount
		if status.action == "Disconnect":
			statusStr = "%s - %s - %s (reason - %s)"
			print(statusStr % (status.time.isoformat(), status.device, status.action, status.reason))
		else:
			print("%s - %s - %s" % (status.time.isoformat(), status.device, status.action))
		
		#zero debug counters
		evCount = 0
		cmdCount = 0

	except Exception as e:
		print "Error in Status Callback"
		print e

def sendCmd(command, payload ="", device="raspberrypi" ):
	#TODO - CLEAN ME up for general useage
	try:
		global cmdCount
		deviceId = 'b827ebddb7d1'
		#Do all the jazz for managing multiple devices in here
		client.publishCommand(device, deviceId, str(command), "json", payload)
		print "Sending '%s' cmd, payload '%s' to device %s" % (command, payload, deviceId)
		cmdCount = cmdCount + 1
	except Exception as e:
		print "Error in Cmd Callback"
		print e

def debugCmd(message):
			payload = {'message' : message}
			sendCmd("print", payload)


def myEventCallback(event):
	global evCount
	global rxData, expectingDataFlag

	try:
		#msgStr = "%s event '%s' received from device [%s]: %s"
		#print(msgStr % (event.format, event.event, event.device, json.dumps(event.data)))
		if event.event == "devStat":
			if (evCount < 3 ):
				debugCmd("Establishing Connection")

		elif event.event == "dataFrag":
			if expectingDataFlag:
				print "receiving Fragmented Data Packet %s of %s" % (event.data['pkt'], event.data['maxPkt'])

				if (len(rxData) <= event.data['maxPkt']):
					#store data as tuple with packet number to allow for error checking
					rxData.append((event.data['pkt'], event.data['d'].encode('utf-8')))

					if (len(rxData) == event.data['maxPkt']):
						"Received All Data"
						expectingDataFlag = False
				else:
					print "Something's wrong..."
			else:
				print "Not expecting Data"
		evCount = evCount + 1
	except Exception as e:
		print "Error in Event Callback"
		print e

try:
	print "Configuring IoT..."
	configFilePath ="./iotServer.cfg"
	options = ibmiotf.application.ParseConfigFile(configFilePath)
	client = ibmiotf.application.Client(options)

	#setup Event CallBacks
	client.connect()
	client.deviceEventCallback = myEventCallback
	client.subscribeToDeviceEvents()

	#set up Status Callbacks 
	client.deviceStatusCallback = myStatusCallback
	client.subscribeToDeviceStatus()
	print "...Connected"

except ibmiotf.ConnectionException  as e:
	print "Error on grabbing IoT Configuration - %s" % (e)
except Exception as err:
	print "Unexpected Error -  %s" % (e)

@app.route('/')
def hello():
	return 'Hello World! I am running on port ' + str(port) + '; evCnt = ' + str(evCount) + '; cmdCnt = ' + str(cmdCount)

@app.route('/getdata')
def sendDataCommand():
	global expectingDataFlag, dataAvailFlag, rxData

	#clear list of data
	while len(rxData) > 0 : rxData.pop()

	expectingDataFlag = True

	sendCmd("transmitData")

	return "No data Received from device"

@app.route('/showdata')
def showData():
	global rxData
	try:
		print rxData
		if len(rxData):
			#extract data from list
			result = [x[1] for x in sorted(rxData, key=lambda tup: tup[0])]

			#Do Any Error Correction in here...?

			#Flatten list
			return ''.join(result)
		else:
			return "No data Received from device"
	except Exception as e:
		print "Error Showing data - %s" % (e)

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))