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
  find $HOME_HH -maxdepth 2  -mtime -30 -type f -name "*.bam" | shuf | head > $TEST_FILES
}

cksum_on_hh()
{
  while read -r line ; do
    cksum $line >> $HH_CKSUM
  done < $TEST_FILES
}

cksum_on_proton()
{
  while read -r line ; do

    #TO-DO try to find a way to use $HOME_HH instead of hard coding
    mod_file_path=$(echo $line | sed "s/\/home\/proton//g")

    echo "${HOME_PROTON}${mod_file_path}" | xargs ssh hhadmin@10.40.16.116 "cksum" >> $PROTON_CKSUM

  done < $TEST_FILES
}

generate_report()
{
  /opt/python3/bin/python3 ${HOME_PYTHON}compare_cksum.py $HH_CKSUM $PROTON_CKSUM $REPORT_FILE
}

main()
{
  CURRENTDT=`date '+%Y_%m_%d_%H_%M_%S'`
  HOME_PROTON="/results/analysis/output/Home"
  HOME_HH="/home/proton"
  HOME_RUN="/home/environments/qc_procedure/data_integrity/proton_to_hh/${CURRENTDT}/"
  HOME_PYTHON="/home/pipelines/qc_procedure/"

  TEST_FILES="${HOME_RUN}${CURRENTDT}_DataIntegrityCheck_FilesList.txt"
  HH_CKSUM="${HOME_RUN}${CURRENTDT}_DataIntegrity_hh.cksum"
  PROTON_CKSUM="${HOME_RUN}${CURRENTDT}_DataIntegrity_proton.cksum"
  REPORT_FILE="${HOME_RUN}${CURRENTDT}_DataIntegrity_hh_proton.cksum.report.txt"

  create_dir   $HOME_RUN
  create_file  $TEST_FILES
  create_file  $HH_CKSUM
  create_file  $PROTON_CKSUM
  create_file  $REPORT_FILE

  log "Selecting files from Holly Hall:$HOME_HH"

  find_test_files

  log "cksum on Holly Hall:$HOME_HH"

  cksum_on_hh

  log "cksum on Proton server:$HOME_PROTON"

  cksum_on_proton

  log "Generating Report:$HOME_RUN"

  generate_report

  log "Completed"

}

main $*
