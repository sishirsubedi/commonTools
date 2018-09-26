import sys
import os
import glob
import optparse
import pandas as pd

def loadAmplicons(instrument,runID,variantcaller,coveragecaller, sampleID, sampleName):

    print('--------')

    print('instrument:',instrument)
    print('runID:',runID)
    print('variantcaller:',variantcaller)
    print('coveragecaller',coveragecaller)
    print('sampleID:',sampleID)
    print('sampleName:',sampleName)


    file_v1_amplicon = ''
    file_v1_amplicon_filtered =''

    if instrument == 'proton':
        file_v1_amplicon = glob.glob(os.path.join('/home', instrument + 'Analysis', '*_' + runID, coveragecaller, sampleName, 'amplicon.filter.txt'))
    elif instrument == 'miseq':
        file_v1_amplicon = glob.glob(os.path.join('/home', instrument + 'Analysis', '*_'+runID+'_*', sampleName+'.amplicon.txt'))
    elif instrument == 'nextseq':
        file_v1_amplicon = glob.glob(os.path.join('/home', instrument + 'Analysis', '*_'+runID+'_*', sampleName+'.amplicon.txt'))



    print('running')
    print('old amplicon file is ' + str(file_v1_amplicon))
    file_v1_amplicon_filtered =str(file_v1_amplicon[0]).replace(".txt", ".v2.txt")
    print('new filtered amplicon file is ' + file_v1_amplicon_filtered)

    if instrument == 'proton':
        df_amplicon = pd.read_csv(file_v1_amplicon[0], sep="\t", header=0)
        df_amplicon = df_amplicon[['contig_id', 'contig_srt', 'contig_end','region_id','attributes','total_reads']]
        df_amplicon['ampliconName'] = (df_amplicon['region_id'].astype(str) + '.' +
                        df_amplicon['contig_id'].astype(str) + '.' +
                        df_amplicon['contig_srt'].astype(str) + '.' +
                        df_amplicon['contig_end'].astype(str) + '.' +
                        df_amplicon['attributes'].astype(str) )
        df_amplicon = df_amplicon[['ampliconName','total_reads','region_id']]
        df_amplicon.columns = ['ampliconName','readDepth','gene']
        df_amplicon['sampleID'] = sampleID
        df_amplicon = df_amplicon[['sampleID','gene','ampliconName','readDepth']]
        df_amplicon.to_csv(file_v1_amplicon_filtered, sep='\t', index=False, header=False)


    elif instrument == 'miseq':
        df_amplicon = pd.read_csv(file_v1_amplicon[0], sep="\t", header=None, skiprows=1)
        df_amplicon.columns = ['ampliconName','readDepth']
        df_amplicon['gene'] = [x.split('.')[0] for x in df_amplicon['ampliconName'].values]
        df_amplicon['sampleID'] = sampleID
        df_amplicon = df_amplicon[['sampleID','gene','ampliconName','readDepth']]
        df_amplicon.to_csv(file_v1_amplicon_filtered, sep='\t', index=False, header=False)

    elif instrument == 'nextseq':
        df_amplicon = pd.read_csv(file_v1_amplicon[0], sep="\t", header=None)
        df_amplicon.columns = ['ampliconName','readDepth']
        df_amplicon['gene'] = [x.split('.')[0] for x in df_amplicon['ampliconName'].values]
        df_amplicon['sampleID'] = sampleID
        df_amplicon = df_amplicon[['sampleID','gene','ampliconName','readDepth']]
        df_amplicon.to_csv(file_v1_amplicon_filtered, sep='\t', index=False, header=False)


if len(sys.argv) > 1:
    parser = optparse.OptionParser()
    parser.add_option('-i', '--instrument')
    parser.add_option('-r', '--runID')
    parser.add_option('-v', '--variant_caller_ID')
    parser.add_option('-c', '--coverage_caller_ID')
    parser.add_option('-d', '--sample_ID')
    parser.add_option('-s', '--sample_Name')
    options,args = parser.parse_args()
    instrument = options.instrument
    runID = options.runID
    variantcaller = options.variant_caller_ID
    coveragecaller = options.coverage_caller_ID
    sampleID = options.sample_ID
    sampleName = options.sample_Name.strip()

    loadAmplicons(instrument,runID,variantcaller,coveragecaller, sampleID, sampleName)

else:
    print("python 03_filterAmplicons.py -h for help")
