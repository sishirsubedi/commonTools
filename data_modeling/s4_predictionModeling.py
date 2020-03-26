import sys
import pandas as pd
import numpy as np
import basemodel as bm
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold,StratifiedKFold
from sklearn.preprocessing import StandardScaler



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


params_focused_selected = {'learning_rate': [0.16],
                        'n_estimators':[90],
                        'min_samples_split': [32],
                        'min_samples_leaf': [4],
                        'max_depth': [3]}

X_train, X_test, y_train, y_test = train_test_split( df_xmat.values, df_ymat_cat, test_size=0.33, random_state=0)
model_exact = bm.grid_search('GB',X_train, y_train,'FOCUSED',params_focused_selected,cv_=10)
bm.evaluateModel(model_exact,X_test, y_test,True,"model_roc")
print(bm.modelMetrics(y_test,model_exact.predict(X_test),model_exact.predict_proba(X_test))

##### cross validated metrics

result = []
kfold = StratifiedKFold(5, True, 1)
kfold.get_n_splits(df_xmat.values, df_ymat_cat)
# enumerate splits
for train, test in kfold.split(df_xmat.values, df_ymat_cat):

    X_train = df_xmat.iloc[train,:]
    y_train = [df_ymat_cat[x] for x in train]

    X_test =  df_xmat.iloc[test,:]
    y_test =  [df_ymat_cat[x] for x in test]

    model_exact = bm.grid_search('GB',X_train, y_train,'FOCUSED',params_focused_selected,cv_=3)
    print(bm.modelMetrics(y_test,model_exact.predict(X_test),model_exact.predict_proba(X_test)))
    result.append([bm.modelMetrics(y_test,model_exact.predict(X_test),model_exact.predict_proba(X_test))])




































#########################################

import sys
import pandas as pd
import numpy as np
import basemodel as bm
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
#Importing Confusion Matrix
from sklearn.metrics import confusion_matrix,classification_report
from sklearn.preprocessing import StandardScaler


## deep learning

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

foi = ['CA', 'CL', 'CREAT', 'IGRAN', 'MCHC', 'SODIUM', 'max_CA', 'min_CA', 'last_PHOS', 'last_MPV', 'last_CA', 'RACE_B']
df_xmat = df_xmat[[x for x in df_xmat.columns if x in foi]]

###plot 12 features
bm.sns.pairplot(df_xmat_plot,hue='pth')
bm.plt.savefig("temp.png");bm.plt.close()
df_xmat_plot[df_xmat_plot['pth']==0]
df_xmat_plot[df_xmat_plot['pth']==0].shape
df_xmat_plot[df_xmat_plot['pth']==1].shape




X_train, X_test, y_train, y_test = train_test_split( df_xmat.values, df_ymat_cat, test_size=0.33)
#Fitting the training data to the network

scaler = StandardScaler()
scaler.fit(X_train)
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

#Initializing the MLPClassifier
mlp = MLPClassifier(hidden_layer_sizes=(12,12,2), max_iter=500,activation = 'relu',solver='adam',random_state=1)
mlp.fit(X_train, y_train)

predictions = mlp.predict(X_test)

print(confusion_matrix(y_test,predictions))
print(classification_report(y_test,predictions))
#Comparing the predictions against the actual observations in y_val
cm = confusion_matrix(predictions, y_test)

#Printing the accuracy
def accuracy(confusion_matrix):
   diagonal_sum = confusion_matrix.trace()
   sum_of_all_elements = confusion_matrix.sum()
   return diagonal_sum / sum_of_all_elements

print("Accuracy of MLPClassifier :", accuracy(cm))
