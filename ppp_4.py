########################### PYTHON PRESTO PIPELINE ###########################

import time
import sys
import os 
import subprocess
import re
import shutil
import cStringIO
import glob
from subprocess import PIPE,Popen


#function for prepsubband loop (line 130)
def is_number(s):
     try:
	 float(s)
	 return True 
     except ValueError:
	 return False

#constant to negate subprocess output
FNULL = open(os.devnull, 'w')

#record elapsed time 
start_time= time.time()

print "************************************************************"

###boolean to check if arguments are in the right format and if the Directory and Filename are valid###

print "Arguments should be in the format: [Directory] [Filename]"

directory= sys.argv[1]
filename_ext= sys.argv[2].split(".")  

filename = filename_ext[0]
ext = "."+filename_ext[1]

print "************************************************************"
print "Directory:", directory
print "Filename:", filename 
print "************************************************************"

#if directory doesn't exist, exit
if(not os.path.isdir(directory)):
	print "Invalid directory"

#if file doesn't exist, exit
if(not os.path.exists(directory+filename+ext)):
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
os.symlink(directory+filename+ext,filename+ext)


###START PROCESSING DATA###


print "Running rfifind..."
#run rfifind
subprocess.call(['rfifind', '-o', './'+filename, '-time', '2', './'+filename+ext], stdout=FNULL, stderr=subprocess.STDOUT)
print "********************************************************"

print "Grabbing file information..."
#get variables needed for DDplan.py from readfile commands
readfile = subprocess.check_output(["readfile",filename+ext])

bandw_regex = re.compile("Total Bandwidth \(MHz\) = (.+)\s+")
bandw = bandw_regex.search(readfile).group(1)
print "Bandwidth=", bandw

cfreq_regex = re.compile("Central freq \(MHz\) = (.+)\s+")
cfreq = cfreq_regex.search(readfile).group(1)
print "Central freq=", cfreq

num_chan_regex = re.compile("Number of channels = (\d+)")
num_chan = num_chan_regex.search(readfile).group(1)
print "Number of channels=", num_chan

smp_time_regex = re.compile("Sample time \(us\) = (.+)\s+")
smp_time = smp_time_regex.search(readfile).group(1)
smp_time = float(smp_time)
smp_time = str((smp_time)/int(1000000))
print "Sample time=", smp_time

numout_regex = re.compile("Spectra per file = (.+)\s+")
numout = numout_regex.search(readfile).group(1)
print "Spectra per file=", numout

nsub_regex = re.compile("samples per spectra = (.+)\s+")
nsub = nsub_regex.search(readfile).group(1)
print "Samples per spectra=", nsub

#high dm
hdm='400'
print "High DM=", hdm
#low dm
ldm='0'
print "Low DM=", ldm
#time resolution
t_res='0.5'
print "Time resolution=", t_res
print "********************************************************"

#run DDplan.py
ddplan_txt = subprocess.check_output(['DDplan.py', '-l', ldm, '-d', hdm, '-f', cfreq, '-b', bandw, '-n', num_chan, '-t', smp_time, '-r', t_res, '-o', filename])

#subband de-dispersion: call prepsubband on each call in DDplan
print "Looping prepsubband..."
#starting_line = 11
i = -1
ddplan_stream = cStringIO.StringIO(ddplan_txt)
for line in ddplan_stream.readlines():
	i = i + 1
	print i, line
	if(line.strip() == ""): continue
	#print i
	this_array = line.split()
	#low dm
	ldm=this_array[0]
	if not is_number(ldm): continue
	#print ldm
	#dm step
	dms=this_array[2]
	#print dms
	#downsamp
	ds=this_array[3]
	#print ds
	#number of dms
	ndm=this_array[4]
	#print ndm
	#numout (numout from DDplan / downsamp)
	numout1= str(int(numout)/int(ds))
	#print numout1

	#run prepsubband command
	subprocess.call(['prepsubband', '-nsub', nsub ,'-lodm', ldm, '-dmstep', dms, '-numdms', ndm, '-numout', numout1, '-downsamp', ds, '-mask', filename+'_rfifind.mask', '-o', filename, filename+ext])#, stdout=FNULL, stderr=subprocess.STDOUT)

print "Running realfft..."
for f in glob.glob("*.dat"):
	print f
	subprocess.call(['realfft', f], stdout=FNULL, stderr=subprocess.STDOUT)

print "Running accelsearch..."
for f in glob.glob("*.fft"):
	print f
	subprocess.call(['accelsearch', '-zmax', '20', f], stdout=FNULL, stderr=subprocess.STDOUT)

#move any files that won't play nice (usually a result of prepsubband not working correctly):
#os.mkdir('wont_sift')
#subprocess.call(["mv", filename+"_ACCEL*", "./wont_sift"])

#copy ACCEL_sift.py into current working directory
subprocess.call(["cp", '../ACCEL_sift.py', '.'], stdout=FNULL, stderr=subprocess.STDOUT)

print "Running ACCEL_sift.py..."
cands_txt = subprocess.check_output(['python', 'ACCEL_sift.py'])

#Prepare to run prepfold  
cands_regex = re.findall("ACCEL_20:(\d+)\s+(\d+\.?\d*)\s+\d+\.?\d*\s+\d+\.?\d*\s+\d+\.?\d*\s+\d+\.?\d*\s+\d+\.?\d*\s+(\d+\.?\d*)\s+", cands_txt) #change the value of "ACCEL_[]" depending on zmax (line 156)

cand_num=[]
cand_dm=[]
cand_period=[]

for lst in cands_regex:
     cand_num.append(lst[0])
     cand_dm.append(lst[1])
     cand_period.append(lst[2])
total = len(cand_num) 

for i in range(0, total):
     
     print "Folding candidate", str(i+1), "out of", str(total), "candidates."
     
     this_cand_num = cand_num[i]
     this_cand_dm = cand_dm[i]
     this_cand_period = cand_period[i]

     datfilename = filename+"_DM"+this_cand_dm
     accelfilename = datfilename+"_ACCEL_20" #change this number depending on the zmax value (line 156)

     subprocess.call(["prepfold", "-mask", filename+"_rfifind.mask", "-accelcand", this_cand_num, "-nsub", nsub, "-dm", this_cand_dm, "-accelfile", accelfilename+".cand", filename+ext, "-o", filename+"_"+this_cand_dm, "-nosearch", "-noxwin"], stdout=FNULL, stderr=subprocess.STDOUT)

#Move all candidate png's to seperate folder
os.mkdir("cand_plots")
for f in glob.glob("*.png"):
	subprocess.call(['cp', f, './cand_plots'], stdout=FNULL, stderr=subprocess.STDOUT)


elapsed_time = time.time() - start_time
print (elapsed_time), "seconds" 
