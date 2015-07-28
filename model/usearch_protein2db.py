#encoding:utf-8
#!/usr/bin/python
import os,sys
from sys import path
path.append(sys.path[0])
path.append(os.path.dirname(sys.path[0]))
import db_construct
import config
import db_operation
import MySQLdb
import getopt
import commands
import random
import glob
import linecache
import multiprocessing
def read_genome(genome_file):
    genome_file_opened=open(genome_file,"r")
    genome_dict={}
    first=True
    for line_seq in genome_file_opened:
        if line_seq.startswith(">"):
            if first:
                chr_name=line_seq
                seq=""
                first=False
            else:
                genome_dict[chr_name]=seq
                chr_name=line_seq
                seq=""
        else:
            seq=seq+line_seq.strip()
    genome_dict[chr_name]=seq
    return genome_dict
def file_split(file_dict,write_file):
    opened_write=open(write_file,'w')
    if len(file_dict)>0:
        for name in file_dict.keys():
	    protein_seq=file_dict.get(name,None)
	    del file_dict[name]
	    opened_write.write(name)
	    opened_write.write(protein_seq)
	    opened_write.write('\n')
            if os.path.getsize(write_file)>4000:
	        opened_write.close()
	        break
    return write_file
def database_replace(database,replaced_database):
    fdatabase=open(database,'r')
    fout=open(replace_database,'w')
    for line in fdatabase:
        if line.startswith(">"):
            line=line.replace(" ","~")
        fout.write(line)
    return replace_database
def multi_usearch(usearch_path,subfile,db_file,indentify,query_cov,output_file_path):
    usearch_command=usearch_path+' -usearch_local %s -db %s -lopen 10.0 -lext 2.0 -id %f -query_cov %f -mincols 35 -maxaccepts 8 -maxrejects 256 -userout %s -userfields query+target+id+qcov+tcov+evalue' %(subfile,db_file,indentify,query_cov,output_file_path)
    commands.getoutput(usearch_command)
if '__main__'==__name__:
    #------------------------------------------------------------------------------------------------------#
    #----------------------------archieve mysql connection infomation--------------------------------------#
    script_loc=os.path.split(os.path.realpath(sys.argv[0]))[0]
    host=config.host
    user=config.username
    pw=config.password
    db=config.db
    connection=db_construct.create_conn_db(host,user,pw,db)
    usearch_path=script_loc+'/usearch7.0.1090_i86linux32'
    #------------------------------------------------------------------------------------------------------#
    useage='''
    useage:python usearch_protein2db.py -i <input protein file> -o <align result> -i <indentify> -c <query coverage> [-t retain_result_number]
'''
    opts,arg=getopt.getopt(sys.argv[1:],"i:d:c:p:")
    for i,a in opts:
        if i in ('-i'):
            indentify=float(a)
        if i in ('-c'):
            query_cov=float(a)
        if i in ('-d'):
            db_file=a
        if i in ('-p'):
            proc=int(a)
    random_name=str(random.randint(10000,99999))
    outdir=script_loc+"/tmp."+random_name
    os.mkdir(outdir)
    replace_database=outdir+"/database_replace.fa"
    db_file_replace=database_replace(db_file,replace_database)
    db_file=db_file_replace
    #extract cds sequence and translate into protein
    input_cds=db_operation.archieve_cds_seq2fasta(connection,outdir+"/outputfile_CDS.fa")
    inputprotein=outdir+"/outputfile_protein.fa"
    command_translate="python %s/standard_code.py -i %s -o %s -t" %(script_loc,input_cds,inputprotein)
    commands.getoutput(command_translate)
    quiry_dict=read_genome(inputprotein)
    name_tail=0
    if len(quiry_dict)>0:
	splitfile_dir=outdir+'/split_dir/'
        splitfile_result_dir=outdir+'/result_dir/'
      #  os.mkdir(outdir)
        os.mkdir(splitfile_dir)
        os.mkdir(splitfile_result_dir)
    while len(quiry_dict)>0:
	name_tail=name_tail+1
	split_file_path=splitfile_dir+"subquery_"+str(name_tail)+'.txt'
	query_file=file_split(quiry_dict,split_file_path)
#---------------------------------------------------------------------------------------------------#
#----------------------------------------execute usearch--------------------------------------------#
    if os.path.splitext(db_file)[1]=='.udb':
        pass
    else:
        udb_out=os.path.splitext(db_file)[0]+'.udb'
        command_udb=usearch_path+' -makeudb_usearch %s -output %s' % (db_file,udb_out)
        commands.getoutput(command_udb)
        db_file=udb_out
    insert_field=['annotation_id','transcript_id','protein_name','indent','coverage',"taget_coverage"]
    cursor=connection.cursor()
    pool=multiprocessing.Pool(processes=proc)
    usearch_result_file_path_list=[]
    input_list=glob.glob(os.path.dirname(split_file_path)+'/*.txt')
    sub_file_number=len(input_list)
    for subfile in input_list:
        subfilename=os.path.basename(subfile)
        output_file_path=splitfile_result_dir+'result_'+subfilename
        result=pool.apply_async(multi_usearch,(usearch_path,subfile,db_file,indentify,query_cov,output_file_path,))
        usearch_result_file_path_list.append(output_file_path)
    pool.close()
    pool.join()
    if len(usearch_result_file_path_list)==0:
        print "Error, homology search failure."
        os.exit(1)
    for output_file_path in usearch_result_file_path_list:
        value_list=[]
        result_list_line=linecache.getlines(output_file_path)
        if len(result_list_line)==0:
            continue
        for line in result_list_line:
            line=line.replace(r"'",r"\'")
            line=line.replace(r'"',r'\"')
            line_list=line.split()
            #
            query_info_list=line_list[0].split('_')
            annotation_id=query_info_list[0]
            transcript_id=query_info_list[1].split('.')[0]
            sql_main_aahomo="update main_table SET aa_homology=1 WHERE transcript_id=%d" %(int(transcript_id))
            cursor.execute(sql_main_aahomo)
            #
            db_info=line_list[1].replace("~"," ")
            #
            indent=line_list[2]
            query_coverage=line_list[3]
            taget_coverage=line_list[4]
            insert_value_list=[annotation_id,transcript_id,"'"+db_info+"'",indent,query_coverage,taget_coverage]
            insert_value="("+','.join(insert_value_list)+")"
            value_list.append(insert_value)
        sql_value=','.join(value_list)
        db_operation.bed_2_mysql(connection,'usearch',insert_field,sql_value)
