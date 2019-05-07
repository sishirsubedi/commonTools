#!/bin/bash

log()
{
 MESSAGE=$1
 TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S"`
 SCRIPT=$( basename $0 )
 echo " [ $TIMESTAMP ] [ $SCRIPT ] $MESSAGE "
}

create_file()
{
  touch  $1
  chmod 775  $1
}

create_dir()
{
	new_dir=$1
	if [ ! -d $new_dir ] ; then
		mkdir $new_dir
	fi
	chmod 775 $new_dir
}

find_test_files()
{

  if [ $INSTRUMENT == "proton" ] ; then
    find $HOME_BACKUP  -mtime -$DAYS -type f -name "*.vcf"  | shuf | head  > $TEST_FILES
  elif [ $INSTRUMENT == "nextseq" ] ; then
    find $HOME_BACKUP  -mtime -$DAYS -type f -name "*.fastq.gz"  | shuf | head > $TEST_FILES
  elif [ $INSTRUMENT == "miseq" ] ; then
    find $HOME_BACKUP  -mtime -$DAYS -type f  | shuf | head > $TEST_FILES
  fi

}

cksum_on_backup()
{
  while read -r line ; do
    cksum $line >> $BACKUP_CKSUM
  done < $TEST_FILES
}

cksum_on_hh()
{
  while read -r line ; do

    #TO-DO try to find a way to use $HOME_HH instead of hard coding
    mod_file_path=$(echo $line | sed "s/\/archive\/commvault_restore//g")
    cksum ${HOME_HH}${mod_file_path}  >> $HH_CKSUM

  done < $TEST_FILES
}

generate_report()
{
  /opt/python3/bin/python3 ${HOME_PYTHON}compare_cksum.py $HH_CKSUM $BACKUP_CKSUM $REPORT_FILE
}

main()
{
  CURRENTDT=`date '+%Y_%m_%d_%H_%M_%S'`
  INSTRUMENT=$1
  DAYS="30"

  log "Running Data Integrity Check QC for $CURRENTDT on $INSTRUMENT"

  HOME_BACKUP="/archive/commvault_restore/${INSTRUMENT}/"
  HOME_HH="/home"
  HOME_RUN_MONTH="/home/environments/qc_procedure/data_integrity/backup_to_hh/${CURRENTDT}/"
  HOME_RUN="${HOME_RUN_MONTH}${INSTRUMENT}/"
  HOME_PYTHON="/home/pipelines/qc_procedure/"

  TEST_FILES="${HOME_RUN}${CURRENTDT}_DataIntegrityCheck_FilesList.txt"
  HH_CKSUM="${HOME_RUN}${CURRENTDT}_DataIntegrity_hh.cksum"
  BACKUP_CKSUM="${HOME_RUN}${CURRENTDT}_DataIntegrity_backup.cksum"
  REPORT_FILE="${HOME_RUN}${CURRENTDT}_DataIntegrity_hh_backup.cksum.report.txt"

  create_dir   $HOME_RUN_MONTH
  create_dir   $HOME_RUN
  create_file  $TEST_FILES
  create_file  $HH_CKSUM
  create_file  $BACKUP_CKSUM
  create_file  $REPORT_FILE

  log "Selecting files from backup restore:$HOME_BACKUP"

  find_test_files

  log "cksum on backup server:$HOME_BACKUP"

  cksum_on_backup


  log "cksum on Holly Hall:$HOME_HH"

  cksum_on_hh

  log "Generating Report:$HOME_RUN"

  generate_report

  log "Completed"

}

main $*
