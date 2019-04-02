import sys
import optparse
import pandas as pd

def filter(input, output):
	df = pd.read_csv(input,sep=',')
	filter=[]
	for indx,row in df.iterrows():
		for gene in df.columns[2:len(df.columns)-3]:
			if "MUTATION" in row[gene]:
				filter.append([row['Sample'],
				gene, \
				row[gene],\
				row[gene].split(' ')[1],\
				row[gene].split(' ')[2]\
				])
	df_filter = pd.DataFrame(filter)
	df_filter.columns=['Sample','Gene','Mutation','Mutation-Frequency','Z-Score' ]
	df_filter.to_csv(output,index=False)


if len(sys.argv) > 1:
	parser = optparse.OptionParser()
	parser.add_option('-I', '--input',
	help = 'input mutation list csv file')
	parser.add_option('-o', '--output',
	help = 'output file')
	options,args = parser.parse_args()
	input = options.input
	output = options.output
	filter(input, output)
else:
	print ("python filterSequenom.py -h for help")
