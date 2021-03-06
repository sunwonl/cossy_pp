__author__ = 'SungJoonPark'

import os
import pandas as pd
import preprocess.icgc as icgc
import numpy as np
from subprocess import check_call


def ready_mutsigcv_for_generateHeat_from_mutsigcvoutput(mutsigcvoutput):
    #erase header, and filter Q value that is 0 to 1e-15
    df = pd.read_csv(mutsigcvoutput,sep="\t")
    df.loc[df['q']==0,'q'] = 1e-15
    df = df.fillna('NaN')
    outputfile = os.path.splitext(mutsigcvoutput)[0]+"_ready_for_generateHeat.txt"

    df.to_csv(outputfile,index=False,header=False,sep="\t")


def make_heatjsonfile_for_runHotnet2_from_icgc_using_mutation_option(icgc_mutation_file):
    #make mutation file for input of generateHeat, we should prepare minimum cnafile and snv file
    def dict_to_file(dict_, outputfile):
        w = open(outputfile,'w')
        for sample in dict_.keys():
            w.write(sample)
            w.write("\t")
            for gene in dict_[sample]:
                w.write(gene)
                w.write("\t")
            w.write("\n")
        w.close()

    def icgc_to_cnafile(df,outputfile):
        df = df[np.logical_or( (df['mutation_type'] =='insertion of <=200bp') , (df['mutation_type'] =='deletion of <=200bp'))]

        cna_dict = {}
        for idx, row in df.iterrows():
            sample = row['submitted_sample_id']
            gene = row['Gene Symbol']
            
            if sample not in cna_dict:
                if row['mutation_type'] == 'insertion of <=200bp':
                    cna_dict[sample]=[gene+"(A)"]
                elif row['mutation_type'] == 'deletion of <=200bp':
                    cna_dict[sample]=[gene+"(D)"]
            else:
                if row['mutation_type'] == 'insertion of <=200bp':
                    cna_dict[sample].append(gene+"(A)")
                elif row['mutation_type'] == 'deletion of <=200bp':
                    cna_dict[sample].append(gene+"(D)")

        dict_to_file(cna_dict, outputfile)

    def icgc_to_snvfile(df,outputfile):
        df = df[df['mutation_type'] =='single base substitution']
        snv_dict = {}
        for idx, row in df.iterrows():
            sample = row['submitted_sample_id']
            gene = row['Gene Symbol']
            if sample not in snv_dict:
                snv_dict[sample]=[gene]
            else:
                snv_dict[sample].append(gene)

        dict_to_file(snv_dict, outputfile)

    df = icgc.get_gene_named_added_icgc_mut_df(icgc_mutation_file)

    snv_outputfile = os.path.splitext(icgc_mutation_file)[0]+"_for_generateHeat.snv"
    cna_outputfile = os.path.splitext(icgc_mutation_file)[0]+"_for_generateHeat.cna"
    icgc_to_snvfile(df,snv_outputfile)
    icgc_to_cnafile(df,cna_outputfile)

    heatjson_outputfile = os.path.splitext(icgc_mutation_file)[0]+"_mutation_for_hotnet2.json"
    print "making snv ,cna file end. It is now to make json file"
    check_call(['python','Q:/COSSY+/tools/hotnet2/hotnet2-master/generateHeat.py','mutation','--snv_file',snv_outputfile,'--cna_file',cna_outputfile,"--output_file",heatjson_outputfile])

def hotnet2outputfile_to_gmtfile(hotnet2outputfile):
    gmtfile = os.path.splitext(hotnet2outputfile)[0]+".gmt"
    w = open(gmtfile,'w')
    with open(hotnet2outputfile,'r') as r:
        for i,line in enumerate(r):
            w.write(str(i)+"\t"+"hotnet2"+"\t"+line)
    w.close()

if __name__ == '__main__':
    # datasets =['COAD','STAD','PRAD','LUSC']
    # for dataset in datasets:
    #     icgc_mutation_file = "Q:/COSSY+/tools/hotnet2/hotnet2-master\data/ICGC_TCGA/"+ dataset+"/simple_somatic_mutation.open." +dataset+"-US.tsv"
    #     make_heatjsonfile_for_runHotnet2_from_icgc_using_mutation_option(icgc_mutation_file)
    hotnet2outputfile = "Q:\COSSY+/tools\hotnet2\hotnet2-master\hotnet_output\STAD\delta_0.00137960659199/components.txt"
    hotnet2outputfile_to_gmtfile(hotnet2outputfile)