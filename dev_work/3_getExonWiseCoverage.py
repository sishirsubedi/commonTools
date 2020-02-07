import pandas as pd
import sys

sample = sys.argv[1]

file_in = sample + '-N.cardiac_intersect.bed'
file_out = sample + '-N.cardiac_result.txt'

df = pd.read_csv(file_in,sep='\t',header=None)
df.sort_values(by=[0, 1],inplace=True)

def searchGap(df):
    table = []
    current = 0
    tag = "temp"

    ### set exon number
    cds_start = int(df.iloc[0,1])
    exon = 1
    for estart in [int(x) for x in df.iloc[0,16].split(',') if x != '']:
        if cds_start > int(estart) and estart != '':
            exon += 1

    for indx,row in df.iterrows():

        if df.iloc[indx,3] >= 10 :
            tag = "high"
        else:
            tag = "low"

        start = df.iloc[indx,1]
        end = df.iloc[indx,2]

        if indx == 0: ## keep the first row
            table.append([df.iloc[indx,0],start,end,tag,df.iloc[indx,3],exon,df.iloc[indx,5],df.iloc[indx,6],df.iloc[indx,7],
            df.iloc[indx,8],df.iloc[indx,9],df.iloc[indx,10],df.iloc[indx,11],df.iloc[indx,12],df.iloc[indx,13],df.iloc[indx,14]])

        elif table[current][4]== 0: ## keep the zero gap region and move to next row
            table.append([df.iloc[indx,0],start,end,tag,df.iloc[indx,3],exon,df.iloc[indx,5],df.iloc[indx,6],df.iloc[indx,7],
            df.iloc[indx,8],df.iloc[indx,9],df.iloc[indx,10],df.iloc[indx,11],df.iloc[indx,12],df.iloc[indx,13],df.iloc[indx,14]])
            current += 1
        else:
            if indx+1 < df.shape[0]: ## if not the last row

                new_tag = "new_temp"
                if df.iloc[indx+1,3] >= 10 :
                    new_tag = "high"
                else:
                    new_tag = "low"

                if end == df.iloc[indx+1,1] and tag == new_tag: # next nt is adjacent and tag is also same then just change coordinate
                    table[current][2]=df.iloc[indx+1,2]
                    #update coverage as average coverage
                    table[current][4]= int(df[( (df[1]>=int(table[current][1])) & (df[2]<=int(table[current][2])) )][3].mean())

                elif end == df.iloc[indx+1,1] and tag != new_tag: # next nt is adjacent but tag is NOT same then change coordinate and tag BUT EXON is same
                    table.append([df.iloc[indx+1,0],df.iloc[indx+1,1],df.iloc[indx+1,2],
                    new_tag,df.iloc[indx+1,3],exon,df.iloc[indx+1,5],df.iloc[indx+1,6],df.iloc[indx+1,7],
                    df.iloc[indx+1,8],df.iloc[indx+1,9],df.iloc[indx+1,10],df.iloc[indx+1,11],df.iloc[indx+1,12],
                    df.iloc[indx+1,13],df.iloc[indx+1,14]])
                    current += 1
                elif end != df.iloc[indx+1,1]: # next nt is NOT adjacent then check for EXON
                    if df.iloc[indx+1,2] > df.iloc[indx,6] : ## found next exon
                        exon += 1
                        table.append([df.iloc[indx+1,0],df.iloc[indx+1,1],df.iloc[indx+1,2],
                        new_tag,df.iloc[indx+1,3],exon,df.iloc[indx+1,5],df.iloc[indx+1,6],df.iloc[indx+1,7],
                        df.iloc[indx+1,8],df.iloc[indx+1,9],df.iloc[indx+1,10],df.iloc[indx+1,11],df.iloc[indx+1,12],
                        df.iloc[indx+1,13],df.iloc[indx+1,14]])
                    elif df[ ( ( df[1] >=  df.iloc[indx,2]+1) & ( df[2] <=  df.iloc[indx+1,1]-1)  )  ].shape[0] == 0: ## same exon found gap
                        table.append([df.iloc[indx+1,0],df.iloc[indx,2],df.iloc[indx+1,1],
                        'low',0,exon,df.iloc[indx,5],df.iloc[indx,6],df.iloc[indx,7],
                        df.iloc[indx,8],df.iloc[indx,9],df.iloc[indx,10],df.iloc[indx,11],df.iloc[indx,12],
                        df.iloc[indx,13],df.iloc[indx,14]])
                    else: ## same exon found something else -- for confirmation
                        table.append([df.iloc[indx+1,0],df.iloc[indx+1,1],df.iloc[indx+1,2],
                        new_tag,df.iloc[indx+1,3],exon,df.iloc[indx+1,5],df.iloc[indx+1,6],df.iloc[indx+1,7],
                        df.iloc[indx+1,8],df.iloc[indx+1,9],df.iloc[indx+1,10],df.iloc[indx+1,11],df.iloc[indx+1,12],
                        df.iloc[indx+1,13],df.iloc[indx+1,14]])

                    current += 1

    return table



result = []
for gene in df[7].unique():
    df_genewise = df[df[7]==gene]
    df_genewise.reset_index(drop=True,inplace=True)
    res = searchGap(df_genewise)
    for row in res:
        result.append(row)

df_result = pd.DataFrame(result)
df_result.columns = ['chr','coding_start','coding_end','cov_status','coverage','exon_number','exon_start','exon_end','Gene','HMGD_RefSeq','strand','exonCount','txStart','txEnd','cdsStart','cdsEnd']
df_result.to_csv(file_out,sep='\t',index=False)
