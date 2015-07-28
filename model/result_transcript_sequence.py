import os,sys
from sys import path
path.append(sys.path[0])
path.append(os.path.dirname(sys.path[0]))
import config
import db_construct
import getopt
opts,arg=getopt.getopt(sys.argv[1:],"o:i:c:t:")
is_select=0
is_homology=0
out_ident=float(0)
out_coverage=float(0)
orftype=False
for i,a in opts:
    if i in ("-i"):
        out_ident=float(a)
    if i in ("-c"):
        out_coverage=float(a)
    if i in ("-o"):
        output_prefix=a
    if i in ("-t"):
        orftype=a
if orftype=="False":
    orftype=False
else:
    orftype_list=orftype.split(",")
#
fout=open(output_prefix+'.retained.fasta','w')
otherfout=open(output_prefix+'.discarded.fasta','w')
#________________________________________archieve mysql connection information and create connection______________________________#
host=config.host
user=config.username
pw=config.password
db=config.db
connection=db_construct.create_conn_db(host,user,pw,db)
#----------------------------------------------------------------------------------------------------------------------------------
if True:
    cursor=connection.cursor()
    sql_usearch="select transcript_id,indent,coverage from usearch;"
    cursor.execute(sql_usearch)
    homo_list=[]
    for trans_id,indent,coverage in cursor.fetchall():
        if trans_id:
            pass
        else:
            print "***Error, there is no eligible sequence to export.***"
            sys.exit(1)
        if float(indent)>=out_ident*100 and float(coverage)>=out_coverage*100:
            if orftype:
                type_sql="select primer_style from orf_find where transcript_id=%d;"%(trans_id)
                cursor.execute(type_sql)
                if cursor.fetchone()[0] in orftype_list:
                    homo_list.append(trans_id)
            else:
                homo_list.append(trans_id)
    trans_id_set=set(homo_list)
    sql_main="select transcript_id,transcript_name,transcript_seq from main_table;"
    cursor.execute(sql_main)
    for transcript_id,transcript_name,transcript_seq in cursor.fetchall():
        if transcript_id in trans_id_set:
            fout.write(">"+transcript_name+'\n')
            fout.write(transcript_seq+'\n')
        else:
            otherfout.write(">"+transcript_name+'\n')
            otherfout.write(transcript_seq+'\n')
