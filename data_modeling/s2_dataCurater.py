import sys
import re
import pandas as pd
import basemodel as bm
from sklearn.preprocessing import OneHotEncoder, Imputer

def getHQFeatures(df_colcount,total_rows,percent_th = 0.30):
    df_colcount.reset_index(inplace=True)
    df_colcount.columns=['features','empty_rows_count']
    return df_colcount[df_colcount.empty_rows_count<=int(percent_th * total_rows)]['features'].values

df = pd.read_csv(sys.argv[1],low_memory=False)

## remove columns with high missing data
passed_cols = getHQFeatures(pd.DataFrame(df.isnull().sum()),df.shape[0])
df_hqf = df[passed_cols]

##remove any rows with no PTH values
df_hqf = df_hqf[df_hqf['PTH'].isnull()==False]

### remove calcium <= 10.4 ---METHOD 2
df_hqf = df_hqf[df_hqf['CA']>10.4]

##impute categorical race with the most frequent race
df_hqf.ix[df_hqf.RACE.isnull(),'RACE']='C'

### fill all categorical values with missing data with mean
df_hqf.fillna(df_hqf.mean(),inplace=True)

## encode categorical values
df_impute = pd.get_dummies(df_hqf.ix[:,['SEX','RACE']])

for nf in df_impute.columns:
    df_hqf[nf] = df_impute[nf]

df_hqf.drop(['SEX','RACE'],axis=1,inplace=True)

feature_columns = [x for x in df_hqf.columns if x not in ['MRN','PTH']]
cor_feat = bm.correlation_info(df_hqf[feature_columns],0.8,1,0)
df_hqf = df_hqf[df_hqf.columns.difference(cor_feat)]
df_hqf.to_csv("d3_method2_final_datamat.csv",index=False)
