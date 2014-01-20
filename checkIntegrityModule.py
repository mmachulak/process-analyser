import glob
import hashlib
import os
import pickle
import threading
import time

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
			#print "MD5:", md5fileDigest # Returns digest of data fed into the update() method so far (using only hexadecimal digits).
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
			print "Security Level:", self.checkHashes()
			#print "Program has run", i, "times."
			print "Automated Run"
			time.sleep(5)
			#i+=1
		#return self.checkHashes() # Returns security level

	def runOnce(self):
		#securityLevel = self.checkHashes()
		print "Security Level:", self.checkHashes()
		print "Manual Run"


############

configDirectory = checkIntegrity("/home/gingerbeard/Dropbox/University/MSc Dissertation Evaluation/systemConfig/")
#integrityCheckThread = threading.Thread(target=configDirectory.runIntegrityCheck)
#print "Security Level:", configDirectory.runIntegrityCheck()
integrityCheckThread = threading.Thread(target=configDirectory.runForever).start()
#configDirectory.runOnce() # To only run integrity check once - use for TCP socket initialisation.


#print "Length:", len(currentHashes)
#filehandler = open("/home/gingerbeard/Dropbox/University/MSc Dissertation Evaluation/knownGoodHashes.pkl", 'w') 
#pickle.dump(currentHashes, filehandler)

