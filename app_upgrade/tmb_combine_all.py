import sys
import os
import glob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pylab
import pandas as pd
import seaborn as sns
import numpy as np
import scipy.stats as st
from statsmodels.nonparametric.kernel_regression import KernelReg
from sklearn.cluster import KMeans,AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.linear_model import LinearRegression
from sklearn.kernel_ridge import KernelRidge
from sklearn.metrics import r2_score
from scipy.cluster.hierarchy import dendrogram, linkage

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


def createdf(samples):

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

    ## modify columns
    df['RunID'] = runids
    df.loc[:,'ExomeID'] = [x[0] for x in df['Sample'].str.split('-')]
    df['TMB-Score'] = df['TMB-Score'].astype(float)
    df['varscan-strelka'] = df['varscan-strelka'].astype(float)
    df['varscan-mutect'] = df['varscan-mutect'].astype(float)
    df['mutect-strelka'] = df['mutect-strelka'].astype(float)
    df['varscan-strelka-mutect'] = df['varscan-strelka-mutect'].astype(float)
    df['TMB-Total-Variants-Raw']=df['varscan-strelka'].values + df['varscan-mutect'].values + df['mutect-strelka'].values + df['varscan-strelka-mutect'].values
    df['TMB-Total-Variants'] = df['TMB-Total-Variants'].astype(float)


    return df


def addMetadata(f):

    df_meta = pd.read_csv(f)
    df_meta.loc[:,'TMB-Foundation-Group'] = [x[0] for x in df_meta['TMB'].str.split(';')]
    df_meta.loc[:,'TMB-Foundation-Score'] = [x[1] for x in df_meta['TMB'].str.split(';')]
    df_meta.loc[:,'TMB-Foundation-Value'] = [float(x[1]) for x in df_meta['TMB-Foundation-Score'].str.split(' ')]
    df_meta.loc[:,'Sample-Age'] = [int(x[0]) for x in df_meta['Age'].str.split(' ')]
    df_meta.loc[:,'Sample-Tumor'] = [str(x[0]) for x in df_meta['Tumor Type'].str.split(' ')]

    df_join = pd.merge(df,df_meta,on=['ExomeID'],how='left',indicator=False)

    return df_join


def plot_generalInfo(df_join):
    ax1 = plt.subplot2grid((3, 2), (0, 0))
    ax2 = plt.subplot2grid((3, 2), (0, 1))
    ax3 = plt.subplot2grid((3, 2), (1, 0), colspan=2)
    ax4 = plt.subplot2grid((3, 2), (2, 0), colspan=2)
    df_join.groupby('Race').count().reset_index()[['Race','Sample']].plot(x='Race',y='Sample',kind='barh',ax=ax1,rot=0,legend=False,figsize=(10,5))
    df_join.groupby('Sex').count().reset_index()[['Sex','Sample']].plot(x='Sex',y='Sample',kind='barh',ax=ax2,rot=0,legend=False,figsize=(10,5))
    df_join.groupby('Sample-Age').count().reset_index()[['Sample-Age','Sample']].plot.bar(x='Sample-Age',y='Sample',ax=ax3,rot=0,legend=False,figsize=(20,10))
    df_join.groupby('Sample-Tumor').count().reset_index()[['Sample-Tumor','Sample']].plot.bar(x='Sample-Tumor',y='Sample',ax=ax4,rot=0,legend=False,figsize=(20,10))
    plt.suptitle("Total Number of Runs-"+str(df_join.shape[0]))
    plt.savefig("Fig_1_TMB_HMH_General.png")
    plt.close()

