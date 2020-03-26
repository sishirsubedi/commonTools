import sys
import pandas as pd
import basemodel as bm

######## generate table describing main features ---
df = pd.read_csv("d3_after_impute_final_datamat.csv",low_memory=False)

df_xmat = df[[x for x in df.columns if x not in ['PTH','MRN','max_PTH','min_PTH','last_PTH']]]
main_features =  [ x for x in df_xmat.columns if '_' not in x ]
df_xmat = df_xmat[main_features]

info = pd.DataFrame()
info ['testResultCode'] = main_features

df_testCodes = pd.read_csv("TestCodes.csv")
df_testCodes = df_testCodes[ ['testResultCode','testResultName']]
join = pd.merge(info,df_testCodes,on='testResultCode',how='left',indicator=True)
join.drop_duplicates(['testResultCode','testResultName'],keep='first',inplace=True)
info['test code'] = join['testResultCode'].values
info['test name'] = join['testResultName'].values
info['median'] = [round(x,2) for x in df_xmat.median()]
info['qr_25'] = [round(x,2) for x in df_xmat.quantile(.25)]
info['qr_75'] = [round(x,2) for x in df_xmat.quantile(.75)]
info['qr'] = [str(x)+'-'+str(y) for x,y in zip(info['qr_25'].values,info['qr_75'].values)]
info['Median (IQR)'] = [str(x)+' ('+str(y)+')' for x,y in zip(info['median'].values,info['qr'].values)]

df_missing = pd.read_csv("d2_before_impute_final_datamat.csv",low_memory=False)
info['Missing %'] = [int(round((x/df_missing.shape[0]),2)*100) for x in df_missing[main_features].isnull().sum()]
info = info[['test code','test name','Missing %','Median (IQR)']]
info.to_csv("paper_data_feature_description.csv",index=False)
#########################################################



#############correlation plot 
df = pd.read_csv("d3_after_impute_final_datamat.csv",low_memory=False)

df_xmat = df[[x for x in df.columns if x not in ['MRN','max_PTH','min_PTH','last_PTH']]]
main_features =  [ x for x in df_xmat.columns if '_' not in x ]
df_xmat = df_xmat[main_features]
bm.correlation_info(df_xmat,0.9,0,1)
