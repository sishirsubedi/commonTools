import sys
import os
import glob
import optparse
import pandas as pd

def compare(instrument, assay, runID,variantcaller,coveragecaller, sample):

    env_valid = 'ngs_validation'
    env_live  = 'ngs_live'
    result = []
    result.append(['----', '----', '----'])
    result.append(['instrument:',instrument])
    result.append(['assay:',assay])
    result.append(['runID:',runID])
    result.append(['variantcaller:',variantcaller])
    result.append(['coveragecaller',coveragecaller])
    result.append(['sample:',sample])

    file_v1_variant = ''
    file_v1_amplicon = ''
    file_v2_variant = ''
    file_v2_amplicon = ''

    if instrument == 'proton':
        file_v1_amplicon = glob.glob(os.path.join('/home', 'environments', env_live, instrument + 'Analysis', '*_' + runID, sample, coveragecaller,'amplicon.filter.v2.txt'))
        file_v1_variant = glob.glob(os.path.join('/home', 'environments', env_live, instrument + 'Analysis', '*_' + runID, sample, variantcaller,'TSVC_variants.split.vep.parse.newVarView.filter.txt'))
        file_v2_amplicon = glob.glob(os.path.join('/home', 'environments', env_valid, instrument + 'Analysis', '*_' + runID, sample, coveragecaller,'amplicon.filter.filter2.txt'))
        file_v2_variant = glob.glob(os.path.join('/home', 'environments', env_valid, instrument + 'Analysis', '*_' + runID, sample, variantcaller,'TSVC_variants.filter.split.vep.parse.filter2.txt'))
    elif instrument == 'nextseq':
        file_v1_amplicon = glob.glob(os.path.join('/home', 'environments', env_live, instrument + 'Analysis', '*_' + runID + '_*', sample, 'variantAnalysis', sample+'.amplicon.txt'))
        file_v1_variant = glob.glob(os.path.join('/home', 'environments', env_live, instrument + 'Analysis',  '*_' + runID + '_*', sample,'variantAnalysis', sample+'.amplicon.vep.parse.filter.txt'))
        file_v2_amplicon = glob.glob(os.path.join('/home', 'environments', env_valid, instrument + 'Analysis', '*_' + runID + '_*', sample, 'variantAnalysis', sample+'.amplicon.filter.filter2.filter3.txt'))
        file_v2_variant = glob.glob(os.path.join('/home', 'environments', env_valid, instrument + 'Analysis',  '*_' + runID + '_*', sample,'variantAnalysis', sample+'.filter.vep.parse.filter2.vcf'))

    print('running')
    print('old amplicon file ')
    print(file_v1_amplicon)
    print('old variant file ')
    print(file_v1_variant)
    print('new amplicon file ')
    print(file_v2_amplicon)
    print('new variant file ')
    print(file_v2_variant)



    df_file_v1_variant = pd.read_csv(file_v1_variant[0], header=None, sep='\t')
    df_file_v2_variant = pd.read_csv(file_v2_variant[0], header=None, sep='\t')


    result.append(['Version: ', ' Ver-3.1 ', ' Ver-3.2 '])

    if os.stat(file_v1_amplicon[0]).st_size == 0 or  os.stat(file_v2_amplicon[0]).st_size == 0:
        result.append(['Amplicons file empty' ])
    else:
        if instrument =='proton':
            df_file_v1_amplicon = pd.read_csv(file_v1_amplicon[0], header=None, sep='\t')
            df_file_v2_amplicon = pd.read_csv(file_v2_amplicon[0], header=None, sep='\t')
        else:
            df_file_v1_amplicon = pd.read_csv(file_v1_amplicon[0], header=None, sep='\t')
            df_file_v2_amplicon = pd.read_csv(file_v2_amplicon[0], header=None, sep='\t')


    result.append(['Total Amplicons:',df_file_v1_amplicon.shape[0],df_file_v2_amplicon.shape[0]])
    result.append(['Total Variants:', df_file_v1_variant.shape[0], df_file_v2_variant.shape[0]])

    match = 0
    for ind,row in df_file_v1_variant.iterrows():
        match2 = df_file_v2_variant[ (df_file_v2_variant[0] == row[0]) & (df_file_v2_variant[2] == row[2])& (df_file_v2_variant[3] == row[3]) & (df_file_v2_variant[4] == row[4]) & (df_file_v2_variant[5] == row[5]) & (df_file_v2_variant[6] == row[6])]
        if (len(match2.index)==1):
            match+=1

    result.append(['Variants Match:', match])
    result.append(['Total Genes:' , len(df_file_v1_variant.iloc[:,0].unique()),len(df_file_v2_variant.iloc[:, 0].unique())])

    f1_genes = df_file_v1_variant.iloc[:,0].unique()
    f2_genes = df_file_v2_variant.iloc[:, 0].unique()

    result.append(['Genes Match:' ,len([x for x in f1_genes if x in f2_genes])])
    classification = df_file_v1_variant.iloc[:, 6].unique()
    result.append(['Total HIGH:', df_file_v1_variant[df_file_v1_variant.iloc[:,6]=='HIGH'].shape[0], df_file_v2_variant[df_file_v2_variant.iloc[:,6]=='HIGH'].shape[0]])
    result.append(['Total MODERATE:', df_file_v1_variant[df_file_v1_variant.iloc[:, 6] == 'MODERATE'].shape[0],df_file_v2_variant[df_file_v2_variant.iloc[:, 6] == 'MODERATE'].shape[0]])
    result.append(['----','----','----'])
    print(result)
    df_result = pd.DataFrame(result)
    df_result.to_csv('validationResults.txt',sep='\t',index=False,header=False, mode = 'a')


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

    print('instrument:'+instrument+':')
    print('runID:'+runID+':')
    print('variantcaller:'+variantcaller+':')
    print('coveragecaller:'+coveragecaller+':')
    print('sample:'+sample+':')

    compare(instrument, assay, runID,variantcaller,coveragecaller, sample)

else:
    print("python 5_validateAnalysis.py -h for help")
