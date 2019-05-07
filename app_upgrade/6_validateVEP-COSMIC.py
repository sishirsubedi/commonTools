import sys
import os
import glob
import optparse
import pandas as pd
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

def getFile(instrument, assay, runID,variantcaller,coveragecaller, sample):

    env_valid='ngs_validation'
    env_live='ngs_live'

    file1= ''
    file2 = ''

    if instrument == 'proton':
        file1 = glob.glob(os.path.join('/home', 'environments', env_live, instrument + 'Analysis', '*_' + runID, sample, variantcaller,'TSVC_variants.split.vep.parse.newVarView.filter.txt'))
        file2 = glob.glob(os.path.join('/home', 'environments', env_valid, instrument + 'Analysis', '*_' + runID, sample, variantcaller,'TSVC_variants.filter.split.vep.parse.filter2.txt'))

    elif instrument == 'nextseq':
        file1 = glob.glob(os.path.join('/home', 'environments', env_live, instrument + 'Analysis',  '*_' + runID + '_*', sample,'variantAnalysis', sample+'.amplicon.vep.parse.filter.txt'))
        file2 = glob.glob(os.path.join('/home', 'environments', env_valid, instrument + 'Analysis',  '*_' + runID + '_*', sample,'variantAnalysis', sample+'.amplicon.vep.parse.filter.txt'))

    return (file1,file2)



def getCosmicInfo(chr,pos,ref,alt):
    present = []
    try:
        connection = mysql.connector.connect(host='localhost',database='ngs_test', user=USER, password=PASSWORD)
        cursor = connection.cursor(prepared=True)

        query = "select cosmicID from db_cosmic_grch37v86 where chr= %s and pos=%s and ref=%s and alt=%s"

        cursor.execute(query, (chr,pos,ref,alt))

        for row in cursor:
            res = [el.decode('utf-8') if type(el) is bytearray else el for el in row]
            present.append(res[0])

    except mysql.connector.Error as error :
        print("Failed to update record to database:{}".format(error))
        connection.rollback()

    finally:
        if(connection.is_connected()):
            connection.close()

    return present


def addCosmic(df):
    cosmic=[]
    for indx,row in df.iterrows():
        chr = row[2]
        pos = row[3]
        ref = row[4]
        alt = row[5]
        cosmic.append(getCosmicInfo(chr,pos,ref,alt))
    df['cosmicIDs'] = cosmic

if len(sys.argv) > 1:
    parser = optparse.OptionParser()
    parser.add_option('-u', '--user')
    parser.add_option('-p', '--password')
    parser.add_option('-i', '--instrument')
    parser.add_option('-a', '--assay')
    parser.add_option('-r', '--runID')
    parser.add_option('-v', '--variant_caller_ID')
    parser.add_option('-c', '--coverage_caller_ID')
    parser.add_option('-s', '--sample_Name')
    options,args = parser.parse_args()
    USER = options.user
    PASSWORD = options.password
    instrument = options.instrument
    assay = options.assay
    runID = options.runID
    variantcaller = options.variant_caller_ID
    coveragecaller = options.coverage_caller_ID
    sample = options.sample_Name.strip()

    print('instrument,'+instrument)
    print('runID,'+runID)
    print('variantcaller,'+variantcaller)
    print('coveragecaller,'+coveragecaller)
    print('sample,'+sample)


    files = getFile(instrument, assay, runID,variantcaller,coveragecaller, sample)
    file1 = files[0][0]
    file2 = files[1][0]


    print('file 3.1 is ,' + str(file1))
    print('file 3.2 is ,' + str(file2))

    df1 = pd.read_csv(file1,sep='\t',header=None)
    df2 = pd.read_csv(file2,sep='\t',header=None)

    df1.columns = ['gene','exon','chr','position','ref','alt','prediction','type','num','altfreq','readdp','altreaddp','consequence','sift','polyphen','hgvsc','hgvsp','dbsnpid','pubmed']
    df2.columns = ['gene','exon','chr','position','ref','alt','prediction','type','num','altfreq','readdp','altreaddp','consequence','sift','polyphen','hgvsc','hgvsp','dbsnpid','pubmed']

    addCosmic(df1)
    addCosmic(df2)

    for indx in range(0,df1.shape[0]):
        for colname in df1.columns[0:17]:
            if str(df1.ix[indx,colname]) != str(df2.ix[indx,colname]):
                print('hmvv3.1',',',df1.ix[indx,'chr'],',',df1.ix[indx,'position'],',',df1.ix[indx,'ref'],',',df1.ix[indx,'alt'],',',':',',',colname,',','--',',',df1.ix[indx,colname])
                print('hmvv3.2',',',df2.ix[indx,'chr'],',',df2.ix[indx,'position'],',',df2.ix[indx,'ref'],',',df2.ix[indx,'alt'],',',':',',',colname,',','--',',',df2.ix[indx,colname])


else:
    print("python 6_validateVEP-COSMIC.py -h for help")