def plot_sequence_stats(df_join):

    print(df_join.head(2))

    df_join['Tumor_Total-Reads'] = df_join['Tumor_Total-Reads'].astype(int)/1000000
    df_join['Normal_Total-Reads'] = df_join['Normal_Total-Reads'].astype(int)/1000000

    df_join['Tumor_Coverage'] =  [int(x.replace('x','')) for x in df_join['Tumor_Coverage']]
    df_join['Normal_Coverage'] =  [int(x.replace('x','')) for x in df_join['Normal_Coverage']]

    for col in ['Tumor_Duplicate','Normal_Duplicate','Tumor_Coverage-10X', 'Normal_Coverage-10X','Tumor_Coverage-20X', 'Normal_Coverage-20X',
                'Tumor_Coverage-50X', 'Normal_Coverage-50X','Tumor_Coverage-100X','Normal_Coverage-100X','Tumor_Total-Reads-ADup', 'Normal_Total-Reads-ADup']:
        df_join[col] =  [int(x.replace('%','')) for x in df_join[col]]

    fig= plt.figure(num=None, figsize=(15, 10), dpi=80, facecolor='w', edgecolor='k')
    ax1 = plt.subplot2grid((3, 2), (0, 0))
    ax2 = plt.subplot2grid((3, 2), (0, 1))
    ax3 = plt.subplot2grid((3, 2), (1, 0), colspan=2)
    ax4 = plt.subplot2grid((3, 2), (2, 0), colspan=2)
    df_join.boxplot(column=['Tumor_Total-Reads', 'Normal_Total-Reads'],ax=ax1)
    ax1.title.set_text('Total Reads (millions)')
    ax1.set_xticklabels(['Tumor','Normal'])
    df_join.boxplot(column=['Tumor_Coverage', 'Normal_Coverage'],ax=ax2)
    ax2.title.set_text('Average Coverage')
    ax2.set_xticklabels(['Tumor','Normal'])
    df_join.boxplot(column=['Tumor_Total-Reads-ADup', 'Normal_Total-Reads-ADup','Tumor_Duplicate', 'Normal_Duplicate'],ax=ax3)
    ax3.title.set_text('Total Reads Pass Percentage and Duplicate Percentage')
    ax3.set_xticklabels(['Tumor Reads Pass','Normal Reads Pass','Tumor Duplicate','Normal Duplicate'])
    df_join.boxplot(column=['Tumor_Coverage-10X', 'Normal_Coverage-10X','Tumor_Coverage-20X', 'Normal_Coverage-20X', 'Tumor_Coverage-50X', 'Normal_Coverage-50X','Tumor_Coverage-100X','Normal_Coverage-100X'],ax=ax4)
    ax4.title.set_text('Coverage at Various Levels')
    ax4.set_xticklabels(['Tumor-10x','Normal-10x','Tumor-20x','Normal-20x','Tumor-50x','Normal-50x','Tumor-100x','Normal-100x'])
    fig.tight_layout()
    plt.savefig("Fig_2_TMB_Seq_Stat_plots.png")
    plt.suptitle("TMB Sequence Quality Control Statistics")
    plt.close()


def plot_TotalVariants_Raw_Selected(df_join):
    sns.regplot(x=np.log10(df_join['TMB-Total-Variants']), y=np.log10(df_join['TMB-Total-Variants-Raw']), data=df_join,ci=None)
    x1 = df_join['TMB-Total-Variants'].values
    y1 = df_join['TMB-Total-Variants-Raw'].values
    plt.title("TMB Variants Comparisons, spearmanr: " + str(round(st.spearmanr(x1, y1)[0],3)))
    plt.savefig("Fig_3_TMB_HMH_Mutations_Raw_Variants_ScatterPlot.png")
    plt.close()


def fitData (X,y,method):
    if method == "simple-lr":
        model = LinearRegression().fit(X, y)
        return model.predict(X)
    elif method == "nonpara-lr":
        model = KernelRidge(kernel='linear').fit(X,y)
        return model.predict(X)
    elif method == "nonpara-poly":
        model = KernelReg(endog=y, exog=X, var_type='c',reg_type='ll')
        x2=np.reshape(range(600),(-1,1))
        return model.fit(x2)[0]


