import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_predict
# from xgboost.sklearn import XGBClassifier
from sklearn import metrics
import numpy as np


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
    else:
        return  []



def grid_search(model,xdata,ydata,mode,param_grid=None):
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
                    predicted = cross_val_predict(model, xdata,ydata, cv=cv_)
                    res_matrix[max_depth_index, n_estimator_index, min_samples_leaf_index] = metrics.accuracy_score(ydata, predicted)
                    if verbose == True:
                        print('\rGRID SEARCHING RF: processing set:| %s | %s | %s |' % (n_estimator_index,max_depth_index,min_samples_leaf_index))
        best_p = np.where(res_matrix == res_matrix.max())
        return res_matrix,(param_grid['n_estimators'][best_p[0][0]],param_grid['max_depth'][best_p[1][0]],param_grid['min_samples_leaf'][best_p[2][0]])

    elif model == 'GB' and mode == 'EXACT':
        res_matrix = np.zeros((len(param_grid['n_estimators']), len(param_grid['max_depth']), len(param_grid['min_samples_leaf'])))
        for n_estimator_index, n_estimator in enumerate(param_grid['n_estimators']):
            for max_depth_index , max_depth  in enumerate(param_grid['max_depth']):
                for min_samples_leaf_index, min_samples_leaf in enumerate(param_grid['min_samples_leaf']):
                    model = GradientBoostingClassifier(
                    max_depth=int(max_depth),
                    n_estimators=int(n_estimator),
                    min_samples_leaf=int(min_samples_leaf),
                    random_state =0 )
                    predicted = cross_val_predict(model, xdata,ydata, cv=cv_)
                    res_matrix[max_depth_index, n_estimator_index, min_samples_leaf_index] = metrics.accuracy_score(ydata, predicted)
                    if verbose == True:
                        print('\rGRID SEARCHING GB: processing set:| %s | %s | %s |' % (n_estimator_index,max_depth_index,min_samples_leaf_index))
        best_p = np.where(res_matrix == res_matrix.max())
        return res_matrix,(param_grid['n_estimators'][best_p[0][0]],param_grid['max_depth'][best_p[1][0]],param_grid['min_samples_leaf'][best_p[2][0]])


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

    auc = metrics.roc_auc_score(y_test, probs)

    if isplot:
        fpr, tpr, thresholds = metrics.roc_curve(y_test, probs)
        plot_roc_curve(fpr, tpr,auc,f_name)


    return auc

def topFeatures(features, feature_importance):
    df = pd.DataFrame()
    df['importance'] = feature_importance
    df['features'] = features
    df_topf = df.sort_values('importance',ascending=False)
    return df_topf.iloc[0:10,:]
