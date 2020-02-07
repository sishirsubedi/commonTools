import pandas as pd
import sys
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

blood_samples= ['NA12878','Exome16', 'Exome17', 'Exome18', 'Exome34', 'Exome36', 'Exome38', 'Exome41', 'Exome42', 'Exome43', 'Exome44', 'Exome46', 'Exome8']

df_low=pd.DataFrame()
result = {}
for sample in blood_samples:
    file_in = "exome_samples/"+sample+"-N.cardiac_result.txt"
    df = pd.read_csv(file_in,sep='\t')
    print (sample)
    print("Total genes", len(df['Gene'].unique()))
    print("Total high genes", len(df[df['cov_status']=="high"]['Gene'].unique()))
    df = df[df['cov_status']=="low"]
    df['sample'] = sample
    df_low = pd.concat([df_low,df])
    genes = df['Gene'].unique()
    for gene in genes:
        if gene not in result.keys():
            result[gene] = [sample]
        else:
            result[gene].append(sample)

df_low.to_csv("Low_coverage.csv",index=False)
plt.figure(figsize=(20,10))
plt.bar([x for x in result.keys()],[len(x) for x in result.values()])
plt.savefig("coverage_overview.png");plt.close()
