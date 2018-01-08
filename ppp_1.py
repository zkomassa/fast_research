#!/bin/python

import time
import sys
import os 
import subprocess
import re

#record elapsed time 
start_time= time.time()

print "************************************************************"
###boolean to check whether everything is in the right format and if the directory and filename are valid###
print "Arguments should be in the format: directory filename"
print "filename should be sans file extension"

directory= sys.argv[1]
filename= sys.argv[2]
print "************************************************************"
print "directory:", directory
print "filename:", filename 
print "************************************************************"

#if directory doesn't exist, exit
if(not os.path.isdir(directory)):
	print "Invalid directory"

#if file doesn't exist, exit
if(not os.path.exists(directory+filename".fits")):
	print "Invalid filename"
	sys.exit()

#if directory for particular file already exists, overwrite it
if (os.path.isdir(filename)):
	print "Removing existing directory", filename
	shutil.rmtree(filename)

#make new directory for the data file
os.mkdir(filename)
os.chdir(filename)

#create link to the data file in current directory from the source directory
os.symlink(directory+filename+".fits",filename+".fits")

###start processing data###

#run rfifind
subprocess.call(['rfifind', '-o', './'+filename, '-time 2', './'+filename+'.fits', '>>', 'dev/null'])

#get variables needed for DDplan.py from readfile commands
readfile = subprocess.check_output(["readfile",filename+]".fits"])

bandw_regex = re.compile("Total Bandwidth \(MHz\) = (.+)\s+")
bandw = bandw_regex.search(readfile).group(1)
print bandw

cf_regex = re.compile("Central freq \(MHz\) = (.+)\s+")
cfreq = cfreq_regex.search(readfile).group(1)
print cfreq

num_chan_regex = re.compile("Central freq \(MHz\) = (.+)\s+")
num_chan = num_chan_regex.search(readfile).group(1)
print num_chan

smp_time_regex = re.compile("Central freq \(MHz\) = (.+)\s+")
smp_time = smp_time_regex.search(readfile).group(1)
print smp_time

numout_regex = re.compile("Central freq \(MHz\) = (.+)\s+")
numout = numout_regex.search(readfile).group(1)
print numout





elapsed_time = time.time() - start_time
print (elapsed_time)*1000.0, "seconds" 
