import zipfile
import sys
import re
import pandas as pd
from datetime import datetime

def checkTestResult(x):
    valid = False
    if (bool(re.match('^[0-9_._>_<]*$', x))):
        valid = True
        if(bool(re.match('[..]',x))):
            return (False,x)
        elif(bool(re.match('[>|<]',x))):
            xdelta = float(re.sub('[>|<]','',x))
            return (valid,xdelta)
        else:
            return (valid, float(x))
    else:
        return (valid,x)

def extractFeature(infile):

    df = pd.read_excel(infile)

    df = df[['mrn', 'dateOfBirth', 'sex', 'race', 'testResultCode',
           'testResultName', 'collectDate', 'testResult']]

    ## change sodium code because it is Na which is marked as NaN and skipped later
    df.ix[df['testResultName']=="Sodium",['testResultCode']]="SODIUM"
    df.sort_values(by='collectDate',inplace=True)

    ### if we want to take the newest recording
    # pth_row = df[df['testResultCode']=="PTH"].iloc[df[df['testResultCode']=="PTH"].shape[0]-1,:]

    ### if we want to take the oldest recording
    pth_row = df[df['testResultCode']=="PTH"].iloc[0,:]


    patient_age = datetime.strptime(str(pth_row['collectDate']),'%Y%m%d').year - datetime.strptime(str(pth_row['dateOfBirth']),'%Y%m%d').year

    ## remove newer rows than pth date
    df = df[df['collectDate'] <= pth_row['collectDate'] ]

    invalid_result=[]
    for indx,row in df.iterrows():
        try:
            check_res = checkTestResult(row['testResult'])
            if(check_res[0]):
                df.ix[indx,['testResult']] = check_res[1]
            else:
                invalid_result.append(indx)
        except:
            sys.stderr.write("Feature result could not identify"); continue


    df.drop(invalid_result,inplace=True)

    df['testResult'] = df['testResult'].astype(float)

    ## get average of testResults
    patient_features = df.groupby(['testResultCode'])['testResult'].mean().reset_index()

    final_features=[]
    final_features.append(['MRN',pth_row['mrn']])
    final_features.append(['AGE',patient_age])
    final_features.append(['SEX',pth_row['sex']])
    final_features.append(['RACE',pth_row['race']])

    for indx,row in patient_features.iterrows():
        final_features.append([row['testResultCode'],row['testResult']])

    df_final_features= pd.DataFrame(final_features)
    df_final_features.columns=['Features','Values']

    # df_final_features.to_csv(str(pth_row['mrn'])+".csv",index=False,header=False)

    return df_final_features

def addRow(df_datamatrix, df_sample):

    if (df_datamatrix.shape[0]==0):

        df_datamatrix = df_datamatrix.append(df_sample['Values'].T)
        df_datamatrix.reset_index(drop=True,inplace=True)
        df_datamatrix.columns = df_sample['Features'].values

    else:
        new_features = [x for x in df_sample['Features'].values if x not in df_datamatrix.columns.values]
        common_features = [x for x in df_sample['Features'].values if x not in new_features]

        new_row = df_datamatrix.shape[0]

        for cf in common_features:
            df_datamatrix.ix[new_row,cf] =  df_sample[df_sample['Features']==cf]['Values'].values[0]

        for nf in new_features:
            df_datamatrix.ix[new_row,nf] =  df_sample[df_sample['Features']==nf]['Values'].values[0]

    return df_datamatrix

df_datamatrix = pd.DataFrame()


### input as text file with file names
# with open(sys.argv[1]) as fp:
#    line = fp.readline().strip()
#    while line:
#        print("processing..."+ str(line))
#        df_sample = extractFeature(line)
#        df_datamatrix = addRow(df_datamatrix,df_sample)
#        line = fp.readline().strip()
#


### input as zipped folder 
with zipfile.ZipFile(sys.argv[1], "r") as f:
    # cnt = 1
    for name in f.namelist():
        with f.open(name) as file:
           print("processing..."+ str(name))
           try:
               df_sample = extractFeature(file)
               ## need to update reference of datamatrix bc datamatrix is called but not initialized (line 101)
               df_datamatrix = addRow(df_datamatrix,df_sample)
           except:
               sys.stderr.write("Sample failed %s\n" % name); continue
           # cnt = cnt + 1
        # if cnt==10:
            # break

df_datamatrix.to_csv("Result_DataMatrix.csv",index=False)
