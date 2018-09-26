import sys
import os
import glob
import optparse
import pandas as pd

def compare(instrument,runID,variantcaller,coveragecaller, sample):

    environment = 'ngs_test'
    result = []
    result.append(['----', '----', '----'])

    result.append(['instrument:',instrument])
    result.append(['runID:',runID])
    result.append(['variantcaller:',variantcaller])
    result.append(['coveragecaller',coveragecaller])
    result.append(['sample:',sample])


    # for r in result: print(r)

    file_v1_coverage = ''
    file_v1_amplicon = ''
    file_v2_coverage = ''
    file_v2_amplicon = ''

    if instrument == 'proton':
        file_v1_amplicon = glob.glob(os.path.join('/home', instrument + 'Analysis', '*_' + runID, coveragecaller, sample, 'amplicon.filter.txt'))
        file_v1_coverage = glob.glob(os.path.join('/home', instrument + 'Analysis', '*_' + runID, variantcaller, sample, 'TSVC_variants.split.vep.parse.newVarView.txt'))
        file_v2_amplicon = glob.glob(os.path.join('/home', 'environments', environment, instrument + 'Analysis', '*_' + runID, sample, coveragecaller,'amplicon.filter.txt'))
        file_v2_coverage = glob.glob(os.path.join('/home', 'environments', environment, instrument + 'Analysis', '*_' + runID, sample, variantcaller,'TSVC_variants.split.vep.parse.newVarView.txt'))
    elif instrument == 'miseq':
        file_v1_amplicon = glob.glob(os.path.join('/home', instrument + 'Analysis', '*_'+runID+'_*', sample+'.amplicon.txt'))
        file_v1_coverage = glob.glob(os.path.join('/home', instrument + 'Analysis', '*_'+runID+'_*', sample+ '.amplicon.vep.parse.txt'))
        file_v2_amplicon = glob.glob(os.path.join('/home', 'environments', environment, instrument + 'Analysis', '*_' + runID + '_*', sample, sample+'.amplicon.txt'))
        file_v2_coverage = glob.glob(os.path.join('/home', 'environments', environment, instrument + 'Analysis',  '*_' + runID + '_*', sample, sample+'.amplicon.vep.parse.txt'))
    elif instrument == 'nextseq':
        file_v1_amplicon = glob.glob(os.path.join('/home', instrument + 'Analysis', '*_'+runID+'_*', sample+'.amplicon.txt'))
        file_v1_coverage = glob.glob(os.path.join('/home', instrument + 'Analysis', '*_'+runID+'_*', sample+ '.amplicon.vep.parse.txt'))
        file_v2_amplicon = glob.glob(os.path.join('/home', 'environments', environment, instrument + 'Analysis', '*_' + runID + '_*', sample, 'variantAnalysis', sample+'.amplicon.txt'))
        file_v2_coverage = glob.glob(os.path.join('/home', 'environments', environment, instrument + 'Analysis',  '*_' + runID + '_*', sample,'variantAnalysis', sample+'.amplicon.vep.parse.txt'))

    # print('running')
    # print('old amplicon file ')
    # print(file_v1_amplicon)
    # print('old coverage file ')
    # print(file_v1_coverage)
    # print('new amplicon file ')
    # print(file_v2_amplicon)
    # print('new coverage file ')
    # print(file_v2_coverage)


    df_file_v1_coverage = pd.read_csv(file_v1_coverage[0], header=None, sep='\t')

    if instrument =='nextseq':
        df_file_v2_coverage = pd.read_csv(file_v2_coverage[0], header=0, sep='\t')
    else:
        df_file_v2_coverage = pd.read_csv(file_v2_coverage[0], header=None, sep='\t')

    if instrument =='proton' or instrument =='miseq':
        df_file_v1_amplicon = pd.read_csv(file_v1_amplicon[0], header=0, sep='\t')
        df_file_v2_amplicon = pd.read_csv(file_v2_amplicon[0], header=0, sep='\t')
    else:
        df_file_v1_amplicon = pd.read_csv(file_v1_amplicon[0], header=None, sep='\t')
        df_file_v2_amplicon = pd.read_csv(file_v2_amplicon[0], header=None, sep='\t')


    # print(df_file_v1_amplicon.head())
    # print(df_file_v2_amplicon.head())
    # print(df_file_v1_coverage.head())
    # print(df_file_v2_coverage.head())

    ## get total amplicons and variants count

    result.append(['Version: ', ' Ver-2 ', ' Ver-3 '])

    result.append(['Total Amplicons:',df_file_v1_amplicon.shape[0],df_file_v2_amplicon.shape[0]])
    if instrument != 'proton':
        result.append(['Total Amplicons>100:', df_file_v1_amplicon[df_file_v1_amplicon.iloc[:,1]>100].shape[0], df_file_v1_amplicon[df_file_v1_amplicon.iloc[:,1]>100].shape[0]])
    else:
        result.append(['Total Amplicons>RD-100:', df_file_v1_amplicon[df_file_v1_amplicon.iloc[:,9]>100].shape[0], df_file_v1_amplicon[df_file_v1_amplicon.iloc[:,9]>100].shape[0]])

    result.append(['Total Variants:', df_file_v1_coverage.shape[0], df_file_v2_coverage.shape[0]])

    match = 0
    for ind,row in df_file_v1_coverage.iterrows():
        match2 = df_file_v2_coverage[ (df_file_v2_coverage[0] == row[0]) & (df_file_v2_coverage[2] == row[2])& (df_file_v2_coverage[3] == row[3]) & (df_file_v2_coverage[4] == row[4]) & (df_file_v2_coverage[5] == row[5]) & (df_file_v2_coverage[6] == row[6])]
        if (len(match2.index)==1):
            match+=1

    result.append(['Variants Match:', match])


    result.append(['Total Genes:' , len(df_file_v1_coverage.iloc[:,0].unique()),len(df_file_v2_coverage.iloc[:, 0].unique())])

    f1_genes = df_file_v1_coverage.iloc[:,0].unique()
    f2_genes = df_file_v2_coverage.iloc[:, 0].unique()

    result.append(['Genes Match:' ,len([x for x in f1_genes if x in f2_genes])])

    classification = df_file_v1_coverage.iloc[:, 6].unique()

    result.append(['Total HIGH:', df_file_v1_coverage[df_file_v1_coverage.iloc[:,6]=='HIGH'].shape[0], df_file_v2_coverage[df_file_v2_coverage.iloc[:,6]=='HIGH'].shape[0]])
    result.append(['Total MODERATE:', df_file_v1_coverage[df_file_v1_coverage.iloc[:, 6] == 'MODERATE'].shape[0],df_file_v2_coverage[df_file_v2_coverage.iloc[:, 6] == 'MODERATE'].shape[0]])
    result.append(['Total LOW:', df_file_v1_coverage[df_file_v1_coverage.iloc[:,6]=='LOW'].shape[0], df_file_v2_coverage[df_file_v2_coverage.iloc[:,6]=='LOW'].shape[0]])


    result.append(['----','----','----'])

    df_result = pd.DataFrame(result)
    df_result.to_csv('TestResults.txt',sep='\t',index=False,header=False, mode = 'a')


if len(sys.argv) > 1:
    parser = optparse.OptionParser()
    parser.add_option('-i', '--instrument')
    parser.add_option('-r', '--runID')
    parser.add_option('-v', '--variant_caller_ID')
    parser.add_option('-c', '--coverage_caller_ID')
    parser.add_option('-s', '--sample_Name')
    options,args = parser.parse_args()
    instrument = options.instrument
    runID = options.runID
    variantcaller = options.variant_caller_ID
    coveragecaller = options.coverage_caller_ID
    sample = options.sample_Name.strip()

    # print('instrument:',instrument)
    # print('runID:',runID)
    # print('variantcaller:',variantcaller)
    # print('coveragecaller',coveragecaller)
    # print('sample:',sample)

    compare(instrument,runID,variantcaller,coveragecaller, sample)

else:
    print("python 01_compareFiles.py -h for help")
