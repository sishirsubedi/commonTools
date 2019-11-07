import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold

from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier

from sklearn.metrics import accuracy_score, log_loss,roc_auc_score,roc_curve,confusion_matrix


def correlation_info(datamatrix,th,drop,draw):
    print("correlation_info running ... ")
    df_all_data = datamatrix

    corr_matrix = df_all_data.iloc[:,0:(df_all_data.shape[1]-1)].corr()
    if draw:
        plt.figure(figsize=(10, 10))
        sns.heatmap(corr_matrix,xticklabels=corr_matrix.columns,yticklabels=corr_matrix.columns)
        plt.savefig("correlation_plot.png")
        plt.close()
    cormat_melted = []
    for i in range(len(corr_matrix)):
        f1 = corr_matrix.columns[i]
        for j in range(i,len(corr_matrix)):
            f2 = corr_matrix.columns[j]
            cormat_melted.append([f1, f2, corr_matrix.iloc[i,j]])
    cormat_melted = pd.DataFrame(cormat_melted,columns=['f1','f2','values'])
    cormat_melted.head(5)
    cormat_melted_filt = cormat_melted.loc[(cormat_melted['values']>=th) & (cormat_melted['values'] !=1.0)]
    todrop = set(cormat_melted_filt['f2'])

    print ("Correlation filter >" , str(th) , ": " , str(len(todrop)) , " features from the dataset")
    print (todrop)

    if drop ==1:
        return todrop


def defaultModels(df_xmat,df_ymat_cat):

    classifiers = [
    GaussianNB(),
    DecisionTreeClassifier(),
    LogisticRegression(),
    RandomForestClassifier(),
    AdaBoostClassifier(),
    GradientBoostingClassifier(),
    ]

    cv = KFold(n_splits=10, random_state=0, shuffle=False)

    res = []

    for clf in classifiers:

        metrics_cv =[]

        for train_index, test_index in cv.split(df_xmat.values):

            X_train = df_xmat.iloc[train_index,:].values
            X_test = df_xmat.iloc[test_index,:].values
            y_train = [df_ymat_cat[i] for i in train_index]
            y_test  = [df_ymat_cat[i] for i in test_index]

            clf.fit(X_train, y_train)

            metrics_cv.append(modelMetrics(y_test, clf.predict(X_test),clf.predict_proba(X_test)))

        res.append([str(clf)[:10],np.array(metrics_cv).mean(axis=0)])

    return res


def modelMetrics(y_true,y_pred,y_pred_prob):

    AUC = roc_auc_score(y_true, y_pred_prob[:, 1])
    LL = log_loss(y_true, y_pred_prob)

    CM = confusion_matrix(y_true, y_pred)

    TN = CM[0][0]
    FN = CM[1][0]
    TP = CM[1][1]
    FP = CM[0][1]

    # Sensitivity, hit rate, recall, or true positive rate
    TPR = TP/(TP+FN)
    # Specificity or true negative rate
    TNR = TN/(TN+FP)
    # Precision or positive predictive value
    PPV = TP/(TP+FP)
    # Negative predictive value
    NPV = TN/(TN+FN)
    # False positive rate
    FPR = FP/(FP+TN)
    # False negative rate
    FNR = FN/(TP+FN)
    # False discovery rate
    FDR = FP/(TP+FP)

    # Accuracy
    ACC = (TP+TN)/(TP+FP+FN+TN)

    return [AUC,ACC,LL,TPR,TNR,PPV,NPV,FPR,FNR,FDR]


def plot_roc_curve(fpr, tpr,auc,f_name):
    plt.plot(fpr, tpr, color='orange', label='ROC:'+str(round(auc,2)))
    plt.plot([0, 1], [0, 1], color='darkblue', linestyle='--')
    plt.xlabel('1 - Specificity')
    plt.ylabel('Sensitivity')
    plt.title('Receiver Operating Characteristic (ROC) Curve')
    plt.legend()
    plt.savefig(f_name+".png")
    plt.close()

def plot_senspec_curve(specificity, tpr,auc,f_name):

    # ax = plt.axes(projection='3d')
    # ax.plot3D(thresholds[1:], specificity[1:], tpr[1:], 'gray')
    # ax.set_xlabel('thresholds')
    # ax.set_ylabel('specificity')
    # ax.set_zlabel('tpr')
    # plt.savefig(f_name+"_sen_spec.png")
    # plt.close()

    plt.plot(specificity, tpr, color='orange')
    plt.xlabel('Specificity')
    plt.ylabel('Sensitivity')
    plt.title('Specificity-Sensitivity Curve')
    plt.savefig(f_name+"_sen_spec.png")
    plt.close()

