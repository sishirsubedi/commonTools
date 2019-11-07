import sys
import pandas as pd
import basemodel as bm
from sklearn.model_selection import train_test_split

df = pd.read_csv("d2_final_datamat.csv")

df_xmat = df[[x for x in df.columns if x not in ['PTH','MRN']]]

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



#### default model survey

default_models = bm.defaultModels(df_xmat,df_ymat_cat)
for m in default_models :
    print(m[0],m[1][0],m[1][1],m[1][2],m[1][3],m[1][4],m[1][5],m[1][6],m[1][7],m[1][8],m[1][9])

### Choose a BEST model
### Categorical data modeling
### Feature selection
X_train, X_test, y_train, y_test = train_test_split( df_xmat.values, df_ymat_cat, test_size=0.33, random_state=0)

gb = GradientBoostingClassifier()
gb.fit(X_train, y_train)
bm.evaluateModel(gb,X_test,y_test)
print(bm.modelMetrics(y_test,gb.predict(X_test),gb.predict_proba(X_test)))


### test prediction power of top selected features
gb_topfeat = bm.topFeatures(df_xmat.columns,gb.feature_importances_)
df_xmat_gbf = df[[x for x in df_xmat.columns if x in gb_topfeat['features'].values]]
# df_xmat_gbf = df[[x for x in df_xmat.columns if x in gb_topfeat['features'][0:3].values]]
X_train, X_test, y_train, y_test = train_test_split( df_xmat_gbf.values, df_ymat_cat, test_size=0.3, random_state=0)
gb = GradientBoostingClassifier()
gb.fit(X_train, y_train)
bm.evaluateModel(gb,X_test,y_test)



######### # hyperparameter tuning ######

model_random = bm.grid_search('GB',df_xmat.values, df_ymat_cat,'RANDOMIZE',cv_=3,n_iter_=25)

params_random_selected= {'learning_rate': [0.03,0.05,0.07],
                         'loss': ['deviance'],
                         'max_depth': [8],
                         'max_features': [3,5,8],
                         'min_samples_leaf': [1],
                         'min_samples_split': [3,4,5]}

model_focused = bm.grid_search('GB',df_xmat.values, df_ymat_cat,'FOCUSED',params_random_selected,cv_=10)


params_focused_selected = {'learning_rate': [0.05],
                         'loss': ['deviance'],
                         'max_depth': [8],
                         'max_features': [8],
                         'min_samples_leaf': [1],
                         'min_samples_split': [5]}

model_exact = bm.grid_search('GB',df_xmat.values, df_ymat_cat,'FOCUSED',params_focused_selected,cv_=10)

######## test back model
X_train, X_test, y_train, y_test = train_test_split( df_xmat.values, df_ymat_cat, test_size=0.33, random_state=0)

gb = bm.GradientBoostingClassifier(
                                learning_rate= 0.05,
                                loss= 'deviance',
                                max_depth= 8,
                                max_features= 8,
                                min_samples_leaf= 1,
                                min_samples_split= 5
                                )
gb.fit(X_train, y_train)
print(bm.modelMetrics(y_test,gb.predict(X_test),gb.predict_proba(X_test)))

bm.evaluateModel(gb,X_test,y_test,True,"Method_1_Final")

gb_topfeat = bm.topFeatures(df_xmat.columns,gb.feature_importances_)

####### continuous data modeling

## with scaling
X_scaled = preprocessing.scale(df_xmat)
X_train, X_test, y_train, y_test = train_test_split( X_scaled, df_ymat.values, test_size=0.4, random_state=0)

## without scaling
X_train, X_test, y_train, y_test = train_test_split( df_xmat.values, df_ymat.values, test_size=0.4, random_state=0)

reg = LinearRegression().fit(X_train, y_train)
reg.score(X_test, y_test)

svr_poly = SVR(kernel='poly', C=100, gamma='auto', degree=3, epsilon=.1,coef0=1)
svr_poly.fit(X_train,y_train)
