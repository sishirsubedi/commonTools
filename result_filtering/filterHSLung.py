import sys
import optparse
import pandas as pd

def filter(input, output,sample):
	df = pd.read_csv(input,sep=',')
	filter=[]
	for indx,row in df.iterrows():
		for gene in df.columns[2:len(df.columns)-3]:
			if "MUTATION" in row[gene]:
				filter.append([ \
				row['Sample'],
				gene.split('#')[0],\
				gene, \
				row[gene],\
				row[gene].split(' ')[1],\
				row[gene].split(' ')[2]\
				])
	df_filter = pd.DataFrame(filter)
	df_filter.columns=['Sample','Gene','Gene-Mutation','Mutation-Values','Mutation-Frequency','Z-Score' ]

	df_sample = pd.read_csv(sample, sep='\t', header=None)
	result=pd.DataFrame(columns=df_filter.columns)

	for index, row in df_sample.iterrows():
		sample = row[0]
		genes = row[1].split(',')
		for gene in genes:
			result_line = df_filter[ (df_filter['Sample']==sample ) & (df_filter['Gene']==gene)]
			if result_line.shape[0] >= 1:
				result = result.append(result_line)
			else:
				result = result.append(pd.Series([sample,gene,'WT',' ',' ',' '], index=df_filter.columns), ignore_index=True)
	result.to_csv(output,index=False)


if len(sys.argv) > 1:
	parser = optparse.OptionParser()
	parser.add_option('-I', '--input',
	help = 'input mutation list csv file')
	parser.add_option('-o', '--output',
	help = 'output file')
	parser.add_option('-s', '--sample',
	help = 'sample and genes ordered file')
	options,args = parser.parse_args()
	input = options.input
	output = options.output
	sample = options.sample
	filter(input, output, sample)
else:
	print ("python filterSequenom.py -h for help")
