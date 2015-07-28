import os,re,sys
from sys import path
path.append(sys.path[0])
import genetic_code_library
import getopt
def translate_dict(genetic_code):  #creating dna and protein dictionary for translation.
    code_dict={}
    seq_list=zip(genetic_code['base1'],genetic_code['base2'],genetic_code['base3'],genetic_code['AAS'])
    for line in seq_list:
        codes=''.join(line[0:3])
        code_dict[codes]=line[3]
    return code_dict
def translate_dna(code_dict,string):  #translating dna to protein
    protein_list=[]
    for n in range(len(string)/3):
        n=n*3
        substr=string[n:n+3]
        aa=code_dict.get(substr,'*')
        protein_list.append(aa)
    protein=''.join(protein_list)
    return protein
if '__main__'==__name__:
    useage='''
    useage: python standard_code.py -i <input> -o <output> [-g genetic code] [-t]
        -i input file, must be a fasta format file.
        -o output file, a fasta format file which will containing protein that translated from dna.
        -g genetic code, including standard, vertebrate_Mt, Ciliate, Euplotid, Plastid. default: standard code.
        -t if -t be given, terminal genetic will be translated.
    '''
    opts,arg=getopt.getopt(sys.argv[1:],"i:o:g:t")
    option_list=[]
    genetic_code='universal'
    terminal=True
    for i,a in opts:
        option_list.append(i)
        if i in ("-i"):
            input_fasta=a
        if i in ("-o"):
            outputfile=a
        if i in ("-g"):
            genetic_code=a 
        if i in ("-t"):
            terminal=False            
    if '-i' not in option_list or '-o' not in option_list:
        print useage
        sys.exit(1)
    code_dict=genetic_code_library.code_dict
    standard=code_dict[genetic_code]
    fout=open(outputfile,'w')
    genetic_dict=translate_dict(standard)
    for line in open(input_fasta,'r'):
        if line.startswith('>'):
            sequence_name=line.strip()+'.protein'+'\n'
        else:
            protein=translate_dna(genetic_dict,line.strip())
            protein=protein.strip('M')
            if not terminal:
                protein=protein.strip('*')
            fout.write(sequence_name)
            fout.write(protein+'\n')
    print "translation complete."
    fout.close()
