from __future__ import division
#!/usr/local/bin
import os.path
import string
import sys,getopt
def reverse_sequence(sequence):  
    li = list(sequence)
    li.reverse()  
    reverse_seq = "".join(li)  
    return reverse_seq  
def reverse_comple(sequence):
    trans_dict=string.maketrans('ATCG','TAGC')
    comple_sequence=sequence.translate(trans_dict)
    result_sequence=reverse_sequence(comple_sequence)
    return result_sequence
def create_frame(input_seq):
    result_dict={}
    #plus strand
    result_dict["plus_0"]=input_seq
    result_dict["plus_1"]=input_seq[1:]
    result_dict["plus_2"]=input_seq[2:]
    #minus strand
    rev_com=reverse_comple(input_seq)
    result_dict["minus_0"]=rev_com
    result_dict["minus_1"]=rev_com[1:]
    result_dict["minus_2"]=rev_com[2:]
    return result_dict
def location_translate(orf_list,frame_type,strand,sequence_length_fact):
    for orf in orf_list:
        orf[0]=orf[0]+frame_type
        orf[1]=orf[1]+frame_type
        orf[4]=orf[4]+frame_type
        orf[5]=orf[5]+frame_type
        if strand=='+':
            pass
        else:
            orf[0]=sequence_length_fact-orf[0]
            orf[1]=sequence_length_fact-orf[1]
            orf[4]=sequence_length_fact-orf[4]
            orf[5]=sequence_length_fact-orf[5]
            start=orf[1]
            orf[1]=orf[0]
            orf[0]=start
            start4=orf[4]
            orf[4]=orf[5]
            orf[5]=start4
    return orf_list
def findorf_one_frame(line_seq,start_codons_list,end_codons_list,min_len_orf,strand,frame_type,sequence_length_fact):
    line_seq=line_seq.upper()
    kmer_dict={}
    seq_length=len(line_seq)
    orf_list=[]
    orf_type=0
    for n in range(int(seq_length/3)):
        loc_first=n*3
        current_kmer=line_seq[loc_first:loc_first+3]
        try:
            kmer_dict[current_kmer].append(loc_first)
        except:
            kmer_dict[current_kmer]=[loc_first]
    #all end codons find
    end_loc_list_all=[]
    for end_codon in end_codons_list:
        end_loc_list=kmer_dict.get(end_codon,[])
        end_loc_list_all=end_loc_list_all+end_loc_list
    #all start codons find
    start_loc_list_all=[]
    for start_codon in start_codons_list:
        start_loc_list=kmer_dict.get(start_codon,[])
        start_loc_list_all=start_loc_list_all+start_loc_list
    #orf find
    if len(end_loc_list_all)>0:
        first_end=min(end_loc_list_all)
        end_loc_list_all.remove(first_end)
        if first_end+3>min_len_orf:
            longest_sequence=[0,first_end+3]
            if line_seq[0:3] in start_codons_list:
                orf_type=3+5
                orf_list.append([0,first_end+3,strand,orf_type]+longest_sequence)
                start_loc_list_all.remove(min(start_loc_list_all))
            else:
                orf_type=3
                orf_list.append([0,first_end+3,strand,orf_type]+longest_sequence)
        while len(start_loc_list_all)>0:
            if min(start_loc_list_all)<first_end:
                start_loc=min(start_loc_list_all)
                start_loc_list_all.remove(start_loc)
                if first_end+3-start_loc>min_len_orf: #not include the last on
                    orf_type=3+5
                    orf_list.append([start_loc,first_end+3,strand,orf_type]+longest_sequence)
                else:
                    continue
            else:
                break
        while len(end_loc_list_all)>0:
            inter_end=min(end_loc_list_all)
            end_loc_list_all.remove(inter_end)
            try:
                current_min_start=min(start_loc_list_all)
                if inter_end+3-current_min_start>min_len_orf:
                    orf_type=3+5
                    orf_list.append([current_min_start,inter_end+3,strand,orf_type]+[current_min_start,inter_end+3])
            except:
                pass
            if len(start_loc_list_all)>0:
                min_start=min(start_loc_list_all)
                while min_start<inter_end:
                    start_loc_list_all.remove(min_start)
                    if len(start_loc_list_all)>0:
                        min_start=min(start_loc_list_all)
                    else:
                        break
        try:
            last_orf_start=min(start_loc_list_all)
            if seq_length-last_orf_start>min_len_orf:
                end_loc=int(seq_length/3)*3
                orf_type=3
                orf_list.append([last_orf_start,end_loc,strand,orf_type]+[last_orf_start,end_loc])
        except:
            pass
    else:
        if len(start_loc_list_all)>0:
            start_loc=min(start_loc_list_all)
            end_loc=int(seq_length/3)*3
            if end_loc-start_loc>min_len_orf:
                orf_type=5
                orf_list.append([start_loc,end_loc,strand,orf_type]+[start_loc,end_loc])
            elif start_loc>min_len_orf:
                orf_type=0
                orf_list.append([start_loc,end_loc,strand,orf_type]+[start_loc,end_loc])
        else:
            if int(seq_length/3)*3>min_len_orf:
                orf_type=0
                end_loc=int(seq_length/3)*3
                orf_list.append([0,end_loc,strand,orf_type]+[0,end_loc])
    orf_list=location_translate(orf_list,frame_type,strand,sequence_length_fact)
    return orf_list
