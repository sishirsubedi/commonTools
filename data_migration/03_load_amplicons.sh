#!/usr/bin/env bash


if [ $# -eq 0 ]
then
	echo "-u user"
	echo "-p password"
  echo "-d database"
  exit
fi

if test $# -gt 0
	then
	while getopts :u:p:d: opt
	do
	case $opt in

	u)
	  user=$OPTARG
		;;
	p)
	 password=$OPTARG
	  ;;
  d)
  	 database=$OPTARG
  	  ;;
	:)
		echo "Option -$OPTARG requires an argument."
		;;
	\?)
		echo "Invalid option: -$OPTARG"
	esac
	done
	shift $((OPTIND-1))
fi


while read sampleID assay  instrument runID sample coveragcaller variantcaller runDate  ; do

  echo $instrument $assay $runID $variantcaller $coveragcaller  $sampleID $sample

  /opt/python3/bin/python3 /home/hhadmin/hmvv_validation/03_filterAmplicons.py -i "${instrument}" -r "${runID}" -v "${variantcaller}" -c "${coveragcaller}" -d "${sampleID}" -s "${sample}"

  ampliconstatement=""

  sampleName="$(echo -e "${sample}" | tr -d '[:space:]')"

  if [ $instrument == "proton" ]
    then
      ampliconfile=$(ls /home/"$instrument"Analysis/*$runID/$coveragcaller/$sampleName/amplicon.filter.v2.txt)
      echo "file is  "$ampliconfile" "
      ampliconstatement="load data local infile '$ampliconfile' into table sampleAmplicons FIELDS TERMINATED BY '\t' (sampleID, gene, ampliconName,readDepth )"

  elif  [ $instrument == "miseq" ]
  then
      ampliconfile=$(ls /home/"$instrument"Analysis/*_"$runID"_*/$sampleName.amplicon.v2.txt)
      echo "file is  "$ampliconfile" "
      ampliconstatement="load data local infile '$ampliconfile' into table sampleAmplicons FIELDS TERMINATED BY '\t' (sampleID, gene, ampliconName,readDepth )"

  elif [ $instrument == "nextseq" ]
  then
      ampliconfile=$(ls /home/"$instrument"Analysis/*_"$runID"_*/$sampleName.amplicon.v2.txt)
      echo "file is  "$ampliconfile" "
      ampliconstatement="load data local infile '$ampliconfile' into table sampleAmplicons FIELDS TERMINATED BY '\t' (sampleID, gene, ampliconName,readDepth )"
  fi

  mysql --user="$user" --password="$password" --database="$database" --execute="$ampliconstatement"

done < /home/hhadmin/hmvv_validation/old_samples_for_amplicons.txt
# done < /home/hhadmin/hmvv_validation/testruns.txt
