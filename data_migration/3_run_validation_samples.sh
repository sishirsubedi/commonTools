#!/usr/bin/env bash

if [ $# -eq 0 ]
then
	echo "-u user"
	echo "-p password"
  echo "-e environment"
  exit
fi

if test $# -gt 0
	then
	while getopts :u:p:e: opt
	do
	case $opt in
	u)
	  user=$OPTARG
		;;
	p)
	 password=$OPTARG
	  ;;
  e)
  	 environment=$OPTARG
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


DB="ngs_"${environment}

clearsamples="delete from samples where 1=1;delete from pipelineQueue where 1=1"
mysql --user="$user" --password="$password" --database="$DB" --execute="$clearsamples"



while read instrument assay runID variantcaller coveragcaller sample; do

  echo $instrument $assay $runID $variantcaller $coveragcaller $sample

  sampleName="$(echo -e "${sample}" | tr -d '[:space:]')"

  insertintosamples="insert into samples "\
"(assayID, instrumentID, runID, sampleName, coverageID, callerID, lastName, firstName, orderNumber, enteredBy) "\
"values ( (select assayID from assays where assayName='$assay' ), (select instrumentID from instruments where instrumentName='$instrument'), '$runID', '$sampleName', '$coveragcaller', '$variantcaller', 'test', 'test', '123', 'hhadmin' )"

   mysql --user="$user" --password="$password" --database="$DB" --execute="$insertintosamples"

done < /home/hhadmin/hmvv_validation/3_1_to_3_2/2_validation_samplelist.txt

getsampleids="select sampleID from samples"
sampleIDs=$(mysql --user="$user" --password="$password" --database="$DB" --execute="$getsampleids" -N)
echo "$sampleIDs"

for i in $sampleIDs;do
  echo "sample id is $i"
  insertintoqueues="INSERT INTO pipelineQueue (sampleID,timeSubmitted) VALUES ($i, now() )";
  mysql --user="$user" --password="$password" --database="$DB" --execute="$insertintoqueues"
done


bash /home/pipelines/ngs_validation/shell/runPipelines.sh -e validation -u  -p   >  /home/pipelines/ngs_validation/cron_logs/pipeline_"$(date +"%Y_%m_%d_%H_%M_%S").log"
