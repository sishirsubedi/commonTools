import sys
import pandas as pd
import numpy as np

FILE1=sys.argv[1] #hh
FILE2=sys.argv[2] #server
OUTFILE=sys.argv[3] #outfile

df_1= pd.read_csv(FILE1,header=None, delim_whitespace=True)
df_1.columns=['checksum','bytes','fname_serv1']

df_2= pd.read_csv(FILE2,header=None, delim_whitespace=True)
df_2.columns=['checksum','bytes','fname_serv2']

df_join=pd.merge(df_1,df_2,on=['checksum','bytes'],how='outer',indicator=True)
df_join.columns=['Checksum','Size','Filename_Server_HH','Filename_Server_2','Match']
df_join.to_csv(OUTFILE,sep='\t',index=False)
