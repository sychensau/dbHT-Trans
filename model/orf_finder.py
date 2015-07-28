import os,re
import sys,getopt
from sys import path
path.append(sys.path[0])
path.append(os.path.dirname(sys.path[0]))
import config
import db_construct
import db_operation
import commands
import random
import genetic_code_library
opts,arg=getopt.getopt(sys.argv[1:],"l:g:")
end="TAA,TAG,TGA"
start="ATG"
for i,a in opts:
    if i in ("-l"):
        min_orf_len=int(a)
    if i in ("-g"):
        genetic=a
if genetic:
    code_dict=genetic_code_library.code_dict
    genetic_code=code_dict[genetic]
    start=genetic_code['start']
    end=genetic_code['end']
###################################################################################################################################
#________________________________________archieve mysql connection information and create connection______________________________#
host=config.host
user=config.username
pw=config.password
db=config.db
connection=db_construct.create_conn_db(host,user,pw,db)
#
script_loc=os.path.split(os.path.realpath(sys.argv[0]))[0]#script location
tmpdir=script_loc+"/tmp."+str(random.randint(1000,9999))
os.mkdir(tmpdir)
bed_tmpfile=tmpdir+"/orf.bed"
transcript_tmpfile=tmpdir+"/transcript.fa"
transcript_tmp_path=db_operation.allsequence2fasta(connection,"main_table",["transcript_id","transcript_seq"],transcript_tmpfile)
if os.path.isfile(transcript_tmp_path):
    pass
else:
    print "Error, could not create fasta file!"
    sys.exit(1)
#execute orf finder
command_line="python "+script_loc+"/ORFs_finder_NGS.py -i %s -b %s -l %d -e %s -s %s" % (transcript_tmp_path,bed_tmpfile,min_orf_len,end,start)
print commands.getoutput(command_line)
#insert into mysql
if os.path.isfile(transcript_tmp_path):
    pass
else:
    print "Error, bed file not found"
    sys.exit(1)
insert_value_list=[]
select_list=[]
for line in open(bed_tmpfile,'r'): #extract cds regions.
    line_list=line.strip().split()
#transcript id
    name_list=line_list[0].split('_')
    transcript_id=name_list[0].strip()
#region
    cds_start=line_list[4]
    cds_end=line_list[5]
#longest
    longest_start=line_list[6]
    longest_end=line_list[7]
    strand=line_list[8]
#select transcript_id for update main table
    select_list.append(transcript_id)
#orf type
    type_id=int(line_list[9])
    if type_id==8:
        primer="'complete'"
    elif type_id==5:
        primer="'3primer_partial'"
    elif type_id==3:
        primer="'5primer_partial'"
    elif type_id==0:
        primer="'internal'"
    else:
        print "error,",line
        sys.exit(1)
#
    strand_value=r"'%s'" %(strand)
    insert_value='('+','.join([transcript_id,cds_start,cds_end,longest_start,longest_end,primer,strand_value])+')'
    insert_value_list.append(insert_value)
    if len(insert_value_list)>=300:
        insert_value_multi=",".join(insert_value_list)
        insert_field_list=['transcript_id','cds_start','cds_end','longest_cds_start','longest_cds_end','primer_style','strand']
        db_operation.bed_2_mysql(connection,"orf_find",insert_field_list,insert_value_multi)
        insert_value_list=[]
if len(insert_value_list)>0:
    insert_value_multi=",".join(insert_value_list)
    insert_field_list=['transcript_id','cds_start','cds_end','longest_cds_start','longest_cds_end','primer_style','strand']
    db_operation.bed_2_mysql(connection,"orf_find",insert_field_list,insert_value_multi)
#updata main_table
cursor=connection.cursor()
for trans_id in set(select_list):
    sql_update_main_table='update main_table SET cds_select=1 WHERE transcript_id=%d' %(int(trans_id))
    cursor.execute(sql_update_main_table)
connection.commit()
