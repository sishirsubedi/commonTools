import sys
import os
import glob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import scipy.stats as st
from sklearn.cluster import KMeans


def get_result_files (f1):
    samples=[]
    in_file = open(f1,"r")
    for line in in_file:
        runid = line.split(',')[0]
        sample = line.split(',')[1].split('-')[0]
        tumor=sample+'-T'
        tumorpair=tumor+'_'+sample+'-N'
        fpath = glob.glob(os.path.join('/home', 'environments', 'ngs_validation', 'nextseqAnalysis', 'tmbAssay', '*_' + runid+ '_*', tumor, 'Paired',tumorpair,tumorpair+'.final_result.txt'))
        if len(fpath)>0:
            samples.append([runid,fpath[0]])
    in_file.close()
    return samples


file_runs = sys.argv[1]
samples=get_result_files(file_runs)


cols=[]
for line in open(samples[0][1],"r"):
    cols.append(line.split(',')[0])

rows=[]
runids=[]
for sample in samples:
    vals=[]
    runids.append(sample[0])
    for line in open(sample[1],"r"):
        sl = line.strip('\n').split(',')
        vals.append(sl[1])
    rows.append(vals)

df = pd.DataFrame(rows)
df.columns = cols
df.loc[:,'ExomeID'] = [x[0] for x in df['Sample'].str.split('-')]
df['TMB-Score'] = df['TMB-Score'].astype(float)
df['varscan-strelka'] = df['varscan-strelka'].astype(float)
df['varscan-mutect'] = df['varscan-mutect'].astype(float)
df['mutect-strelka'] = df['mutect-strelka'].astype(float)
df['varscan-strelka-mutect'] = df['varscan-strelka-mutect'].astype(float)
df['TMB-Total-Variants'] = df['TMB-Total-Variants'].astype(float)
df['RunID'] = runids

#### combine metadata
df_meta = pd.read_csv("tmb_metadata.csv")
df_meta.loc[:,'TMB-Foundation-Group'] = [x[0] for x in df_meta['TMB'].str.split(';')]
df_meta.loc[:,'TMB-Foundation-Score'] = [x[1] for x in df_meta['TMB'].str.split(';')]
df_meta.loc[:,'TMB-Foundation-Value'] = [float(x[1]) for x in df_meta['TMB-Foundation-Score'].str.split(' ')]
df_meta.loc[:,'Sample-Age'] = [int(x[0]) for x in df_meta['Age'].str.split(' ')]
df_meta.loc[:,'Sample-Tumor'] = [str(x[0]) for x in df_meta['Tumor Type'].str.split(' ')]

df_join = pd.merge(df,df_meta,on=['ExomeID'],how='left',indicator=False)

##output result
df_join.to_csv("tmb_validation_samples_all.csv",index=False)


##### analysis plots #######
#### general info
ax1 = plt.subplot2grid((3, 2), (0, 0))
ax2 = plt.subplot2grid((3, 2), (0, 1))
ax3 = plt.subplot2grid((3, 2), (1, 0), colspan=2)
ax4 = plt.subplot2grid((3, 2), (2, 0), colspan=2)
df_join.groupby('Race').count().reset_index()[['Race','Sample']].plot(x='Race',y='Sample',kind='barh',ax=ax1,rot=0,legend=False,figsize=(10,5))
df_join.groupby('Sex').count().reset_index()[['Sex','Sample']].plot(x='Sex',y='Sample',kind='barh',ax=ax2,rot=0,legend=False,figsize=(10,5))
df_join.groupby('Sample-Age').count().reset_index()[['Sample-Age','Sample']].plot.bar(x='Sample-Age',y='Sample',ax=ax3,rot=0,legend=False,figsize=(20,10))
df_join.groupby('Sample-Tumor').count().reset_index()[['Sample-Tumor','Sample']].plot.bar(x='Sample-Tumor',y='Sample',ax=ax4,rot=0,legend=False,figsize=(20,10))
plt.suptitle("Total Number of Runs-"+str(df_join.shape[0]))
plt.savefig("TMB_Foundation_General.png")
plt.close()

sns.regplot(x="TMB-Score", y="TMB-Foundation-Value", data=df_join,ci=None)
plt.title("TMB Score Comparisons,correlation: " + str(round(df_join['TMB-Score'].corr(df_join['TMB-Foundation-Value']),3)) )
plt.savefig("TMB_HMH_Foundation_ScatterPlot.png")
plt.close()

sns.regplot(x="TMB-Score", y="TMB-Total-Variants", data=df_join,ci=None)
plt.title("TMB Score Comparisons")
plt.savefig("TMB_HMH_Score_Variants_ScatterPlot.png")
plt.close()

sns.lineplot(x=range(df_join.shape[0]) ,y=df_join['TMB-Score'].sort_values(), marker="o",color='b',label="HMH")
sns.lineplot(x=range(df_join.shape[0]) ,y=df_join['TMB-Foundation-Value'].sort_values(), marker="o",color='r',label="Foundation")
plt.title("Total Number of Runs-"+str(df_join.shape[0]))
plt.xlabel("Runs")
plt.savefig("TMB_HMH_Foundation_Score_LinePlot.png")
plt.close()

sns.lineplot(x=range(df_join.shape[0]) ,y=df_join['TMB-Total-Variants'].sort_values(), marker="o",color='b',label="HMH")
plt.title("Total Number of Runs-"+str(df_join.shape[0]))
plt.xlabel("Runs")
plt.savefig("TMB_HMH_Variants_LinePlot.png")
plt.close()

kmeans = KMeans(n_clusters=3)
d_points=np.reshape(df_join['TMB-Score'],(-1,1))
kmeans.fit(d_points)
df_join['cluster'] = kmeans.fit_predict(d_points)
sns.scatterplot(x=range(df_join.shape[0]) ,y=df_join['TMB-Score'].sort_values(), hue="cluster", data=df_join,palette=['blue','red','green'])
# plt.title("Cluster Analysis, centers "+ " , ".join([ str(round(x[0],2)) for x in kmeans.cluster_centers_ ]))
plt.title("Cluster Analysis")
plt.xlabel(" Group cutoffs- (0,3.34) (3.35,9.15) (>9.15)")
plt.savefig("TMB_HMH_kmeans_score.png")
plt.close()
