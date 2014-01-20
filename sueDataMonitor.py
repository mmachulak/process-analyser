##server.py
import glob
import hashlib
import os
import pickle
import socket
import SocketServer
import sys
import threading
import time

class ProcessReceivedData(SocketServer.BaseRequestHandler):

	def forwardSensorValue(self,sensorIP,sensorValue):
		monitoringDevice = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    		monitoringDevice.connect(("localhost", 37568))
		monitoringDevice.send("SensorValue"+","+sensorIP+","+sensorValue) # SensorValue (the first) indicates the data type to the MD
		return

	def forwardMetricValue(self,metricName,securityLevel):
		monitoringDevice = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    		monitoringDevice.connect(("localhost", 37568))
		monitoringDevice.send("MetricValue"+","+securityLevel) # SensorValue (the first) indicates the data type to the MD
		return

    	def handle(self):
		# Echo the back to the client
		receivedData = self.request.recv(1024)
		#cur_thread = threading.currentThread()
		#response = '%s: %s' % (cur_thread.getName(), data)
		self.request.send("Received: "+receivedData)
		listReceivedData = receivedData.split(",")
		print "Received:", listReceivedData
		
		if listReceivedData[0] == "Kill Monitor":
			print "Data monitor has been killed by the sensor simulator.  No more sensor values."
			print "Number of value in dataset:", len(receivedDataset)
			sys.exit()
		elif listReceivedData[0] == "runRogueChangesMetricCheck":
			configDirectory = checkIntegrity("/home/x/systemConfig/")
			integrityCheckThread = threading.Thread(target=configDirectory.runOnce).start()
		elif listReceivedData[0] == "runReachabilityCountMetricCheck":
			pass
		elif listReceivedData[0] == "sensorValue":
			print("Received Sensor Value: "+listReceivedData[1])
			print("Forwarding from PLC to monitoring device ...")
			print self.client_address
			self.forwardSensorValue(self.client_address[0],listReceivedData[1])
		return

class ThreadedDataMonitorServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    	pass

class checkIntegrity(object):
	def __init__(self, directoryToMonitor):
		self.directoryToMonitor = directoryToMonitor
		self.currentHashes = {}
		self.pickledKnownGoodValues = open('knownGoodHashes.pkl', 'rb')
		self.knownGoodValues = pickle.load(self.pickledKnownGoodValues)

	def createFiles(self):
		"""Used for testing purposes - automatically recreates 100 files with "known good" values"""
		for i in range(1,101):
			#print directoryToCreate
			file = open(self.directoryToMonitor+str(i), 'w')
			file.write('This is a file for integrity checking')
			file.close()

	def gatherCurrentHashes(self):
		"""This function collects the file names of every file in the monitored directory, and then
		checks its md5sum.  The digest is then stored in a dictionary (key=filename, value=md5sum,
		which is returned by the function."""
		checkIntegrityFiles = os.listdir(self.directoryToMonitor) # Retrieves list of files in monitoring directory.
		for filePath in checkIntegrityFiles:
			fullFilePath = self.directoryToMonitor+filePath
			openedFile = open(fullFilePath, 'rb')
			fileHash = hashlib.md5()
			while True: # Update the digest in chunks.  Often more efficient than loading an entire file into memory.
				dataOfFile = openedFile.read(8192)
				if not dataOfFile:
					break
				fileHash.update(dataOfFile)
			#print "File:", fullFilePath
			md5fileDigest = fileHash.hexdigest()
			#print "MD5:", md5fileDigest # Returns digest of data fed into the update() method so far (using only hex digits).
			self.currentHashes[fullFilePath]=md5fileDigest
		return

	def checkHashes(self):
		"""The function compares the current hashes to the known good hashes, and calculates the security
		level, based upon the mechanism outlined the dissertation."""
		self.gatherCurrentHashes()
		securityLevel = 0
		unauthorisedModification = 0
		for key in self.currentHashes:
			if self.currentHashes[key] != self.knownGoodValues[key]:
				unauthorisedModification += 1
		securityLevel = 100-unauthorisedModification # Using the initial security levels example for testing purposes.
		return securityLevel

	def passSecurityLevelToDataMonitor(self, securityLevel):
		"""This module sends the calculated security level to be stored on the monitoring device."""
		return

	def runForever(self):
		#print "Test"
		#i = 1
		while True:
			#securityLevel = self.checkHashes()
			print "Security Level of Rogue Changes Metric:", self.checkHashes()
			#print "Program has run", i, "times."
			#print "Automated Run of Rogue Changed Module"
			time.sleep(20) # Determines how often to recalculate the security level of the Rogue Changes metric.
			#i+=1
		#return self.checkHashes() # Returns security level

	def runOnce(self):
		#securityLevel = self.checkHashes()
		print "Security Level of Rogue Changes Metric:", self.checkHashes()
		print "Manual Run of Rogue Changes Metric."

def main():
	serverAddress = ('localhost', 29892) # let the kernel give us a port
	socketForDataCollection = ThreadedDataMonitorServer(serverAddress, ProcessReceivedData)
	serverThread = threading.Thread(target=socketForDataCollection.serve_forever)
	serverThread.setDaemon(True) # don't hang on exit
	serverThread.start()

	configDirectory = checkIntegrity("/home/x/systemConfig/")
	integrityCheckThread = threading.Thread(target=configDirectory.runForever)
	integrityCheckThread.start()

	while True:
		print "Another minute..."
		time.sleep(60)

if __name__ == "__main__":
    main()
