#!/usr/local/bin
from __future__ import division
import os,sys
from sys import path
path.append(sys.path[0])
path.append(os.path.dirname(sys.path[0]))
import config
import db_construct
import getopt
def length_stat(connection,transcript_id_list):
    cursor=connection.cursor()
    sequence_length_list=[]
    gene_trans_dict={}
    for trans_id in transcript_id_list:
        sql_sequence="select transcript_seq,gene_name from main_table where transcript_id=%d" %(int(trans_id))
        cursor.execute(sql_sequence)
        sequence=cursor.fetchone()
        if len(sequence[0])>0:
            sequence_length_list.append(len(sequence[0]))
        else:
            print "****Error, %s is not found****"%(trans_id)
            sys.exit(1)
        transcript_number=gene_trans_dict.get(sequence[1],0)
        gene_trans_dict[sequence[1]]=transcript_number+1
    #statistics
    sequence_length_list.sort()
    seq_number=len(sequence_length_list)
    n50_num=int(round(seq_number*0.5))-1
    n90_num=int(round(seq_number*0.1))-1
    N50=sequence_length_list[n50_num]
    N90=sequence_length_list[n90_num]
    Average=int(round(sum(sequence_length_list)/len(sequence_length_list)))
    return N50,N90,Average,gene_trans_dict
def gene_stat(count_dict):
    trans_nd={}
    all_value=count_dict.values()
    all_value.sort()
    all_value_set=set(all_value)
    for tn in all_value_set:
        num=all_value.count(tn)
        trans_nd[tn]=num
    average=sum(all_value)/len(count_dict.keys())
    return average,trans_nd
#---------------------------------------------------------------------------------------------------------------------------------#
#________________________________________archieve mysql connection information and create connection______________________________#
if __name__=="__main__":
    opts,arg=getopt.getopt(sys.argv[1:],"o:i:c:t:")
    output="transcripts_stat.txt"
    script_loc=os.path.split(os.path.realpath(sys.argv[0]))[0]
    out_ident=float(0)
    out_coverage=float(0)
    orftype=False
    for i,a in opts:
        if i in ("-o"):
            output=a
        if i in ("-i"):
            out_ident=float(a)
        if i in ("-c"):
            out_coverage=float(a)
        if i in ("-t"):
            orftype=a
    if orftype=="False":
        orftype=False
    else:
        orftype_list=orftype.split(",")
    fout=open(output,'w')
    host=config.host
    user=config.username
    pw=config.password
    db=config.db
    connection=db_construct.create_conn_db(host,user,pw,db)
    cursor=connection.cursor()
    #raw
    seq_list=[]
    sql_main_table_id="select transcript_id from main_table;"
    cursor.execute(sql_main_table_id)
    for t_id in cursor.fetchall():
        seq_list.append(t_id[0])
    raw_N50,raw_N90,raw_len_AVERAGE,raw_count_dict=length_stat(connection,seq_list)
    raw_gene_average,raw_gene_trans_count=gene_stat(raw_count_dict)

    #orf_find
    seq_list=[]
    sql_orf_find_id="select transcript_id,primer_style from orf_find;"
    cursor.execute(sql_orf_find_id)
    for t_id,primer_style in cursor.fetchall():
        if orftype:
            if primer_style in orftype_list:
                seq_list.append(t_id)
        else:
            seq_list.append(t_id)
    seq_list=list(set(seq_list))
    t_N50,t_N90,t_len_AVERAGE,t_count_dict=length_stat(connection,seq_list)
    t_gene_average,t_gene_trans_count=gene_stat(t_count_dict)
    #clean
    seq_list=[]
    sql_usearch_id="select transcript_id,indent,coverage from usearch;"
    cursor.execute(sql_usearch_id)
    for u_id,indent,coverage in cursor.fetchall():
        if indent>=out_ident*100 and coverage>=out_coverage*100:
            if orftype:
                type_sql="select primer_style from orf_find where transcript_id=%d;"%(u_id)
                cursor.execute(type_sql)
                if cursor.fetchone()[0] in orftype_list:
                    seq_list.append(u_id)
            else:
                seq_list.append(u_id)
    seq_list=list(set(seq_list))
    u_N50,u_N90,u_len_AVERAGE,u_count_dict=length_stat(connection,seq_list)
    u_gene_average,u_gene_trans_count=gene_stat(u_count_dict)
    #output
    fout.write("length distribution of transcripts\n")
    fout.write("-"*100+"\n")
    fout.write("length_distribution\ttranscripts_inputted\ttranscripts_having_CDS\ttranscripts_having_homologous_AA\n")
    fout.write("mean\t"+str(raw_len_AVERAGE)+"\t"+str(t_len_AVERAGE)+"\t"+str(u_len_AVERAGE)+"\n")
    fout.write("N50\t"+str(raw_N50)+"\t"+str(t_N50)+"\t"+str(u_N50)+"\n")
    fout.write("N90\t"+str(raw_N90)+"\t"+str(t_N90)+"\t"+str(u_N90)+"\n\n")
#
    fout.write("gene count\n")
    fout.write("-"*100+"\n")
    lock_file=script_loc+"/lock.txt"
    fopen_lock=open(lock_file,'r')
    lock_n=fopen_lock.readline()
    if int(lock_n)==0:
        fout.write("No information due to the lack of 'gene list'.")
        sys.exit(1)
    else:
        pass
    fout.write("the_count_of_transcripts_genes\ttranscripts_inputted\ttranscripts_having_CDS\ttranscripts_having_homologous_AA\n")
    all_keys=raw_gene_trans_count.keys()+t_gene_trans_count.keys()+u_gene_trans_count.keys()
    all_keys.sort()
    nums=set(all_keys)
    fout.write("average_transcripts_per_gene\t"+str(round(raw_gene_average,3))+"\t"+str(round(t_gene_average,3))+"\t"+str(round(u_gene_average,3))+"\n")
    for num in nums:
        if num==1:
            fout.write("genes_including_%d_transcript\t"%(num))
            fout.write(str(raw_gene_trans_count.get(num,0)))
            fout.write("\t")
            fout.write(str(t_gene_trans_count.get(num,0)))
            fout.write("\t")
            fout.write(str(u_gene_trans_count.get(num,0)))
            fout.write("\n")
        else:
            fout.write("genes_including_%d_transcripts\t"%(num))
            fout.write(str(raw_gene_trans_count.get(num,0)))
            fout.write("\t")
            fout.write(str(t_gene_trans_count.get(num,0)))
            fout.write("\t")
            fout.write(str(u_gene_trans_count.get(num,0)))
            fout.write("\n")
