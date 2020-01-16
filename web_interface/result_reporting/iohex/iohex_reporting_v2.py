import sys
import cx_Oracle as orc
import os
import glob
import pandas as pd
import numpy as np
import decimal
from scipy.stats import linregress
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import warnings
warnings.filterwarnings("ignore")

def gettaskList(taskListID):
    soft = pd.read_csv("/var/www/html/softConfig.ini", header = None)
    con = orc.connect(soft.iloc[0,0].split('=')[1])
    cur = con.cursor()
    query =  " SELECT "
    cur.execute(query,(taskListID,))
    taskList = []
    for row in cur:
        taskList.append([x for x in row])
    con.close()
    if len(taskList) != 0:
        df_taskList = pd.DataFrame(taskList)
        df_taskList.columns = ['Tasklist_Number','LAST_NAME','FIRST_NAME','MIDDLE_INITIAL','MRN','OrderID','TEST_ID','RESULT','GROUP_TEST_ID','COLLECT_DT','RECEIVE_DATE','BARCODE']
        df_taskList['Blank1'] = "N/A"
        df_taskList['Blank2'] = "N/A"
        df_taskList['Blank3'] = "N/A"
        df_taskList['Blank4'] = "N/A"
        df_taskList['Blank5'] = "N/A"
        df_taskList['Blank6'] = "N/A"
        df_taskList.drop_duplicates(subset=['TEST_ID','Tasklist_Number'], keep='first',inplace=True)
        df_taskList['Name'] = "full_name"
        for t_num in df_taskList['Tasklist_Number'].unique():
            full_name = ""
            if df_taskList[df_taskList['Tasklist_Number']==t_num]['FIRST_NAME'].values[0] != None : full_name = df_taskList[df_taskList['Tasklist_Number']==t_num]['FIRST_NAME'].values[0]
            if df_taskList[df_taskList['Tasklist_Number']==t_num]['MIDDLE_INITIAL'].values[0] != None : full_name = full_name+' '+ df_taskList[df_taskList['Tasklist_Number']==t_num]['MIDDLE_INITIAL'].values[0]
            if df_taskList[df_taskList['Tasklist_Number']==t_num]['LAST_NAME'].values[0] != None : full_name = full_name+' '+ df_taskList[df_taskList['Tasklist_Number']==t_num]['LAST_NAME'].values[0]
            df_taskList.ix[df_taskList['Tasklist_Number']==t_num,['Name']] = full_name
        updated_columns = ['COLLECT_DT','TEST_ID','Tasklist_Number','Name','OrderID','BARCODE','Blank1','Blank2','Blank3','Blank4','Blank5','Blank6','RESULT']
        df_taskList = df_taskList[updated_columns]
        df_taskList.columns = ['Date','Compound','Patient#','Name','Order#','Filename','Blank1','Blank2','Blank3','Blank4','Blank5','Blank6','Calculated Amt']
        # df_taskList.sort_values('Date').drop_duplicates('Compound',keep='last')
        return (1,df_taskList)
    else :
        print "--------------------- Error: TaskListID '"+ taskListID + "' not found in the SoftLab database !"
        print "--------------------- Make sure TaskListID is correct."
        return (0,0)

