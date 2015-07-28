#encoding:utf-8
#!/usr/bin/python
import os,sys,getopt
from sys import path
path.append(sys.path[0])
path.append(os.path.dirname(sys.path[0]))
import db_construct
import config
def insert_db(value_insert):
    value_insert=value_insert.strip(',')
    sql_insert="INSERT INTO main_table (transcript_name,gene_name,transcript_seq) VALUES %s;" %(value_insert)
    cursor=conn.cursor()
    try:
        cursor.execute(sql_insert)
        conn.commit()
    except:
        conn.rollback()
        print '***Error, could not import sequence into mysql.***'
#_______________________________________________________________
opts,arg=getopt.getopt(sys.argv[1:],"i:g:")
gene_name_list=None
for i,a in opts:
    if i in ("-i"):
        transcript_file=a
    if i in ("-g"):
        gene_name_list=a
#-----------------------------------------gene name start dictionary-------------------
genenam_dict={}
if gene_name_list:
    for line in open(gene_name_list,'r'):
        line_list=line.strip().split()
        trans_name=' '.join(line_list[0:-1])
        genenam_dict[trans_name]=line_list[-1]
else:
    fkopen=open(transcript_file,'r')
    for line in open(transcript_file,'r'):
        if line.startswith(">"):
            line=line.lstrip(">").strip()
            genenam_dict[line]=line
    fkopen.close()
#-----------------------------------------gene name dictionary end-------------------

#-----------------------------create connection with mysql database start------------------
host=config.host
user=config.username
pw=config.password
db=config.db
conn=db_construct.create_conn_db(host,user,pw,db)
cursor=conn.cursor()
value_insert=''
sql_set_packet="set global max_allowed_packet=1024*1024*16;"
cursor=conn.cursor()
cursor.execute(sql_set_packet)
#-----------------------------create connection with mysql database end------------------
k=1
#______________________________________________
fopen=open(transcript_file,'r')
first_line=True
for line in fopen:
    seq_control=False
    if line.startswith(">"):
        k=k+1
        if k%10000==0:
            print k
        if first_line:
            first_line=False
            trans_name=line.strip().lstrip('>')
            gene_name=genenam_dict.get(trans_name,'0')
            seq_list=[]
            #seq_control=True
        else: #deal with next transcript
            trans_seq=''.join(seq_list)
            value_insert=value_insert+"("+"'"+trans_name+"',"+"'"+gene_name+"',"+"'"+trans_seq+"'"+"),"
            if k%450==0 and k!= 0:
                insert_db(value_insert)
                value_insert=""
            trans_name=line.strip().lstrip('>')
            gene_name=genenam_dict.get(trans_name,'0')
            seq_list=[]
    else:
        seq_line=line.strip()
        seq_list.append(seq_line)
#last transcript insert
trans_seq=''.join(seq_list)
value_insert=value_insert+"("+"'"+trans_name+"',"+"'"+gene_name+"',"+"'"+trans_seq+"'"+"),"
#commit data
value_insert=value_insert.strip(',')
sql_insert="INSERT INTO main_table (transcript_name,gene_name,transcript_seq) VALUES %s;" %(value_insert)
cursor=conn.cursor()
try:
    cursor.execute(sql_insert)
    conn.commit()
except:
    conn.rollback()
    print '***error, to submit failure.***'
    sys.exit(1)
cursor=conn.cursor()
sql_detect='select count(*) from main_table;'
cursor.execute(sql_detect)
sequence_num=cursor.fetchone()
if int(sequence_num)==0:
    print "***there is not sequence to import into mysql.***"
    sys.exit(1)
else:
    print "sequence number: %d"%(sequence_num)
