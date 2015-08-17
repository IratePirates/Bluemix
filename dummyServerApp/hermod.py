# IBM Internet of Things Communiucation Module for Device
#        -  the good messenger gods were already taken...
# Author- Steve B
#!/usr/bin/python2.7

import ibmiotf.application
import ibmiotf.device
import os

class device:
	def __init__(self, cfgFile="/home/pi/dummySensor/device.cfg"):
		self.client = None
		self.evCount = 0

		try:
			print ("Parsing Config")
			options = ibmiotf.device.ParseConfigFile(cfgFile)
			self.client = ibmiotf.device.Client(options)
		except Exception as e:
			print "Exception - Initialising Device Messaging -  %s " %(e)

	def defaultCommandCallback(self, cmd):
		try:
			print "Received command %s" % (cmd.command)
		except Exception as e:
			print "Exception - defaultCommandCallback Messaging %s " %(e)

	def registerCmdCallback(self, myCommandCallback="defaultCommandCallback"):
		try:
			self.client.connect()
			self.client.commandCallback = myCommandCallback
		except Exception as e:
			print "Exception - binding cmdCallback -  %s " %(e)

	def publishEvent(self, myData, msgType="devStat", encoding="json", QoS=0):
		try:
			if self.client :
				self.client.publishEvent(msgType, encoding, myData, QoS)
				print "Publishing evCount: %d ;" %(self.evCount)
				self.evCount = self.evCount + 1
			else:
				print "Cannot Publish Event, no Client exists yet"
		except Exception as e:
			print "Exception - Publishing Event -  %s " %(e)

	def disconnect(self):
		try:
			self.client.disconnect()
		except Exception as e:
			print "Exception - Disconnecting -  %s " %(e)

	def sendFragDataEvent(self, fileHandle, totalChunks, bufferSize = 2048):
		dataSrc=[]
		try:
			#open text file
			for chunk in range(0 , totalChunks) :
				dataSrc.append(fileHandle.read(bufferSize))

			#Send Fragments
			for i in range(0 , totalChunks) :
				pktNum =i+1

				myData = {'pkt' : pktNum, 'maxPkt' : totalChunks, 'd':dataSrc[i]}
				self.publishEvent( myData, msgType="dataFrag", encoding="json", QoS=2)

			print "Publishing Data Fragmented as %i packets " % (totalChunks)
			return True
		except Exception as err:
			print "Data Send Err - %s " %(err)

	def fileSend(self, filePath, bufferSize = 2048):
		try:
			print "Opening File Location... "
			fileSize = os.path.getsize(filePath)
			totalChunks = (fileSize / bufferSize) + (fileSize % bufferSize > 0) # Hacky Ceiling Function
			print "Opening File- %s ; size %d; \n   bufferSize %d ; chunks required - %d ;" %( filePath, fileSize, bufferSize, totalChunks)
			sampleFile = open(filePath, 'r', bufferSize)
			print "Data collected"
			self.sendFragDataEvent(sampleFile, totalChunks, bufferSize)
			sampleFile.close()
			return True
		except Exception as err:
			print "fileSend Err - %s " %(err)

class server:
	def __init__ (self, configFilePath="./iotServer.cfg"):
		self.server = None
		self.evCount = 0
		self.cmdCount = 0
		self.expectingDataFlag = False
		self.dataAvailable = False
		self.rxData= [] #store for received data

		try:
			print "Configuring IoT..."

			options = ibmiotf.application.ParseConfigFile(configFilePath)
			self.server = ibmiotf.application.Client(options)
		except ibmiotf.ConnectionException  as e:
			print "Error on grabbing IoT Configuration - %s" % (e)
		except Exception as e:
			print "Exception - Initialising Server Messaging -  %s " %(e)

	def sendCmd(self, command, payload ="",deviceId = 'b827ebddb7d1', device="raspberrypi" ):
	#TODO - CLEAN ME up for general useage
		try:
			#Do all the jazz for managing multiple devices in here
			self.server.publishCommand(device, deviceId, str(command), "json", payload)
			print "Sending '%s' cmd, payload '%s' to device %s" % (command, payload, deviceId)
			self.cmdCount = self.cmdCount + 1
		except Exception as e:
			print "Error in Cmd Callback"
			print e

	def debugCmd(self, message):
			payload = {'message' : message}
			self.sendCmd("print", payload)

	def registerCallbackMethods(self, myEventCallback, myStatusCallback):
		try:
			self.server.connect()
			self.server.deviceEventCallback = myEventCallback
			self.server.deviceStatusCallback = myStatusCallback #why does this not work
			self.server.subscribeToDeviceStatus()
			self.server.subscribeToDeviceEvents()

		except Exception as e:
			print "Error in Registering Status Callback"
			print e

	def sendDataPushCmd(self, deviceId = 'b827ebddb7d1', device="raspberrypi"):
		try:
			#clear list of data
			while len(self.rxData) > 0 : self.rxData.pop()

			self.expectingDataFlag = True

			self.sendCmd(command="transmitData", payload ="",deviceId = 'b827ebddb7d1', device="raspberrypi" )
		except Exception as e:
			print "Error while sending request for Data - %s" %e

	def retrieveDataFromDevice(self):
		try:
			if  self.dataAvailable and not self.expectingDataFlag:
				print "Data Available - Printing"
				self.dataAvailable = False
				return self.rxData
			else:
				print "No Data Available - Contacting device"
				self.sendDataPushCmd(deviceId = 'b827ebddb7d1', device="raspberrypi")

				rxDataTmp = []

				if not self.expectingDataFlag:
					#Or hack, and require the page is reloaded.
					rxDataTmp = self.retrieveDataFromDevice()

				if rxDataTmp:
					self.dataAvailable = False
					return rxDataTmp
				else:
					return 0
		except Exception as e:
			print "Error while Retrieving Data - %s" %e

if __name__ == "__main__":
	print "Messenger Module for communication with IBM IoT devices"