def plotClustering(df_join, type):

    d_points=np.reshape(df_join['TMB-Total-Variants'],(-1,1))
    t_points=np.reshape(range(0,350),(-1,1))

    if type == "kmeans":

        model = KMeans(n_clusters=3).fit(d_points)
        df_join['kmeans'] = model.predict(d_points)

        sns.scatterplot(x=range(df_join.shape[0]) ,y=df_join['TMB-Total-Variants'].sort_values(), hue="kmeans", data=df_join,palette=['blue','red','green'])
        plt.title("Cluster Analysis - Kmeans")
        plt.savefig("Fig_5_TMB_HMH_kmeans_score.png")
        plt.close()

        return model.predict(t_points)


    elif type == "gmix":

        # model = GaussianMixture(n_components=3,init_params='random').fit(d_points)
        model = GaussianMixture(n_components=3).fit(d_points)
        df_join['gmix'] = model.predict(d_points)

        sns.scatterplot(x=range(df_join.shape[0]) ,y=df_join['TMB-Total-Variants'].sort_values(), hue="gmix", data=df_join,palette=['blue','red','green'])
        plt.title("Cluster Analysis - Gmixture")
        plt.savefig("Fig_5_TMB_HMH_gmix_score.png")
        plt.close()

        return model.predict(t_points)

    elif type == "hclust":

        model = AgglomerativeClustering(n_clusters=3).fit(d_points)
        df_join['hclust'] = model.fit_predict(d_points)

        sns.scatterplot(x=range(df_join.shape[0]) ,y=df_join['TMB-Total-Variants'].sort_values(), hue="hclust", data=df_join,palette=['blue','red','green'])
        plt.title("Cluster Analysis - hclust ")
        plt.savefig("Fig_5_TMB_HMH_hclust_score.png")
        plt.close()


        linkage_matrix = linkage(d_points, 'ward')
        figure = plt.figure(figsize=(7.5, 5))
        dendrogram(
            linkage_matrix,
            color_threshold=0,
        )
        plt.title('Hierarchical Clustering Dendrogram (Ward)')
        plt.xlabel('sample index')
        plt.ylabel('distance')
        plt.savefig("Fig_5_TMB_HMH_hclust_dendog_score.png")
        plt.close()


        centers={}
        centers[0]=df_join[df_join['hclust']==0]['TMB-Total-Variants'].mean()
        centers[1]=df_join[df_join['hclust']==1]['TMB-Total-Variants'].mean()
        centers[2]=df_join[df_join['hclust']==2]['TMB-Total-Variants'].mean()

        predict =[]
        for point in t_points:
            predict.append(np.argmin([np.abs(point-centers[0])[0],np.abs(point-centers[1])[0],np.abs(point-centers[2])[0]]))

        return predict





# file_runs = sys.argv[1]
file_runs ="tmb_samples.txt"
file_metadata = "tmb_metadata.csv"

## get sample results
samples=get_result_files(file_runs)

## create DataFrame
df = createdf(samples)

#### combine metadata
df_join = addMetadata(file_metadata)

##output result
df_join.to_csv("tmb_validation_samples_all.csv",index=False)

### drop duplicates
df_join.drop_duplicates('ExomeID',keep='last',inplace=True)
df_join = df_join[df_join['ExomeID'] != 'Exome3001']
df_join = df_join[df_join['ExomeID'] != 'Exome3002']
df_join.to_csv("tmb_validation_samples_unique.csv",index=False)

plot_generalInfo(df_join)

plot_sequence_stats(df_join[['Tumor_Total-Reads', 'Normal_Total-Reads',
        'Tumor_Duplicate', 'Normal_Duplicate',
        'Tumor_Total-Reads-ADup', 'Normal_Total-Reads-ADup',
        'Tumor_Coverage', 'Normal_Coverage',
        'Tumor_Coverage-10X', 'Normal_Coverage-10X','Tumor_Coverage-20X', 'Normal_Coverage-20X',
        'Tumor_Coverage-50X','Normal_Coverage-50X', 'Tumor_Coverage-100X','Normal_Coverage-100X',
        'Tumor_Breadth-Coverage']].copy())


plot_TotalVariants_Raw_Selected(df_join)


### modeling non parametric:
X = np.reshape(df_join['TMB-Total-Variants'],(-1,1))
y = df_join['TMB-Foundation-Value'].values
y_slr = fitData(X,y,"simple-lr")
y_nplr = fitData(X,y,"nonpara-lr")
### figure with model
sns.scatterplot(x="TMB-Total-Variants", y="TMB-Foundation-Value", data=df_join, hue='Source')
plt.plot(X,y_slr,'-b',label='simple-lr')
# plt.plot(X,y_nplr,'-g',label='nonparametric-lr')
plt.title("TMB Score Comparisons , S/P/R^2= " +
        str(round(st.spearmanr(df_join['TMB-Total-Variants'],df_join['TMB-Foundation-Value'])[0],3))+"/" +
        str(round(st.pearsonr(df_join['TMB-Total-Variants'],df_join['TMB-Foundation-Value'])[0],3)) +"/" +
        str(round(r2_score(y, y_slr),3)))
