# -*- coding: utf-8 -*-
"""
Created on Fri Jul  6 08:25:51 2018

@author: tmhsxs240
"""
import os
import glob
import sys
import pandas as pd
import numpy as np
from scipy.stats import linregress


import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages



if len(sys.argv) != 2:
	print ( "\n-----------------------------------------------\n")
	print("\nProgram ERROR: Did not find date !")
	print ( "\n-----------------------------------------------\n")
else:
	date= sys.argv[1]
	path="/home/scratch/iohexol/"

	# remove all old files
	files = glob.glob(path + "report/*")
	for f in files:
		os.remove(f)

	#check if file exists
	if not os.path.exists(path +"tracefinder/Iohexol_tracefinder_%s.csv"%(date)):
		print ( "\n-----------------------------------------------\n")
		print("File not found Iohexol_tracefinder_%s.csv"%(date))
		print("\nProgram ERROR. ")
		print ( "\n-----------------------------------------------\n")
		exit()
	if not os.path.exists(path +"tasklist/Iohexol_tasklist_%s.txt" %(date)):
		print ( "\n-----------------------------------------------\n")
		print("File not found Iohexol_tasklist_%s.txt" %(date))
		print("\nProgram ERROR. ")
		print ( "\n-----------------------------------------------\n")
		exit()


    # process tracefinder file
	trace_finder = pd.read_csv(path +"tracefinder/Iohexol_tracefinder_%s.csv"%(date))
	trace_finder_iohexol = trace_finder.loc[(trace_finder['Compound'] == 'iohexol')]
	trace_finder_iohexol_data = trace_finder_iohexol.loc[trace_finder_iohexol['Filename'].str.contains("100",regex=True),:]
	trace_finder_columns= ['Compound', 'Filename', 'Calculated Amt']
	trace_finder_iohexol_data_filt = trace_finder_iohexol_data.loc[:,trace_finder_columns]



    # process tasklist file
	task_list = path +"tasklist/Iohexol_tasklist_%s.txt" %(date)
	iohs = ['IOHT1','IOHT2','IOHT3']
	task=[]
	with open(task_list) as f:
	    content = f.readlines()
	    for line in content:
	      temp=[]
	      line.rstrip().split('\t')
	      newline = line.split()
	      if len(newline)>1:
	        if newline[0].isnumeric():
	          temp.append(newline[0])
	          temp.append(newline[1])
	          temp.append(newline[3])
	        elif len(newline)>5:
	          if 'Age' in newline[2]:
	            name = newline[1]+" " + newline[0]
	            temp.append(name)
	        elif newline[0] == 'DIR':
	          temp.append(newline[0])
	          temp.append(newline[1])
	        elif newline[0] in iohs:
	          temp.append(newline[0])
	          temp.append(newline[4])
	        elif newline[0] == 'BSA':
	          temp.append(newline[0])
	          temp.append(newline[2])
	        if len(temp)>0:
	          task.append(temp)


	# filter tasklist file to keep only required entries
	tasklist =[]
	for i  in range(len(task)):

	  if i > len(task)-11:
	    break

	  if task[i][0].isnumeric():
	    temp =[]
	    temp.append(task[i][0])
	    temp.append(task[i][1])
	    temp.append(task[i][2])
	    temp.append(task[i+1][0])
	    uniq_ids = np.unique([task[i+2][1],task[i+3][1],task[i+4][1],task[i+5][1],task[i+6][1]])

	    temp.append(uniq_ids[0])
	    temp.append(uniq_ids[1])
	    temp.append(uniq_ids[2])

	    temp.append(task[i+7][1])

	    temp.append(task[i+8][1])
	    temp.append(task[i+9][1])
	    temp.append(task[i+10][1])

	    tasklist.append(temp)


	### generate report
	entries =[]
	for task in tasklist:

	  PATIENT_NUMBER=task[0]
	  ORDER_NUMBER = task[1]
	  DATE = task[2]
	  PATIENT_NAME=task[3]
	  id1 = task[4][3:]
	  id2 = task[5][3:]
	  id3 = task[6][3:]

	  IOHT1=float(task[7])
	  IOHT2=float(task[8])
	  IOHT3=float(task[9])

	  BSA=float(task[10])

	  IX120=float(trace_finder_iohexol_data_filt.loc[trace_finder_iohexol_data_filt.Filename==id1,:]['Calculated Amt'].values[0])
	  IX180=float(trace_finder_iohexol_data_filt.loc[trace_finder_iohexol_data_filt.Filename==id2,:]['Calculated Amt'].values[0])
	  IX240=float(trace_finder_iohexol_data_filt.loc[trace_finder_iohexol_data_filt.Filename==id3,:]['Calculated Amt'].values[0])


	  LN120 = np.log(IX120/100.0)
	  LN180 = np.log(IX180/100.0)
	  LN240 = np.log(IX240/100.0)

	  result = linregress([IOHT1,IOHT2,IOHT3], [LN120,LN180,LN240])
	  IXSLP =result.slope
	  IXINC = result.intercept
	  IXR2 = result.rvalue **2

	  IXEXP = np.exp(IXINC)
	  IOCL  = 3236.0 * np.abs(IXSLP)/IXEXP

	  ICGFR = 0.990778*IOCL - 0.001218*np.power(IOCL,2)
	  NGFR = ICGFR/BSA*1.73

	  entries.append([DATE,'IOHT1',PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,id1,'N/A','N/A','N/A','N/A','N/A','N/A',IOHT1])
	  entries.append([DATE,'IOHT2',PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,id1,'N/A','N/A','N/A','N/A','N/A','N/A',IOHT2])
	  entries.append([DATE,'IOHT3',PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,id1,'N/A','N/A','N/A','N/A','N/A','N/A',IOHT3])
	  entries.append([DATE,'IX120',PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,id1,'N/A','N/A','N/A','N/A','N/A','N/A',IX120])
	  entries.append([DATE,'IX180',PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,id2,'N/A','N/A','N/A','N/A','N/A','N/A',IX180])
	  entries.append([DATE,'IX240',PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,id3,'N/A','N/A','N/A','N/A','N/A','N/A',IX240])
	  entries.append([DATE,'LN120',PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,id3,'N/A','N/A','N/A','N/A','N/A','N/A',LN120])
	  entries.append([DATE,'LN180',PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,id3,'N/A','N/A','N/A','N/A','N/A','N/A',LN180])
	  entries.append([DATE,'LN240',PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,id3,'N/A','N/A','N/A','N/A','N/A','N/A',LN240])
	  entries.append([DATE,'IXSLP',PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,id3,'N/A','N/A','N/A','N/A','N/A','N/A',IXSLP])
	  entries.append([DATE,'IXINC',PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,id3,'N/A','N/A','N/A','N/A','N/A','N/A',IXINC])
	  entries.append([DATE,'IXR2',PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,id3,'N/A','N/A','N/A','N/A','N/A','N/A',IXR2])
	  entries.append([DATE,'IXEXP',PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,id3,'N/A','N/A','N/A','N/A','N/A','N/A',IXEXP])
	  entries.append([DATE,'IOCL',PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,id3,'N/A','N/A','N/A','N/A','N/A','N/A',IOCL])
	  entries.append([DATE,'ICGFR',PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,id3,'N/A','N/A','N/A','N/A','N/A','N/A',ICGFR])
	  entries.append([DATE,'BSA',PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,id3,'N/A','N/A','N/A','N/A','N/A','N/A',BSA])
	  entries.append([DATE,'NGFR',PATIENT_NUMBER,PATIENT_NAME,ORDER_NUMBER,id3,'N/A','N/A','N/A','N/A','N/A','N/A',NGFR])


	entries_df = pd.DataFrame(entries)
	entries_df.columns = ['Date','Compound', 'Patient#',"Name",'Order#','Filename','Blank1','Blank2','Blank3','Blank4','Blank5','Blank6','Calculated Amt']
	entries_df.to_csv(path+"report/Iohexol_report_%s.csv" %(date),index=False)



	orders = entries_df["Order#"].unique()

	with PdfPages(path +"report/Iohexol_report_%s.pdf" %(date)) as pdf:
		for order in orders:
			data_mat = entries_df.loc[entries_df["Order#"]==order,:]
			x=data_mat.loc[ ( data_mat["Compound"]=="IOHT1") | (data_mat["Compound"]=="IOHT2") | (data_mat["Compound"]=="IOHT3"),:]["Calculated Amt"].values
			y=data_mat.loc[ ( data_mat["Compound"]=="LN120") | (data_mat["Compound"]=="LN180") | (data_mat["Compound"]=="LN240"),:]["Calculated Amt"].values
			rsqr= data_mat.loc[ data_mat["Compound"]=="IXR2",:]["Calculated Amt"].values[0]
			rsqr=round(rsqr,4)

			plt.figure()
			plt.xlim(100,280)
			plt.ylim(-3,0)
			settitle= " %s, %s, %s " % ( data_mat.Date.unique()[0] , data_mat.Name.unique()[0] , order)
			plt.title(settitle)
			plt.xlabel("Time")
			plt.ylabel("Ln(mg/mL")
			lab="R^2 = %s" %(rsqr)
			#fig=plt.plot(x,y,'-ro',)


			slope, intercept, r_value, p_value, std_err = linregress(x, y)

			line = slope*x+intercept
			fig = plt.plot(x, line, 'r',label=lab)
			plt.scatter(x,y, color="k", s=3.5)

			plt.legend()

			pdf.savefig()
			plt.close()

	os.remove(path +"tracefinder/Iohexol_tracefinder_%s.csv"%(date));
	os.remove(path +"tasklist/Iohexol_tasklist_%s.txt" %(date));

	print ( "\n-----------------------------------------------\n")
	print("Report generated as ")
	print("Iohexol_report_%s.csv" %(date))
	print("Iohexol_graph_%s.pdf" %(date))
	print("\n Please download the report !")
	print ( "\n-----------------------------------------------\n")
