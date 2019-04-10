import sys
import optparse
import pandas as pd
import numpy as np

def calcLogR(df):
	for indx,row in df.iterrows():
		if(row['Percent_Ratio']<0.0025):
			df.at[indx,'BCR_LR_MIN']=-1.0
		elif(row['Percent_Ratio'] != row['Percent_Ratio'] ):
			df.at[indx,'BCR_LR_MIN']=-1.0
		else:
			df.at[indx,'BCR_LR_MIN']=2-np.log10(float(row['Percent_Ratio']))



def filter(input, output):

	df_control = pd.read_csv(input, skiprows=12,nrows=3)
	df_control.columns = ['Well', 'Control Name', 'ABL1_Ct', 'BCR-ABL1_minor_Ct',
	   'ABL1_Copies/qPCR', 'BCR-ABL1_minor_copies/qPCR', 'Percent_Ratio',
	   'MI_Comment']
	df_control['BCR_LR_MIN']=''
	df_sample = pd.read_csv(input, skiprows=18)
	df_sample.columns = ['Well', 'Specimen Name', 'ABL1_Ct', 'BCR-ABL1_minor_Ct',
	   'ABL1_Copies/qPCR', 'BCR-ABL1_minor_copies/qPCR', 'Percent_Ratio',
	   'MI_Comment']
	df_sample['BCR_LR_MIN']=''


	calcLogR(df_control)
	calcLogR(df_sample)


	original_file= open(input,'r')
	revised_file = open(output,'w')

	lcount=1
	for aline in original_file:
		if lcount >12:
			break
		revised_file.write(aline)
		lcount +=1

	original_file.close()
	revised_file.close()

	df_control.to_csv(output, mode='a', header=True,index=False)

	r1=[]
	r1.append(['','','','','','','','',''])
	r1.append(['Sample_Information:','','','','','','','',''])
	df_r1= pd.DataFrame(r1,columns=df_control.columns)
	df_r1.to_csv(output, mode='a', header=False,index=False)


	df_sample.to_csv(output, mode='a', header=True,index=False)



if len(sys.argv) > 1:
	parser = optparse.OptionParser()
	parser.add_option('-i', '--input',
	help = 'input sample file')
	parser.add_option('-o', '--output',
	help = 'output file')
	options,args = parser.parse_args()
	input = options.input
	output = options.output
	filter(input, output)
else:
	print ("python filterBCRABL.py -h for help")
