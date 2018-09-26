#!/usr/bin/env bash

while read instrument assay runID variantcaller coveragcaller sample; do

  echo $instrument $assay $runID $variantcaller $coveragcaller $sample

  /opt/python3/bin/python3 01_validateAnalysis.py -i "${instrument}" -r "${runID}" -v "${variantcaller}" -c "${coveragcaller}" -s "${sample}"

#done < Validation_samples.txt
done < testruns.txt