def addData(df_taskList):
    orders = df_taskList["Order#"].unique()
    df_result = pd.DataFrame(columns = df_taskList.columns)
    for order in orders:
        df = df_taskList.loc[df_taskList["Order#"]==order,:]
        DATE = df['Date'].values[0]
        PATIENT_NUMBER = df['Patient#'].values[0]
        PATIENT_NAME = df['Name'].values[0]
        ORDER_NUMBER = df['Order#'].values[0]
        FILENAME = df['Filename'].values[0]
        if checkNonNumeric(df):
            print "--------------------- Skipped: %s %s , Non numeric value in the database! "% (PATIENT_NAME,ORDER_NUMBER)
            continue
        IOHT1=float(df.loc[df['Compound']=='IOHT1',:]['Calculated Amt'].values[0])
        IOHT2=float(df.loc[df['Compound']=='IOHT2',:]['Calculated Amt'].values[0])
        IOHT3=float(df.loc[df['Compound']=='IOHT3',:]['Calculated Amt'].values[0])
        IX120=float(df.loc[df['Compound']=='IX120',:]['Calculated Amt'].values[0])
        IX180=float(df.loc[df['Compound']=='IX180',:]['Calculated Amt'].values[0])
        IX240=float(df.loc[df['Compound']=='IX240',:]['Calculated Amt'].values[0])
        LN120 = np.log(IX120/100.0)
        LN180 = np.log(IX180/100.0)
        LN240 = np.log(IX240/100.0)
        result = linregress([IOHT1,IOHT2,IOHT3], [LN120,LN180,LN240])
        IXSLP =result.slope
        IXINC = result.intercept
        IXEXP = np.exp(IXINC)
        IOCL  = 3236.0 * np.abs(IXSLP)/IXEXP
        df.loc[df.index.max() + 1,:] = [DATE,"LN120",PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,FILENAME,"N/A","N/A","N/A","N/A","N/A","N/A",LN120]
        df.loc[df.index.max() + 1,:] = [DATE,"LN180",PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,FILENAME,"N/A","N/A","N/A","N/A","N/A","N/A",LN180]
        df.loc[df.index.max() + 1,:] = [DATE,"LN240",PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,FILENAME,"N/A","N/A","N/A","N/A","N/A","N/A",LN240]
        df.loc[df.index.max() + 1,:] = [DATE,"IXSLP",PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,FILENAME,"N/A","N/A","N/A","N/A","N/A","N/A",IXSLP]
        df.loc[df.index.max() + 1,:] = [DATE,"IXINC",PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,FILENAME,"N/A","N/A","N/A","N/A","N/A","N/A",IXINC]
        df.loc[df.index.max() + 1,:] = [DATE,"IXEXP",PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,FILENAME,"N/A","N/A","N/A","N/A","N/A","N/A",IXEXP]
        df.loc[df.index.max() + 1,:] = [DATE,"IOCL",PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,FILENAME,"N/A","N/A","N/A","N/A","N/A","N/A",IOCL]
        df_result = pd.concat([df_result, df], axis=0)
    return df_result

def plotReport(df,pdf_path):
    orders = df["Order#"].unique()
    with PdfPages(pdf_path) as pdf:
        for order in orders:
            data_mat = df.loc[df["Order#"]==order,:]
            if checkNonNumeric(data_mat):continue
            x=data_mat.loc[ ( data_mat["Compound"]=="IOHT1") | (data_mat["Compound"]=="IOHT2") | (data_mat["Compound"]=="IOHT3"),:]["Calculated Amt"].values
            y=data_mat.loc[ ( data_mat["Compound"]=="LN120") | (data_mat["Compound"]=="LN180") | (data_mat["Compound"]=="LN240"),:]["Calculated Amt"].values
            rsqr= data_mat.loc[ data_mat["Compound"]=="IXR2",:]["Calculated Amt"].values[0]
            plt.figure()
            plt.xlim(100,280)
            plt.ylim(y.min()-1.0,y.max()+1.0)
            settitle= " %s, %s, %s " % ( str(data_mat.Date.unique()[0])[0:10], data_mat.Name.unique()[0] , order)
            plt.title(settitle)
            plt.ylabel("Ln(mg/mL")
            lab="R^2 = %s" %(rsqr)
            slope, intercept, r_value, p_value, std_err = linregress([np.float64(num) for num in x], [np.float64(num) for num in y])
            line = (slope*np.array([float(num) for num in x]))+intercept
            x = np.array([float(num) for num in x])
            fig = plt.plot(x, line, 'r',label=lab)
            plt.scatter(x,y, color="k", s=3.5)
            plt.legend()
            pdf.savefig()
            plt.close()

# def gettraceFinder(trace_finder_file):
#     trace_finder = pd.read_csv(trace_finder_file)
#     trace_finder_iohexol = trace_finder.loc[(trace_finder['Compound'] == 'iohexol')]
#     trace_finder_iohexol_data = trace_finder_iohexol.loc[trace_finder_iohexol['Filename'].str.isdigit(),:]
#     trace_finder_columns= ['Compound', 'Filename', 'Calculated Amt']
#     return trace_finder_iohexol_data.loc[:,trace_finder_columns]

def checkNonNumeric(df):
    for code in ['@FT', 'See Comment','.']:
        if code in df['Calculated Amt'].values or any(x is None for x in df['Calculated Amt'].values) :
            return True
    return False


path="/home/scratch/iohexol/"
taskListID = sys.argv[1]
taskList_Return = gettaskList(taskListID)

if taskList_Return[0] == 0:
    exit()
else:
    df_result = addData(taskList_Return[1])
    df_result.to_csv(path+"report/Iohexol_report_%s.csv" %(taskListID),index=False)
    plotReport(df_result,path+"report/Iohexol_report_%s.pdf" %(taskListID))
    print "--------------------- Program successfully completed."
