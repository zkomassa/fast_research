# fast_research

*Descriptions of each of the main scripts for processing raw pulsar data:*

**pulsardatascript_orig.bash** = A simple script to perform a readfile on some important info of any data file.

**ddscript_13_fits.bash** = Final PRESTO script made to process Arecibo files (**.fits** files).

**ddscript_13_sf.bash** = Final PRESTO script made to process Parkes Mulit-Beam files (**.sf** files).

**process_all_arecibo_files.bash** = A script to process every **.fits** file with **ddscript_13_fits.bash** in blocks of 7 files at a time.

**ppp_4.py** = (Work in progress) Python PRESTO Pipeline: A remastered version of **ddscript_13_sf.bash** written in Python rather than Bash. (takes either file type as an argument now!)
