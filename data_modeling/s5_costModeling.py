import sys
import pandas as pd
import basemodel as bm
from sklearn.model_selection import train_test_split

df = pd.read_csv("d5_after_impute_final_datamat.csv",low_memory=False)

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


######## test back model
X_train, X_test, y_train, y_test = train_test_split( df_xmat.values, df_ymat_cat, test_size=0.33, random_state=0)

gb = bm.GradientBoostingClassifier(
                                learning_rate= 0.15,
                                loss= 'exponential',
                                max_depth= 4,
                                max_features= 10,
                                min_samples_leaf= 1,
                                min_samples_split= 2
                                )


gb.fit(X_train, y_train)
print(bm.modelMetrics(y_test,gb.predict(X_test),gb.predict_proba(X_test)))
bm.evaluateModel(gb,X_test,y_test,True,"Method_1_Final")

### get probabilities from the trained model
gb_probs = gb.predict_proba(df_xmat.values)
gb_probs = gb_probs[:, 1]



dfle = pd.read_csv("LE_GovtData.csv")
dfsavings = pd.read_csv("Savings_PaperData.csv")


COST_PHPT_SCREENING = 99.35
result =[]
for indx,row in df.iterrows():
    age = int(row["AGE"])
    sex = "Female"
    if int(row["SEX_M"]) == 1 : sex = "Male"

    if ( (sex=="Female" and age >=42) | (sex=="Male" and age >=38)):

        life_expect = int(dfle[(dfle["age"]==age) & (dfle["Sex"] == sex)]["Life_expectancy"].values[0])

        cost_savings = dfsavings[dfsavings["Life_Expectancy"]==life_expect]["Cost_Savings"].values[0]

        exp_cost_savings =  (float(cost_savings) * gb_probs[indx] ) - (COST_PHPT_SCREENING* (1.0-gb_probs[indx]))

        result.append([row["MRN"],row["PTH"],row["max_CA"],age,sex,life_expect, cost_savings,gb_probs[indx],exp_cost_savings])

df_result = pd.DataFrame(result)
df_result.columns=['mrn','pth','max_CA','age','sex','life_expect','cost_savings','model_probability','exp_cost_savings']
df_result.to_csv("Cost_Result.csv",index=False)
