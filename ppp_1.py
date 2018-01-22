#!/bin/python

import time
import sys
import os 
import subprocess
import re
import shutil
import cStringIO
import glob
from subprocess import PIPE,Popen


#record elapsed time 
start_time= time.time()

print "************************************************************"
###boolean to check whether everything is in the right format and if the directory and filename are valid###
print "Arguments should be in the format: directory filename"
print "filename should be sans file extension"

directory= sys.argv[1]
filename= sys.argv[2]
#presto= sys.argv[3]
print "************************************************************"
print "directory:", directory
print "filename:", filename 
print "************************************************************"

#if directory doesn't exist, exit
if(not os.path.isdir(directory)):
	print "Invalid directory"

#if file doesn't exist, exit
if(not os.path.exists(directory+filename+".sf")):
	print "Invalid filename"
	sys.exit()

#if directory for particular file already exists, overwrite it
#if (os.path.isdir(filename)):
	#print "Removing existing directory", filename
	#shutil.rmtree(filename)

#make new directory for the data file
#os.mkdir(filename)
os.chdir(filename)

#create link to the data file in current directory from the source directory
#os.symlink(directory+filename+".sf",filename+".sf")

###start processing data###

#run rfifind
#subprocess.call(['rfifind', '-o', './'+filename, '-time', '2', './'+filename+'.sf'])

#get variables needed for DDplan.py from readfile commands
readfile = subprocess.check_output(["readfile",filename+".sf"])
print readfile
"""
bandw_regex = re.compile("Total Bandwidth \(MHz\) = (.+)\s+")
bandw = bandw_regex.search(readfile).group(1)
print bandw

cfreq_regex = re.compile("Central freq \(MHz\) = (.+)\s+")
cfreq = cfreq_regex.search(readfile).group(1)
print cfreq

num_chan_regex = re.compile("Number of channels = (\d+)")
num_chan = num_chan_regex.search(readfile).group(1)
print num_chan

smp_time_regex = re.compile("Sample time \(us\) = (.+)\s+")
smp_time = smp_time_regex.search(readfile).group(1)
smp_time = '0.000'+smp_time
print smp_time

numout_regex = re.compile("Spectra per file = (.+)\s+")
numout = numout_regex.search(readfile).group(1)
print numout
"""
nsub_regex = re.compile("samples per spectra = (.+)\s+")
nsub = nsub_regex.search(readfile).group(1)
print nsub
"""
#high dm
hdm='1000'
#low dm
ldm='0'
#time resolution
t_res='0.5'

#run DDplan.py
#ddplan_txt = subprocess.check_output(['DDplan.py', '-l', ldm, '-d', hdm, '-f', cfreq, '-b', bandw, '-n', num_chan, '-t', smp_time, '-r', t_res, '-o', filename])


#subband de-dispersion: call prepsubband on each call in DDplan
#get the line in file after last call
#print "Looping prepsubband..."
#starting_line = 13 
#i = -1
#print ddplan_txt
#ddplan_stream = cStringIO.StringIO(ddplan_txt)
'''for line in ddplan_stream.readlines():
	i = i + 1
	print 'in loop'
	print i, line
	if(i < starting_line): continue
	if(line.strip() == ""): break
	if(i == 14): break
	print i
	this_array = line.split()
	#low dm
	ldm=this_array[0]
	print ldm
	#dm step
	dms=this_array[2]
	print dms
	#downsamp
	ds=this_array[3]
	print ds
	#number of dms
	ndm=this_array[4]
	print ndm
	#numout (numout from DDplan / downsamp)
	numout1= str(int(numout)/int(ds))
	print numout1

	#run prepsubband command
	subprocess.call(['prepsubband', '-nsub', nsub ,'-lodm', ldm, '-dmstep', dms, '-numdms', ndm, '-numout', numout1, '-downsamp', ds, '-mask', filename+'_rfifind.mask', '-o', filename, filename+'.sf'])'''

#print "Running realfft..."
#for f in glob.glob("*.dat"):
	#print f
	#subprocess.call(['realfft', f])

#print "Running accelsearch..."
#for f in glob.glob("*.fft"):
	#print f
	#subprocess.call(['accelsearch', '-zmax', '0', f])

#print "Running ACCEL_sift.py..."
#cands_txt = subprocess.check_output(['python', presto+'ACCEL_sift.py'])
#cand_txt = Popen(['python', presto+'ACCEL_sift.py'],stdout=PIPE)
#print cands_txt
"""
#Prepare to run prepfold 
with open("cands.txt") as cands_txt:
    cands_data = cands_txt.read() 
cands_regex = re.findall("ACCEL_0:(\d+)\s+(\d+\.?\d*)\s+\d+\.?\d*\s+\d+\.?\d*\s+\d+\.?\d*\s+\d+\.?\d*\s+\d+\.?\d*\s+(\d+\.?\d*)\s+", cands_data)

cand_num=[]
cand_dm=[]
cand_period=[]

for lst in cands_regex:
     cand_num.append(lst[0])
     cand_dm.append(lst[1])
     cand_period.append(lst[2])
total = len(cand_num) 

for i in range(0, total):
     
     print "Running candidate", str(i+1), "out of", str(total), "candidates."
     
     this_cand_num = cand_num[i]
     this_cand_dm = cand_dm[i]
     this_cand_period = cand_period[i]

     datfilename = filename+"_DM"+this_cand_dm
     accelfilename = datfilename+"_ACCEL_0"

     subprocess.call(["prepfold", "-mask", filename+"_rfifind.mask", "-accelcand", this_cand_num, "-nsub", nsub, "-dm", this_cand_dm, "-accelfile", accelfilename+".cand", filename+".sf", "-o", filename+"_"+this_cand_dm, "-nosearch", "-noxwin"])

#Move all candidate png's to seperate folder
os.mkdir("cand_plots")
subprocess.call(["cp", "*.png", "./cand_plots"])




''' Things to do:

1)Run in an environment with a working version of ACCEL_sift.py 
2)Run whole script and make sure prepfold output works
3)Stop subprocess calls from doing output
4)Add an argument for different file types (e.g. .sf or .fits)
'''






elapsed_time = time.time() - start_time
print (elapsed_time), "time" 
