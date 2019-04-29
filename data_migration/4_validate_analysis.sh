#!/usr/bin/env bash

rm -f validationResults.txt
rm -f validationResults_VEPCosmic.txt

while read instrument assay runID variantcaller coveragcaller sample; do

  echo $instrument $assay $runID $variantcaller $coveragcaller $sample

  sampleName="$(echo -e "${sample}" | tr -d '[:space:]')"

  /opt/python3/bin/python3 5_validateAnalysis.py -i "${instrument}" -a "${assay}" -r "${runID}" -v "${variantcaller}" -c "${coveragcaller}" -s "${sampleName}"

done < 2_validation_samplelist.txt


while read instrument assay runID variantcaller coveragcaller sample; do

  echo $instrument $assay $runID $variantcaller $coveragcaller $sample

  sampleName="$(echo -e "${sample}" | tr -d '[:space:]')"

  /opt/python3/bin/python3 6_validateVEP-COSMIC.py -u "" -p "" -i "${instrument}" -a "${assay}" -r "${runID}" -v "${variantcaller}" -c "${coveragcaller}" -s "${sampleName}" >> validationResults_VEPCosmic.txt

done < 2_validation_samplelist.txt
