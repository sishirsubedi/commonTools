#!/bin/bash
#PBS -l nodes=1:ppn=3
#PBS -l walltime=10:00:00
#PBS -q default
#PBS Error_Path=${PBS_JOBNAME}.err
#PBS Output_Path=${PBS_JOBNAME}.out
#PBS -k eo

RUNID=$1
EXOME1=$2
EXOME=$(echo "$EXOME1" | sed 's/\-//g')


HOME="/home/environments/ngs_test/nextseqAnalysis/exomeAnalysis/${RUNID}/"
SAMPLEPATH=$(find ${HOME}Paired/ -maxdepth 1 -type d  -name "${EXOME}*")
SAMPLE=$(basename $SAMPLEPATH)

NORMAL_SAMPLEPATH=$(find ${HOME}Single/ -maxdepth 1 -type d  -name "${EXOME}-N_*")
NORMAL_SAMPLE=$(basename $NORMAL_SAMPLEPATH)
NORMAL_BAM=$(find $NORMAL_SAMPLEPATH/Alignment/ -maxdepth 1 -type f  -name "${NORMAL_SAMPLE}.sorted.rmdups.bam")


TUMOR_SAMPLEPATH=$(find ${HOME}Single/ -maxdepth 1 -type d  -name "${EXOME}-T_*")
TUMOR_SAMPLE=$(basename $TUMOR_SAMPLEPATH)
TUMOR_BAM=$(find $TUMOR_SAMPLEPATH/Alignment/ -maxdepth 1 -type f  -name "${TUMOR_SAMPLE}.sorted.rmdups.bam")


SAMPLE_DIR="$SAMPLEPATH/"

ENVIRONMENT="test"
DEPTH="10"
NALF="10"
TALF="10"

# echo "
# $RUNID $SAMPLE
# "
#### remove all the output files
find ${SAMPLE_DIR}varscan/ -maxdepth 1 -type f  -name "${SAMPLE}*" -exec rm {} \;
find ${SAMPLE_DIR}mutect/ -maxdepth 1 -type f  -name "${SAMPLE}*" -exec rm {} \;
find ${SAMPLE_DIR}strelka/ -maxdepth 1 -type f  -name "${SAMPLE}*" -exec rm {} \;
find ${SAMPLE_DIR}/ -maxdepth 1 -type f  -name "${SAMPLE}*" -exec rm {} \;


echo "
$SAMPLE
$REF_GENOME_1
$NORMAL_BAM
$TUMOR_BAM
${SAMPLE_DIR}
$ENVIRONMENT
$DEPTH
$NALF
$TALF
"

###Run specific programs
REF_GENOME_1="/home/doc/ref/ref_genome/ucsc.hg19.fasta"
REF_GENOME_2="/home/doc/ref/ref_genome/Homo_sapiens.GRCh37.73.dna_sm.primary_assembly.fa"
DIR_SCRIPT="/home/pipelines/ngs_test/"

bash ${DIR_SCRIPT}shell/tmb_VCaller_varscan.sh $SAMPLE $REF_GENOME_1  $NORMAL_BAM  $TUMOR_BAM  ${SAMPLE_DIR}varscan/  $ENVIRONMENT  $DEPTH  $NALF  $TALF

/opt/python3/bin/python3 ${DIR_SCRIPT}python/tmb_parseVEP.py  "TEST" "$SAMPLE"  "$SAMPLE_DIR"  "$ENVIRONMENT"  "${DEPTH}_${NALF}_${TALF}"