def evaluateModel(model,X_test,y_test,isplot=None,f_name=None):
    probs = model.predict_proba(X_test)
    probs = probs[:, 1]

    auc = roc_auc_score(y_test, probs)

    if isplot:
        fpr, tpr, thresholds = roc_curve(y_test, probs)
        plot_roc_curve(fpr, tpr,auc,f_name)

    return auc

def topFeatures(features, feature_importance):
    df = pd.DataFrame()
    df['importance'] = feature_importance
    df['features'] = features
    df_topf = df.sort_values('importance',ascending=False)
    return df_topf.iloc[0:10,:]

def grid_search(model,xdata,ydata,mode,param_grid=None,cv_=None,n_iter_=None):

    if model == 'RF' and mode == 'RANDOMIZE':
        n_estimators = [int(x) for x in np.linspace(start = 200, stop = 2000, num = 10)]
        max_features = ['auto', 'sqrt']
        max_depth = [int(x) for x in np.linspace(10, 110, num = 11)]
        min_samples_split = [2, 5, 10]
        min_samples_leaf = [1, 2, 4]
        bootstrap = [True, False]
        random_grid = {'n_estimators': n_estimators,
                       'max_features': max_features,
                       'max_depth': max_depth,
                       'min_samples_split': min_samples_split,
                       'min_samples_leaf': min_samples_leaf,
                       'bootstrap': bootstrap}
        rf = RandomForestClassifier()
        rf_random = RandomizedSearchCV(estimator = rf, param_distributions = random_grid, n_iter = 5, cv = 2, verbose=2, random_state=0, n_jobs = -1)
        rf_random.fit(xdata, ydata)
        return rf_random.best_params_


    elif model == 'RF' and mode == 'FOCUSED':
        rf = RandomForestClassifier()
        rf_random = GridSearchCV(estimator = rf, param_grid  = param_grid, cv = 3, verbose=2, n_jobs = -1)
        rf_random.fit(xdata, ydata)
        return rf_random.best_params_

    elif model == 'RF' and mode == 'EXACT':
        res_matrix = np.zeros((len(param_grid['n_estimators']), len(param_grid['max_depth']), len(param_grid['min_samples_leaf'])))
        for n_estimator_index, n_estimator in enumerate(param_grid['n_estimators']):
            for max_depth_index , max_depth  in enumerate(param_grid['max_depth']):
                for min_samples_leaf_index, min_samples_leaf in enumerate(param_grid['min_samples_leaf']):
                    model = RandomForestClassifier(n_jobs=-1,
                    max_depth=int(max_depth),
                    n_estimators=int(n_estimator),
                    min_samples_leaf=int(min_samples_leaf),
                    random_state =0 )
                    predicted = cross_val_predict(model, xdata,ydata, cv=3)
                    res_matrix[max_depth_index, n_estimator_index, min_samples_leaf_index] = accuracy_score(ydata, predicted)
                    print('\rGRID SEARCHING RF: processing set:| %s | %s | %s |' % (n_estimator_index,max_depth_index,min_samples_leaf_index))
        best_p = np.where(res_matrix == res_matrix.max())
        return res_matrix,(param_grid['n_estimators'][best_p[0][0]],param_grid['max_depth'][best_p[1][0]],param_grid['min_samples_leaf'][best_p[2][0]])

    elif model == 'GB' and mode == 'RANDOMIZE':

        loss = ['deviance', 'exponential']

        #There is a trade-off between learning_rate and n_estimators
        learning_rates = [0.05, 0.1, 0.25, 0.5, 0.75, 1]
        n_estimators = [10,50,100,200]

        max_depth = [2,4,8]
        max_features = [5,10,'auto']

        min_samples_split = [2, 4, 8]
        min_samples_leaf = [1, 2, 4]

        random_grid = {'loss': loss,
                       'learning_rate': learning_rates,
                       'max_features': max_features,
                       'max_depth': max_depth,
                       'min_samples_split': min_samples_split,
                       'min_samples_leaf': min_samples_leaf,
                       }

        gb = GradientBoostingClassifier()
        model_random = RandomizedSearchCV(estimator = gb, param_distributions = random_grid, n_iter = n_iter_, cv = cv_, verbose=2, random_state=0, n_jobs = -1)
        model_random.fit(xdata, ydata)

        return model_random

    elif model == 'GB' and mode == 'FOCUSED':
        gb = GradientBoostingClassifier()
        model_focused = GridSearchCV(estimator = gb, param_grid  = param_grid, cv = cv_, verbose=2, n_jobs = -1)
        model_focused.fit(xdata, ydata)
        return model_focused
