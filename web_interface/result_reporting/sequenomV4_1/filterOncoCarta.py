import sys
import optparse
import pandas as pd

def filter(input, output, sample):
	mutation_df = pd.read_csv(input, sep='\t', skiprows=14)

	#mutation_df = mutation_df.iloc[:,0:mutation_df.shape[1]-1]

	sample_df = pd.read_csv(sample, sep='\t', header=None)
	result=pd.DataFrame(columns=mutation_df.columns)

	## remove rows where mutation and allele are same
	mutation_df = mutation_df[mutation_df['Mutation']!=mutation_df['Allele']]

	for index, row in sample_df.iterrows():
		sample = row[0]
		genes = row[1].split(',')
		for gene in genes:
			result_line = mutation_df[ (mutation_df['Sample']==sample ) & (mutation_df['Gene']==gene)]
			if result_line.shape[0] >= 1:
				result = result.append(result_line)
			else:
				result = result.append(pd.Series([sample,gene,'WT',' ',' ',' ',' ',' ',' ',' ',' '], index=mutation_df.columns), ignore_index=True)
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
	print ("python filterOncoCarta.py -h for help")
