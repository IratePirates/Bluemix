#!/usr/bin/python2.7
import os
import hermod

from flask import Flask

Server = None

app = Flask(__name__)

def demoStatusCallback(status):
	try:
		if status.action == "Disconnect":
			statusStr = "%s - %s - %s (reason - %s)"
			print(statusStr % (status.time.isoformat(), status.device, status.action, status.reason))
		else:
			print("%s - %s - %s" % (status.time.isoformat(), status.device, status.action))
		
	except Exception as e:
		print "Error in default Status Callback"
		print e

def demoEventCallback(event):
	try:
		#msgStr = "%s event '%s' received from device [%s]: %s"
		#print(msgStr % (event.format, event.event, event.device, json.dumps(event.data)))
		if event.event == "devStat":
			if (Server.evCount < 3 ):
				Server.debugCmd("Establishing Connection")

		elif event.event == "dataFrag":
			if Server.expectingDataFlag:
				print "receiving Fragmented Data Packet %s of %s" % (event.data['pkt'], event.data['maxPkt'])

				if (len(Server.rxData) <= event.data['maxPkt']):
					#store data as tuple with packet number to allow for error checking
					Server.rxData.append((event.data['pkt'], event.data['d'].encode('utf-8')))

					if (len(Server.rxData) == event.data['maxPkt']):
						print"Received All Data"
						Server.dataAvailable = True
						Server.expectingDataFlag = False
				else:
					print "Something's wrong..."
			else:
				print "Not expecting Data"
		Server.evCount = Server.evCount + 1
	except Exception as e:
		print "Error in Event Callback - %s" % (e)

port = os.getenv('VCAP_APP_PORT', '5000')

try:
	print "Starting Server ... "
	Server = hermod.server("./serverFiles/iotServer.cfg")
	#setup Event CallBacks
	Server.registerCallbackMethods(demoEventCallback, demoStatusCallback)
	#set up Status Callbacks 
	print "...Connected"

except Exception as err:
	print "Unexpected Error -  %s" % (err)

@app.route('/')
def hello():
	global Server
	return 'Hello World! I am running on port ' + str(port) + '; evCnt = ' + str(Server.evCount) + '; cmdCnt = ' + str(Server.cmdCount)

@app.route('/data')
def showData():
	try:
		rxData = Server.retrieveDataFromDevice()
		if rxData:
			#extract data from list
			result = [x[1] for x in sorted(rxData, key=lambda tup: tup[0])]

			#Do any Data Processing in here!!

			#Flatten list
			return ''.join(result)
		else:
			return "No data Received from device"
	except Exception as e:
		print "Error Showing data - %s" % (e)

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))