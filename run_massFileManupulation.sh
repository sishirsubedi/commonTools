#!/bin/bash
input="samples.csv"
OLDIFS=$IFS
IFS=","
while read run sample
do
  sampleName="$(echo -e "${sample}" | tr -d '[:space:]')"
  # echo "--$run--$sampleName--"
  qsub -F "$run  $sampleName" /home/pipelines/ngs_test/shell/FileManupulation.sh
  # bash /home/pipelines/ngs_test/shell/FileManupulation.sh  $run  $sampleName

done < "$input"
IFS=$OLDIFS
