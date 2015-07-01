#!/usr/bin/python

# setdatetime.py
#
# This script takes two arguments, local file root and remote file root. It then gets the last modified date of all the 
# files and folders of the remote directory and makes the same files in the local directory have the same last modified
# date
import paramiko
import argparse
import os
import re

# load ssh
ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('midas',username='jacob') 

def getRemoteFileTime(ssh, remoteFile):
	command = './gettime "' + remoteFile + '"'
	stdin, stdout, stderr = ssh.exec_command(command)
	strOutput = stdout.read().decode("utf-8").strip() 
	if not strOutput:
		raise ValueError('Remote file time get failed to get a good string')
	return int(strOutput)

def updateLocalFileTime(localFile, time):
	os.utime(localFile, (time, time))
	print('"' + localFile + '" updated to time ' + str(time))

def makeLocalFileTimeRemotes(ssh, localFile, remoteFile):
	try:
		time = getRemoteFileTime(ssh, remoteFile) 
		updateLocalFileTime(localFile, time) 
	except ValueError as err:
		print(err.args)
		pass

parser = argparse.ArgumentParser()
parser.add_argument("file1")
parser.add_argument("file2")
args = parser.parse_args()

localFileRoot = args.file1
remoteFileRoot = args.file2
for root, dirs, files in os.walk(localFileRoot):
	for dir in dirs: 
		commonFile = os.path.relpath(os.path.join(root, dir), args.file1)
		makeLocalFileTimeRemotes(ssh, os.path.join(args.file1, commonFile), os.path.join(args.file2, commonFile))
	for file in files:
		commonFile = os.path.relpath(os.path.join(root, file), args.file1)
		makeLocalFileTimeRemotes(ssh, os.path.join(args.file1, commonFile), os.path.join(args.file2, commonFile))
