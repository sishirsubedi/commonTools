import sys
import re
import pandas as pd
import basemodel as bm
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn import preprocessing
from sklearn.model_selection import cross_val_score,cross_val_predict
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier

# df = pd.read_csv(sys.argv[1])

df = pd.read_csv("d2_final_datamat.csv")

df_xmat = df[[x for x in df.columns if x not in ['PTH','MRN']]]

### continuous predictions
df_ymat_cont = df[['PTH']]

###categorical predictions
df_ymat_cat  = []
for x in df_ymat_cont.values:
    if x<66:
        df_ymat_cat.append(0)
    else:
        df_ymat_cat.append(1)

### categorical data modeling

X_train, X_test, y_train, y_test = train_test_split( df_xmat.values, df_ymat_cat, test_size=0.4, random_state=0)


######### best model ######
gb = GradientBoostingClassifier()

gb.fit(X_train, y_train)
bm.evaluateModel(gb,X_test,y_test)

cross_val_score(gb, X_train, y_train, cv=10)
cross_val_score(gb, df_xmat.values, df_ymat_cat, cv=10)


gb_topfeat = bm.topFeatures(df_xmat.columns,gb.feature_importances_)
df_xmat_gbf = df[[x for x in df_xmat.columns if x in gb_topfeat['features'].values]]
df_xmat_gbf = df[[x for x in df_xmat.columns if x in gb_topfeat['features'][0:3].values]]

X_train, X_test, y_train, y_test = train_test_split( df_xmat_gbf.values, df_ymat_cat, test_size=0.4, random_state=0)
gb = GradientBoostingClassifier()
gb.fit(X_train, y_train)
bm.evaluateModel(gb,X_test,y_test)


##### for cross validation
cv = KFold(n_splits=10, random_state=0, shuffle=False)
for train_index, test_index in cv.split(df_xmat.values):

    X_train = df_xmat.iloc[train_index,:].values
    X_test = df_xmat.iloc[test_index,:].values
    y_train = [df_ymat_cat[i] for i in train_index]
    y_test  = [df_ymat_cat[i] for i in test_index]

    gb = GradientBoostingClassifier()
    gb.fit(X_train, y_train)
    print(bm.evaluateModel(gb,X_test,y_test))



### other categorical models

gnb = GaussianNB()
gnb.fit(X_train, y_train)
bm.evaluateModel(gnb,X_test,y_test,"gaussian_roc")

dtree = DecisionTreeClassifier(random_state=0)
dtree.fit(X_train, y_train)
bm.evaluateModel(dtree,X_test,y_test,"gdtree_roc")

rf = RandomForestClassifier()
rf.fit(X_train, y_train)
bm.evaluateModel(rf,X_test,y_test,"rf_roc")



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
