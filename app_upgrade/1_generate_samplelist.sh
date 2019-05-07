#!/usr/bin/env bash


FILE="2_validation_samplelist.txt"

if [ -f $FILE ]; then
  rm $FILE
fi

mysql --user='' --password='' --database='ngs_live' --execute='select i.instrumentName,a.assayName,s.runID, \
s.callerID,s.coverageID,s.sampleName from samples as s join assays as a on s.assayID= a.assayID join instruments as i on i.instrumentID=s.instrumentID \
where i.instrumentName="nextseq" and a.assayName="heme" order by s.runID desc limit 2' -N  >> $FILE


mysql --user='' --password='' --database='ngs_live' --execute='select i.instrumentName,a.assayName,s.runID, \
s.callerID,s.coverageID,s.sampleName from samples as s join assays as a on s.assayID= a.assayID join instruments as i on i.instrumentID=s.instrumentID \
where i.instrumentName="proton" and a.assayName="gene50" order by s.runID desc limit 2' -N  >> $FILE

mysql --user='' --password='' --database='ngs_live' --execute='select i.instrumentName,a.assayName,s.runID, \
s.callerID,s.coverageID,s.sampleName from samples as s join assays as a on s.assayID= a.assayID join instruments as i on i.instrumentID=s.instrumentID \
where i.instrumentName="proton" and a.assayName="neuro" and CHAR_LENGTH(s.runID)>2 order by s.runID desc limit 2' -N  >>	$FILE
