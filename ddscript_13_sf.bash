#!/bin/bash

#A script to process single .sf data files through the PRESTO pipeline.

#command line arguments are in the format: ddscript_[n]_sf.bash directory filename
#where n = version of this script

#redirect outputs to a log file:
#exec &> logfile3.txt

STARTTIME="$(date -u +%s)"
echo "************************************************************"
#boolean to check whether or not everything is in the right format and if the directory and filename are valid
echo "Arguments should be in the format: directory filename"
echo "filename should be sans file extension"

directory=$1
filename=$2
echo "************************************************************"
echo "directory: $directory"
echo "filename: $filename"
echo "************************************************************"
#if directory is invalid, exit
if [ ! -d $directory ]; then
	echo "invalid directory."
	exit 0
fi

#if file doesn't exist, exit
if [ ! -e "$directory/$filename.sf" ]; then
	echo "invalid filename."
	exit 0
fi

#if directory for this particular already exists, overwrite it
if [ ! -d $filename ]; then
	echo -e "Creating new directory for $filename.\n\n"
	rm -r $filename
fi

#create new folder for data files
mkdir $filename
cd $filename

#create link to file in current directory in the folder
ln -s $directory/$filename.sf ./

echo "************************************************************"

#run rfifind:
echo "Running rfifind..."
rfifind -o ./$filename -time 2 ./$filename.sf >> /dev/null

echo "************************************************************"

#get variables needed for DDplan.py from readfile:
 #low dm
 ldm=0
 #high dm
 hdm=1000
 #bandwidth
 bandw=`readfile $filename.sf | grep "Total Bandwidth" | awk '{print $5}'`
 #time resolution
 t_res=0.5
 #center frequency
 cfreq=`readfile $filename.sf | grep "Central freq" | awk '{print $5}'`
 #number of channels
 num_chan=`readfile $filename.sf | grep "Number of channels" | awk '{print $5}'`
 #sample time
 smp_time=`readfile $filename.sf | grep "Sample time" | awk '{print $5}'`
 smp_time=0.000$smp_time
 #spectra per file 
 numout=`readfile $filename.sf | grep "Spectra per file" | awk '{print $5}'`

echo "**File information**"
 echo "low dm"= $ldm
 echo "high dm"= $hdm
 echo "bandwidth"= $bandw
 echo "Center freq"= $cfreq
 echo "Num of channels"= $num_chan
 echo "time resolution"= $t_res
 echo "Sample time"= $smp_time
 echo "spectra per file"= $numout

echo "************************************************************"
 
#run DDplan.py
echo "Running DDplan.py..."
DDplan.py -l $ldm -d $hdm -f $cfreq -b $bandw -n $num_chan -t $smp_time -r $t_res -o $filename | tee ddplaninfo.txt >> /dev/null

echo "************************************************************"

#subband de-dispersion: call prepsubband on each call in DDplan
#get the line in file after last call
echo "Looping prepsubband..."
lastline=14
line=`head -$lastline ddplaninfo.txt | tail -1`
while [ "$line" != "" ]; do
	((lastline++))
	line=`head -$lastline ddplaninfo.txt | tail -1`
done

#loop prepsubband for all calls in ddplaninfo
for (( i=14; i<lastline; i++ ))
do
	#get the call from the current line in the file
	call=`head -$i ddplaninfo.txt | tail -1`

	#put call into an array
	IFS=' ' read -a array <<<"$call"

	#get all the variables:
	#nsub
 	nsub=`readfile $filename.sf | grep "samples per spectra" | awk '{print $5}'`
 
	#low dm
	ldm=${array[0]}
	
	#dm step
	dms=${array[2]}
	
	#number of dms
	ndm=${array[4]}
	
	#downsamp
	ds=${array[3]}

	#numout (numout from DDplan / downsamp)
	numout1=$(( $numout / $ds ))

	#run prepsubband command
	prepsubband -nsub $nsub -lodm $ldm -dmstep $dms -numdms $ndm -numout $numout1 -downsamp $ds -mask ${filename}_rfifind.mask -o $filename $filename.sf >> /dev/null
done

echo "************************************************************"

#run realfft on all .dat files
echo "Running realfft..."
ls *.dat | xargs -n 1 --replace realfft {} >> /dev/null

echo "************************************************************"

#run accelsearch on all .fft files
echo "Running accelsearch..."
ls *.fft | xargs -n 1 accelsearch -zmax 0 >> /dev/null

echo "************************************************************"

#run ACCEL_sift.py on all candidates
echo "Running ACCEL_sift.py..."
#in GZNU server, re-direct X11 interface to admin1 (for job grid compatability)
  #tmp=`echo $DISPLAY`
  #export DISPLAY=10.10.10.24:19.0
  python $PRESTO/python/ACCEL_sift.py > cands.txt
  #export DISPLAY=$tmp
  #cd $tmp

echo "************************************************************"

echo "Preparing to run prepfold on best candidates..."
#prepare to run prepfold
 #make list of DMs
 dmslist=`grep "ACCEL" cands.txt | awk '{print $2}'`
 #make into an array
 dmsarr=($dmslist)

 #make list of candidate numbers
 candlist=`grep "ACCEL" cands.txt | awk '{print $1}'`
 #make into an array
 candarr=($candlist)
 echo "$candlist"

 #make list of periods
 periodslist=`grep "ACCEL" cands.txt | awk '{print $8/1000}'`
 #make into an array
 periodsarr=($periodslist)
 echo "$periodslist"

 #get total number of candidates
 tot=`grep "ACCEL" cands.txt | wc | awk '{print $1}'`
 echo $tot

#loop prepfold through all viable candidates
for (( i=0; i<tot; i++ ))
do
	echo "Running prepfold on candidate # $(( $i+1 )) out of $tot candidates"
	
	#get filename of ACCEL_0 cands file and candnum
	line=${candarr[$i]}
	accelfilename="$(cut -d':' -f1 <<< $line)"
	candnum="${line: -1}"
	echo "candnum: $candnum"
	
	#get dat filename
	length=$(( ${#accelfilename}-8 ))
	datfilename="${accelfilename: 0:$length}"
	echo $datfilename	
	
	#get time series plots
	#string="prepfold -mask ${filename}_rfifind.mask -accelcand 2 -p ${periodsarr[$i]} -dm ${dmsarr[$i]} -nsub $nsub -accelfile $accelfilename.cand $datfilename.dat -noxwin"
	#echo $string
	#$string

	#get raw data plots
	string1="prepfold -mask ${filename}_rfifind.mask -accelcand $candnum -nsub $nsub -dm ${dmsarr[$i]} -accelfile $accelfilename.cand ${filename}.sf -o ${filename}_${dmsarr[$i]} -nosearch -noxwin" 
	echo $string1
	$string1
done

#move candidate png's to seperate folder
echo "Moving candidates to new folder 'plots'"
mkdir plots
ls *.png
cp *.png ./plots

#For some reason, some files wont output an ACCEL_0.cand file, and so the time series plots cannot be viewed

ENDTIME="$(date -u +%s)"
echo -e "\n\nTime elapsed for processing $filename: $(($ENDTIME - $STARTTIME)) seconds."
exit 0
