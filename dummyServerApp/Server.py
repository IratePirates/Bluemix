import os, json
import ibmiotf.application
from flask import Flask

client = None
msgCount = 0

app = Flask(__name__)

port = os.getenv('VCAP_APP_PORT', '5000')

def myEventCallback(event):
	try:
		global msgCount
		msgStr = "%s event '%s' received from device [%s]: %s"
		print(msgStr % (event.format, event.event, event.device, json.dumps(event.data)))
		msgCount = msgCount+ 1 
	except Exception as e:
		print "Error in Event Callback"
		print e

try:
	print "Configuring IoT..."
	configFilePath ="./iotServer.cfg"
	options = ibmiotf.application.ParseConfigFile(configFilePath)
	client = ibmiotf.application.Client(options)
	print "...Configured"
	
	client.connect()
	client.deviceEventCallback = myEventCallback
	client.subscribeToDeviceEvents(event="mayflyTime")
	print "...Connected"
	
except ibmiotf.ConnectionException  as e:
	print "Error on grabbing IoT Configuration %s" % (e)

@app.route('/')
def hello():
	return 'Hello World! I am running on port ' + str(port) + '; msgCount = ' + str(msgCount) + ';'

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))