import sys
import pandas as pd
import numpy as np
import basemodel as bm
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler



#### default model survey #############################

df = pd.read_csv("d3_after_impute_final_datamat.csv",low_memory=False)

df_xmat = df[[x for x in df.columns if x not in ['PTH','MRN','max_PTH','min_PTH','last_PTH']]]
feature_columns = df_xmat.columns
### continuous predictions
df_ymat_cont = df[['PTH']]

###categorical predictions
df_ymat_cat  = []
for x in df_ymat_cont.values:
    #if ca < ___(8?) then 0
    #else if pth
    if x < 66:
        df_ymat_cat.append(0)
    else:
        df_ymat_cat.append(1)



######## basic modeling
scaler = StandardScaler()
df_xmat = pd.DataFrame(scaler.fit_transform(df_xmat),columns=feature_columns)


default_models = bm.defaultModels(df_xmat,df_ymat_cat)
for m in default_models :
    # print(m[0],round(m[1][0],4),round(m[2][0],4))
    print(m[0],round(m[1],4),round(m[2],4))


##### choose xgboost and hyperparameter tuning

#### tune learning rate and number of trees

params_focused_selected = {'n_estimators':range(10,201,10), 'learning_rate': np.arange(0.01,0.21,0.01)}
model_exact = bm.grid_search('GB',df_xmat.values, df_ymat_cat,'FOCUSED',params_focused_selected,cv_=10)

model_scores=[]
i=0
while i<400:
    model_scores.append(model_exact.cv_results_['mean_test_score'][i:i+20])
    i+=20
df_model_scores = pd.DataFrame(model_scores)
df_model_scores.columns = range(10,201,10)
df_model_scores.index = [0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.1,0.11,0.12,0.13,0.14,0.15,0.16,0.17,0.18,0.19,0.2]
bm.sns.heatmap(df_model_scores,cmap="RdYlGn",cbar_kws={'label': 'mean accuracy (cv-10)'})
bm.plt.xlabel("number of trees")
bm.plt.ylabel("learning rate")
bm.plt.savefig("model_scores_hmap.png");bm.plt.close()
df_model_scores.to_csv("df_model_scores.csv")

############### tune other tree based parameters

params_focused_selected = {'learning_rate': [0.16],
                            'n_estimators':[90],
                            'min_samples_split': [2,4,8,16,32,64,128],
                            'min_samples_leaf': [1,2,4,8,16,32,64,128],
                            'max_depth': range(2,11,1)}

model_exact = bm.grid_search('GB',df_xmat.values, df_ymat_cat,'FOCUSED',params_focused_selected,cv_=10)
print(model_exact.cv_results_['mean_test_score'].min(),model_exact.cv_results_['mean_test_score'].max(),model_exact.best_params_,model_exact.best_score_)

bm.plt.plot(range(1,505,1),model_exact.cv_results_['mean_test_score'].sort())
bm.plt.plot(range(1,505,1),model_exact.cv_results_['mean_test_score'].sort(),'ro',markersize=1)

bm.plt.plot(range(1,505,1),scores,'k-')
bm.plt.plot(range(1,505,1),scores,'ro',markersize=1)
bm.plt.axhline(y=0.745, color='k', linestyle='--')
bm.plt.xlabel("model")
bm.plt.ylabel("mean accuracy (cv-10)")
bm.plt.savefig("model_scores_para_tuning.png");bm.plt.close()

##################### final model
params_focused_selected = {'learning_rate': [0.16],
                            'n_estimators':[90],
                            'min_samples_split': [32],
                            'min_samples_leaf': [4],
                            'max_depth': [3]}

model_exact = bm.grid_search('GB',df_xmat.values, df_ymat_cat,'FOCUSED',params_focused_selected,cv_=10)
print(model_exact.cv_results_['mean_test_score'].min(),model_exact.cv_results_['mean_test_score'].max(),model_exact.best_params_,model_exact.best_score_)


############################ feature selection

from sklearn.feature_selection import RFECV

X_train = df_xmat
y_train = df_ymat_cat


print ("feature ranking running....-> GradientBoostingClassifier")
model2 = bm.GradientBoostingClassifier(learning_rate=0.16,
                            n_estimators = 90,
                            min_samples_split= 32,
                            min_samples_leaf= 4,
                            max_depth=3)
rfe = RFECV(estimator=model2, step=1, cv=bm.StratifiedKFold(10),scoring='accuracy',n_jobs=-1)
rfe = rfe.fit(X_train,y_train )
gboost_ranking =[]
for x,d in zip(rfe.estimator_.feature_importances_,X_train.columns):
    gboost_ranking.append([d,x])
gboost_ranking = pd.DataFrame(gboost_ranking,columns=['features','gboost'])
gboost_ranking.sort_values('features',inplace=True)
gboost_ranking.to_csv("gboost_ranking_final.csv",index=False)


########################### work in excel to combine features


df = pd.read_csv("d3_after_impute_final_datamat.csv",low_memory=False)

df_xmat = df[[x for x in df.columns if x not in ['PTH','MRN','max_PTH','min_PTH','last_PTH']]]

### continuous predictions
df_ymat_cont = df[['PTH']]

###categorical predictions
df_ymat_cat  = []
for x in df_ymat_cont.values:
    #if ca < ___(8?) then 0
    #else if pth
    if x < 66:
        df_ymat_cat.append(0)
    else:
        df_ymat_cat.append(1)


 ############# use selected feature

df_feature_ranking = pd.read_csv("gboost_ranking_final.csv")

# df_feature_ranking = df_feature_ranking[df_feature_ranking['real_column']==1]

gb_topfeat_gboost = df_feature_ranking.sort_values(by='gboost',ascending=False)['features'].values

final_score_all=[]

for indx in range(1,114):
    df_xmat_gbf = df[[x for x in df_xmat.columns if x in gb_topfeat_gboost[0:indx]]]
    params_focused_selected = {'learning_rate': [0.16],
                            'n_estimators':[90],
                            'min_samples_split': [32],
                            'min_samples_leaf': [4],
                            'max_depth': [3]}

    model_exact = bm.grid_search('GB',df_xmat_gbf.values, df_ymat_cat,'FOCUSED',params_focused_selected,cv_=10)

    final_score_all.append([model_exact.cv_results_['mean_test_score'].max()])

df_final_score_all = pd.DataFrame(final_score_all)
df_final_score_all.to_csv("df_final_score_all_seq_model.csv",index=False)
#########################################################
