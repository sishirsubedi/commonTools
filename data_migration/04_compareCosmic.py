import sys
import os
import glob
import optparse
import pandas as pd

def compare(instrument, assay, runID,variantcaller,coveragecaller, sample):

    environment = 'ngs_validation'
    result = []

    file_v2_coverage = ''

    if instrument == 'proton':
        file_v2_coverage = glob.glob(os.path.join('/home', 'environments', environment, instrument + 'Analysis', '*_' + runID, sample, variantcaller,'TSVC_variants.split.vep.parse.newVarView.filter.txt'))
    elif instrument == 'miseq':
        file_v2_coverage = glob.glob(os.path.join('/home', 'environments', environment, instrument + 'Analysis',  '*_' + runID + '_*', sample, sample+'.amplicon.vep.parse.filter.txt'))
    elif instrument == 'nextseq':
        file_v2_coverage = glob.glob(os.path.join('/home', 'environments', environment, instrument + 'Analysis',  '*_' + runID + '_*', sample,'variantAnalysis', sample+'.amplicon.vep.parse.filter.txt'))

    print('running')
    print('new coverage file ')
    print(file_v2_coverage)


    df_file_v2_coverage = pd.read_csv(file_v2_coverage[0], header=None, sep='\t')
    df_file_v2_coverage = df_file_v2_coverage.iloc[:,[2,3,4,5]]
    df_file_v2_coverage.columns=['chr','pos', 'ref','alt']

    df_cosmic82 = pd.read_csv('/home/hhadmin/hmvv_validation/cosmic_82.txt', sep='\t')

    df_cosmic86 = pd.read_csv('/home/hhadmin/hmvv_validation/cosmic_86.txt', sep='\t')


    df_join1 = pd.merge(df_file_v2_coverage,df_cosmic82,on=['chr','pos', 'ref','alt'], how='left')
    df_join2 = pd.merge(df_join1,df_cosmic86,on=['chr','pos', 'ref','alt'], how='left')
    df_join2.columns=['chr','pos', 'ref','alt','v82','v86']
    df_join2.dropna(inplace=True)

    v82_uniq=df_join2['v82'].unique()
    v86_uniq=df_join2['v86'].unique()
    result.append([instrument,assay,runID,sample,df_join2.shape[0], len(v82_uniq),len(v86_uniq),[x for x in v82_uniq if x not in v86_uniq ],[x for x in v86_uniq if x not in v82_uniq ] ])


    df_result = pd.DataFrame(result)
    df_result.to_csv('04_cosmicResults.txt',sep='\t',index=False,header=False, mode = 'a')


if len(sys.argv) > 1:
    parser = optparse.OptionParser()
    parser.add_option('-i', '--instrument')
    parser.add_option('-a', '--assay')
    parser.add_option('-r', '--runID')
    parser.add_option('-v', '--variant_caller_ID')
    parser.add_option('-c', '--coverage_caller_ID')
    parser.add_option('-s', '--sample_Name')
    options,args = parser.parse_args()
    instrument = options.instrument
    assay = options.assay
    runID = options.runID
    variantcaller = options.variant_caller_ID
    coveragecaller = options.coverage_caller_ID
    sample = options.sample_Name.strip()

    # print('instrument:'+instrument+':')
    # print('runID:'+runID+':')
    # print('variantcaller:'+variantcaller+':')
    # print('coveragecaller:'+coveragecaller+':')
    # print('sample:'+sample+':')

    compare(instrument, assay, runID,variantcaller,coveragecaller, sample)

else:
    print("python 04_compareCosmic.py -h for help")