plt.savefig("Fig_4_TMB_HMH_Foundation_Variants_Score_ScatterPlot_main.png")
plt.close()


### caris vs Foundation
x1 = np.reshape(df_join[df_join['Source']=="Caris"]['TMB-Total-Variants'].values,(-1,1))
y1 = df_join[df_join['Source']=="Caris"]['TMB-Foundation-Value'].values
y1_slr = fitData(x1,y1,"simple-lr")
sns.regplot(x=x1, y=y1, ci=None)
plt.title("TMB Score Comparison-Caris, S/P/R^2= "+ str(round(st.spearmanr(x1,y1)[0],3))+"/" + str(round(st.pearsonr(df_join[df_join['Source']=="Caris"]['TMB-Total-Variants'].values,y1)[0],3)) + "/" +str(round(r2_score(y1, y1_slr),3)) )
plt.savefig("TMB_HMH_Variants_Foundation_Score_ScatterPlot_Caris.png")
plt.close()

x2 = np.reshape(df_join[df_join['Source']=="Foundation"]['TMB-Total-Variants'].values,(-1,1))
y2 = df_join[df_join['Source']=="Foundation"]['TMB-Foundation-Value'].values
y2_slr = fitData(x2,y2,"simple-lr")
sns.regplot(x=x2, y=y2, ci=None)
plt.title("TMB Score Comparison-Foundation, S/P/R^2= "+ str(round(st.spearmanr(x2,y2)[0],3))+"/" + str(round(st.pearsonr(df_join[df_join['Source']=="Foundation"]['TMB-Total-Variants'].values,y2)[0],3)) +"/" + str(round(r2_score(y2, y2_slr),3)) )
plt.savefig("TMB_HMH_Variants_Foundation_Score_ScatterPlot_Foundation.png")
plt.close()

#####  clustering
kmeans = plotClustering(df_join, "kmeans")
hclust = plotClustering(df_join, "hclust")
gmix = plotClustering(df_join, "gmix")
df_pred = pd.DataFrame([range(0,350), kmeans,hclust,gmix]).T
df_pred.columns = ['vals','kmeans','hclust','gmix']
df_pred.to_csv("cluster_model_temp.csv",index=False)

# df_model = pd.read_csv("cluster_model.csv")
# sns.lineplot(x=range(0,350), y="kmeans",data=df_model,label='kmeans' )
# sns.lineplot(x=range(0,350), y="hclust",data=df_model,label='hclust' )
# sns.lineplot(x=range(0,350), y="gmix",data=df_model,label='gmixture' )
# sns.lineplot(x=range(0,350), y="gmix2nd",data=df_model,label='gmixture-2nd')
# plt.ylabel("group")
# plt.xlabel('HMH TMB Total Variants')
# plt.title("kmeans (118-326), hclust (84-300), gmixture (58-276), 2nd (130-284) ")
# plt.savefig("TMB_HMH_Variants_Foundation_Score_Cluster_lineplot.png")
# plt.close()
 ############ other extra plots
# # st.probplot(df['TLOD'],dist="expon", plot=pylab)
# # plt.savefig("qqplot_expon_t.png")
# # plt.close()
# #
# # x1=df_join['TMB-Total-Variants'].values
# # y1=df_join['TMB-Foundation-Value'].values
# #
# # sns.regplot(x=x1, y=y1, data=df_join,ci=None)
# # plt.savefig("test.png")
# # plt.close()
#
#
# ## table
# # (df_join['TMB-Total-Variants']<200).sum()
# # (df_join['TMB-Total-Variants']>=200).sum()
# # (df_join['TMB-Foundation-Value']>=10.0).sum()
# # (df_join['TMB-Foundation-Value']<10.0).sum()
# # df_join[ ( (df_join['TMB-Total-Variants']>=200.0 ) & (df_join['TMB-Foundation-Value']>=10.0))].shape[0]
# # df_join[ ( (df_join['TMB-Total-Variants']<200.0 ) & (df_join['TMB-Foundation-Value']<10.0))].shape[0]
# # df_join[ ( (df_join['TMB-Total-Variants']>=200.0 ) & (df_join['TMB-Foundation-Value']>10.0))].shape[0]
#
