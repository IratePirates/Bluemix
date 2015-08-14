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
			print "Exception - Initialising Messaging -  %s " %(e)

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

if __name__ == "__main__":
	print "Messenger Module for communication with IBM IoT devices"
