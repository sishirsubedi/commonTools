#!/bin/bash

DATE=`date '+%Y-%m-%d %H:%M:%S'`
echo "SOP ----- archer_data_archive.sh  at - $DATE"

path="/var/www/analysis"

runs=( $(find /$path -maxdepth 1 -type d -mtime +365 | cut -d "/" -f 6 ) )

for run in ${runs[*]}; do
   
  # check valid archer run -- must be four digit number
  validrun=${#run}
  
  if [[ "$validrun" == 4 ]] && [[ "$run" =~ ^[0-9]+$  ]] ; then
  
     echo "########## processing run : $run ######"
     echo "run info: "$( ls -ld /$path/$run)" "

     fastqfiles=( $(find /$path/$run -mindepth 1 -type f -name "*.fastq.gz" | wc -l ) )

     echo "number of fastqfiles $fastqfiles"


     if [ "$fastqfiles" -gt 0  ]; then
     
         # remove all fastq files
         echo "removing fastq files"
         sudo rm -f  $path/$run/*.fastq.gz
         
 
     else
         message="There are no fastq files on this $run directory to delete."
         echo $message
         
     fi

     # zip remaining files in archive folder
     rundate=$( stat -c '%y' /$path/$run |cut -d " " -f1,2 | cut -c'1-19'| sed -e 's/\s/_/g' -e 's/\:/\_/g' )
     echo "archive directory is named as :  "$run"_"$rundate""
     tar -czf /archive/Archer_ARCHIVE/archer_archive_"$run"_"$rundate".tar.gz $path/$run/*


     if [ -f /archive/Archer_ARCHIVE/archer_archive_"$run"_"$rundate".tar.gz ]; then

           # remove run from analysis folder
           sudo rm -rf $path/$run

    else

           message="ERROR - Archive file was NOT CREATED in archive directory!"
           echo $message
           echo $message | mail -s "Archer Data Archive Run - $run Archive not created" "ssubedi@houstonmethodist.org"

    fi


   else
         message="$run is not a valid archer run."
         echo $message
         echo $message | mail -s "Archer Data Archive Run - $run is not valid " "ssubedi@houstonmethodist.org" 
     fi
   

done

DATE=`date '+%Y-%m-%d %H:%M:%S'`
echo " EOP ----- archer_data_archive.sh  at - $DATE"


# to uncompress the file in archive directory

### make directory with same runnumber 
#mkdir runNumber ## same as archer_archive_"runNumber".tar.gz

### unzip to runNumber folder
#tar -xzf archer_archive_runNumber.tar.gz -C runNumber