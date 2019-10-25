import sys
import re
import pandas as pd
import basemodel as bm
from sklearn.preprocessing import OneHotEncoder, Imputer

def getHQFeatures(df_colcount,total_rows,percent_th = 0.25):
    df_colcount.reset_index(inplace=True)
    df_colcount.columns=['features','empty_rows_count']
    return df_colcount[df_colcount.empty_rows_count<=int(percent_th * total_rows)]['features'].values

df = pd.read_csv(sys.argv[1],low_memory=False)

## remove columns with high missing data
passed_cols = getHQFeatures(pd.DataFrame(df.isnull().sum()),df.shape[0])
df_hqf = df[passed_cols]
##remove any rows with no PTH values
df_hqf = df_hqf[df_hqf['PTH'].isnull()==False]
##impute categorical race with the most frequent race
df_hqf.ix[df_hqf.RACE.isnull(),'RACE']='C'
### fill all categorical values with missing data with mean
df_hqf.fillna(df_hqf.mean(),inplace=True)
## encode categorical values
df_impute = pd.get_dummies(df_hqf.ix[:,['SEX','RACE']])

for nf in df_impute.columns:
    df_hqf[nf] = df_impute[nf]

df_hqf = df_hqf[['MRN', 'AGE',
                'SEX_F', 'SEX_M', 'SEX_N', 'RACE_A', 'RACE_B', 'RACE_C', 'RACE_D',
                'RACE_H', 'RACE_I', 'RACE_O', 'RACE_S', 'RACE_Z','AAGRF', 'AGRAT', 'ALB', 'ALP', 'ALT',
                'AST', 'BASOA', 'BASOR', 'BILIT', 'BUN', 'CA', 'CL', 'CO2', 'CREAT',
                'EOSA', 'EOSAB', 'EOSR', 'GLU', 'HCTI', 'HGBI', 'IGRAN', 'K', 'LYMPA',
                'LYMPR', 'MCH', 'MCHC', 'MCV', 'MONOA', 'MONOR', 'MPV', 'NAGRF', 'NEUA',
                'NEUR', 'NRBCA', 'PLTI', 'RBC', 'RDWSD', 'SODIUM', 'TP', 'WBCI', 'PTH'
                ]]

cor_feat = bm.correlation_info(df_hqf.iloc[:,1:df_hqf.shape[0]-1],0.8,1,1)
df_hqf = df_hqf[df_hqf.columns.difference(cor_feat)]
df_hqf.to_csv("final_datamat.csv",index=False)