def read_genome(genome_file):
    genome_file_opened=open(genome_file,"r")
    genome_dict={}
    first=True
    for line_seq in genome_file_opened:
        line_seq=line_seq.strip()
        if line_seq.startswith(">"):
            if first:
                chr_name=line_seq.strip(">")      
                seq=""
                first=False
            else:
                genome_dict[chr_name]=seq
                chr_name=line_seq.strip(">") 
                seq=""
        else:
            seq=seq+line_seq.strip()
    genome_dict[chr_name]=seq
    return genome_dict
def main_exe(sequence,start_list,end_list,min_len_orf):
    sequence=sequence.strip()
    sequence_length=len(sequence)
    frame6_dict=create_frame(sequence)
    all_orf_result={}
    for frame_one in frame6_dict:
        strand_list=frame_one.split('_')
        if strand_list[0]=="plus":
            strand="+"
            frame_type=int(strand_list[1])
        elif strand_list[0]=="minus":
            strand="-"
            frame_type=int(strand_list[1])
        line_seq=frame6_dict[frame_one]
        result_list=findorf_one_frame(line_seq,start_list,end_list,min_len_orf,strand,frame_type,sequence_length)
        all_orf_result[frame_one]=result_list
    return all_orf_result
def export_result(sequence_name,sequence,orf_result,fout_bed,sequence_file):
    if sequence_file:
        fout_fasta=open(sequence_file,'w')
    orf_count=0
    for frame in orf_result:
        for result_one in orf_result[frame]:
            orf_count=orf_count+1
            fout_bed.write(sequence_name+"\t"+str(0)+"\t"+str(len(sequence))+"\t")
            fout_bed.write(frame+"\t"+str(result_one[0])+"\t"+str(result_one[1])+"\t"+str(result_one[4])+"\t"+str(result_one[5])+"\t"+result_one[2]+"\t"+str(result_one[3])+"\n")
            if sequence_file:
                orf_name='_'.join([sequence_name,frame,str(result_one[0]),str(result_one[1])])
                orf_sequence_strand=sequence[int(result_one[0]):int(result_one[1])]
                if result_one[2]=='+':
                    orf_sequence=orf_sequence_strand
                elif result_one[2]=='-':
                    orf_sequence=reverse_comple(orf_sequence_strand)
                else:
                    print "Error"
                fout_fasta.write(orf_name+'\n')
                fout_fasta.write(orf_sequence+'\n')
    return orf_count
if __name__=="__main__":
    useage='''
    -h/--help

    -i/--input_file <fasta>	the inputted fasta file.

    -b/--bed <file>	to output bed file. (default: orfs.bed)

    -s/--starts <string>	starts codons, split by comma. (default: ATG)

    -e/--ends <string>	ends codons, split by comma. (default: TAA,TAG,TGA)

    -l/--min_length	minimum ORF length to output. (default: 100)

    -f/--fasta	to output ORF sequence into fasta file.
'''
    opts,arg=getopt.getopt(sys.argv[1:],"hi:b:s:e:l:f:",["help","input_file=","bed=","starts=","ends=","min_length=","fasta="])
    parameters=[a[0] for a in opts]
    if '-h' in parameters or '--help' in parameters:
        print useage
        sys.exit(1)
    if len(parameters)==0:
        print useage
        sys.exit(1)
    if '-i' not in parameters and '--input_file' not in parameters:
        print useage
        sys.exit(1)
    script_loc=os.path.split(os.path.realpath(sys.argv[0]))[0]
    outbed='orfs.bed'
    min_length=100
    start_codons="ATG"
    end_codons="TAA,TAG,TGA"
    fasta_file=script_loc+'/orf_finder.orf.fa'
    for i,a in opts:
        if i in ("-i","--input_file"):
            inputfile=a
        if i in ("-b","--bed"):
            outbed=a
        if i in ("-s","--starts"):
            start_codons=a
        if i in ("-e","--ends"):
            end_codons=a
        if i in ("-l","--min_length"):
            min_length=int(a)
        if i in ("-f","--fasta"):
            fasta_file=a
    start=start_codons.strip().split(',')
    end=end_codons.strip().split(',')
    fout_bed=open(outbed,'w')
    count_init=0
    line_seq_dict=read_genome(inputfile)
    orf_num_all=0
    for seq_name in line_seq_dict:
        count_init=count_init+1
        sequence=line_seq_dict[seq_name]
        sequence=sequence.strip()
        result=main_exe(sequence,start,end,min_length)
        orf_num=export_result(seq_name,sequence,result,fout_bed,fasta_file)
        orf_num_all=orf_num_all+orf_num
    print "all of ORFs: %d" %(orf_num_all)
