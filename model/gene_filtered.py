#!/usr/local/bin
from __future__ import division
import os,sys
from sys import path
path.append(sys.path[0])
path.append(os.path.dirname(sys.path[0]))
import config
import db_construct
import getopt
if __name__=="__main__":
    opts,arg=getopt.getopt(sys.argv[1:],"o:i:c:t:")
    output="filtered_gene_list.txt"
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
    retain_transcript=[]
    sql_retain_trans="select transcript_id,indent,coverage from usearch;"
    cursor.execute(sql_retain_trans)
    for trans,indent,coverage in cursor.fetchall():
        if float(indent)>=float(out_ident*100) and float(coverage)>=float(out_coverage*100):
            if orftype:
                type_sql="select primer_style from orf_find where transcript_id=%d;"%(trans)
                cursor.execute(type_sql)
                if cursor.fetchone()[0] in orftype_list:
                    retain_transcript.append(trans)   
            else:
                retain_transcript.append(trans)   
    #
    all_gene=[]
    retain_gene=[]
    sql_main="select transcript_id,gene_name from main_table;"
    cursor.execute(sql_main)
    for transcript_id,gene_name in cursor.fetchall():
        all_gene.append(gene_name)
        if transcript_id in retain_transcript:
             retain_gene.append(gene_name)
    filter_gene=set(all_gene)-set(retain_gene)
    fout=open(output,"w")
    for line in filter_gene:
        fout.write(line+"\n")
    print ">>> Fltered genes list export completed!"
    print "The number of genes:",len(set(all_gene))
    print "fltered genes:",len(set(filter_gene))
    print "retained genes:",len(set(retain_gene))
