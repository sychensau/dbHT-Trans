import os,sys,getopt
from sys import path
path.append(sys.path[0])
path.append(os.path.dirname(sys.path[0]))
import config
import db_construct
opts,arg=getopt.getopt(sys.argv[1:],"o:c:i:t:")
output='output_meta_table.txt'
out_ident=0
out_coverage=0
for i,a in opts:
    if i in ("-o"):
        output=a
    if i in ("-c"):
        out_coverage=float(a)
    if i in ("-i"):
        out_ident=float(a)
    if i in ("-t"):
        orftype=a
if orftype=="False":
    orftype=False
else:
    orftype_list=orftype.split(",")
#---------------------------------------------------------------------------------------------------------------------------------#
#________________________________________archieve mysql connection information and create connection______________________________#
host=config.host
user=config.username
pw=config.password
db=config.db
connection=db_construct.create_conn_db(host,user,pw,db)
#---------------------------------------------------------------------------------------------------------------------------------#
result_dict={} #{trans_id:[transcript_name,gene_name,[cds1,primer,yes,yes],[cds1,primer,yes,yes]....]}

#-----------------------------------select alignment cds_id and transcript_id-----------------------------------------------------------------------#
cursor=connection.cursor()
sql_select_main="select transcript_id,transcript_name,gene_name,transcript_seq from main_table;"
cursor.execute(sql_select_main)
transcript_info={}
for transcript_id,transcript_name,gene_name,transcript_seq in cursor.fetchall():
    transcript_seq_len=len(transcript_seq)
    transcript_info[transcript_id]=[transcript_name,gene_name,transcript_seq_len]
#
usearch_info={}
sql_select_usearch="select annotation_id,transcript_id,protein_name,indent,coverage,taget_coverage from usearch;"
cursor.execute(sql_select_usearch)
retain_transcript=[]
for annotation_id,transcript_id,protein_name,indent,coverage,taget_coverage in cursor.fetchall():
    if float(indent)>=out_ident*100 and float(coverage)>=out_coverage*100:
        ali_n=usearch_info.get(annotation_id,None)
        retain_transcript.append(transcript_id)
        if ali_n:
            usearch_info[annotation_id].append((protein_name,str(indent),str(coverage),str(taget_coverage)))
        else:
            usearch_info[annotation_id]=[(protein_name,str(indent),str(coverage),str(taget_coverage))]
#
fout=open(output,'w')
sql_cds="select primer_style,annotation_id,transcript_id,cds_start,cds_end,longest_cds_start,longest_cds_end,strand from orf_find"
cursor.execute(sql_cds)
for primer_style,annotation_id,transcript_id,cds_start,cds_end,longest_cds_start,longest_cds_end,strand in cursor.fetchall():
    if orftype:
        if primer_style in orftype_list:
            pass
        else:
            continue
    else:
        pass
    transcript_name=transcript_info[transcript_id][0]
    gene_name=transcript_info[transcript_id][1]
    trans_length=transcript_info[transcript_id][2]
    align_list=usearch_info.get(annotation_id,[])
    align_number=len(align_list)
    fout.write(transcript_name+"\t"+gene_name+"\t"+str(trans_length)+"\t"+str(cds_start)+"\t"+str(cds_end)+'\t'+str(longest_cds_start)+'\t'+str(longest_cds_end)+'\t'+primer_style+"\t"+strand+"\t"+str(align_number)+"\t")
    if len(align_list)==0:
        fout.write("None"+"\n")
    else:
        for align in align_list:
            align_str=';'.join(align)
            fout.write("["+align_str+"]	")
        fout.write('\n')
for line in transcript_info:
    if line in retain_transcript:
        pass
    else:
        transcript_name=transcript_info[line][0]
        gene_name=transcript_info[line][1]
        transcript_length=transcript_info[line][2]
        fout.write(transcript_name+"	"+gene_name+"	"+str(transcript_length)+"	"+"None"+"\n")
