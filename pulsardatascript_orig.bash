#!/bin/bash

#counter for number of files
file_no=`ls /home/zkomassa/arecibo_data/*.fits | wc -l`
echo "Total number of files: $file_no" >> ${filename}_file_details.txt

#do the process for all the files
for((i=1;i<=file_no;i++))
do
  #get filename
  filename=`ls *.fits | sed -n "$i p"`

  #echo "Process $filename"

  #sample time
  t_sample=`readfile $filename | grep "Sample time" | awk '{print $5}'`

  #lowest frequency
  lfreq=`readfile $filename | grep "Low channel" | awk '{print $5}'`

  #center frequency
  cfreq=`readfile $filename | grep "Central freq" | awk '{print $5}'`

  #highest frequency
  hfreq=`readfile $filename | grep "High channel" | awk '{print $5}'`

  #frequency resolution
  fr=`readfile $filename | grep "Channel width" | awk '{print $5}'`

  #length of file
  length=`readfile $filename | grep "Time per file" | awk '{print $6}'`

  #number of channels
  num_chan=`readfile $filename | grep "Number of channels" | awk '{print $5}'`

  #total bandwidth
  tot_band=`readfile $filename | grep "Total Bandwidth" | awk '{print $5}'`

  #subints per file
  subints=`readfile $filename | grep "Subints per file" | awk '{print $5}'`
  
  #time per subint 
  time_subint=`readfile $filename | grep "Time per subint" | awk '{print $6}'`

  #print out the data
  #echo "Process $filename, sampling time $t_sample us, lowest frequency $lfreq MHz, highest frequency $hfreq MHz, frequency resolution $fr, length of file $length s."
  echo "Process $filename, sampling time $t_sample us, frequency resolution $fr, length of file $length s, number of channels $num_chan, total bandwidth $tot_band, subints per file $subints, time per subint $time_subint, highest frequency $hfreq, lowest frequency $lfreq." >> ${filename}_file_details_.txt
done


