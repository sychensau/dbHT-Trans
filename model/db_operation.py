import MySQLdb
import os
def clean_all_table(connection,table):
    sql_clean="truncate %s;" % (table)
    try:
        cursor=connection.cursor()
        cursor.execute(sql_clean)
        return True
    except:
        connection.rollback()
        return False
def clean_by_condition(connection,table,field,value):
    if type(value)==int:
        sql_clean="delete from %s where %s==%d;" % (table,field,value)
    elif type(value)==float:
        sql_clean="delete from %s where %s==%f;" % (table,field,value)
    elif type(value)==str:
        sql_clean="delete from %s where %s=='%s';" % (table,field,value)
    try:
        cursor=connection.cursor()
        cursor.excute(sql_clean)
        return True
    except:
        connection.rollback()
        return False
def create_conn_db(host,username,password,db):
    conn=MySQLdb.connect(host,username,password,db)
    return conn
def sql2fasta(connection,table,target_field_list,field,value,outfile):
    taget_field=','.join(target_field_list)
    fopen=open(outfile,'w')
    if type(value)==int:
        sql_sequence="select %s from %s where %s==%d;" % (taget_field,table,field,value)
    elif type(value)==float:
        sql_sequence="select %s from %s where %s==%f;" % (taget_field,table,field,value)
    elif type(value)==str:
        sql_sequence="select %s from %s where %s=='%s';" % (taget_field,table,field,value)
    try:
        cursor=connection.cursor()
        cursor.excute(sql_clean)
        for seq_id,name,sequence in cursor.fetchall():
            fopen.write(seq_id+'_'+name+'\n')
            fopen.write(sequence+'\n')
        return True
    except:
        connection.rollback()
        return False
def allsequence2fasta(connection,table,target_field_list,outfile):
    taget_field=','.join(target_field_list)
    fopen=open(outfile,'w')
    sql_sequence="select %s from %s;" % (taget_field,table)
    try:
        cursor=connection.cursor()
        cursor.execute(sql_sequence)
        for seq_id,sequence in cursor.fetchall():
            fopen.write('>'+str(seq_id)+'\n')
            fopen.write(sequence+'\n')
        outputfile_path=os.path.abspath(outfile)
        return outputfile_path
    except:
        connection.rollback()
        return False
def bed_2_mysql(connection,table,field_list,values):
    target_field=','.join(field_list)
    sql_insert="insert into %s (%s) value %s;" %(table,target_field,values)
    cursor=connection.cursor()
    cursor.execute(sql_insert)
    connection.commit()
def archieve_cds_seq2fasta(connection,outputfile): 
    sql_transcript_seq="select transcript_id,transcript_seq from main_table;"
    cursor=connection.cursor()
    cursor_cds=connection.cursor()
    cursor.execute(sql_transcript_seq)
    transcript_sequence={}
    for seq_id,sequence in cursor.fetchall():
        transcript_sequence[int(seq_id)]=sequence 
    sql_cds_seq="select annotation_id,transcript_id,cds_start,cds_end,strand from orf_find;"
    cursor_cds.execute(sql_cds_seq)
    cds_info=cursor_cds.fetchall()
    fout=open(outputfile,'w')
    complementation={'A':'T','C':'G','T':'A','G':'C','N':'N'}
    for anno_id,trans_id,start,end,strand in cds_info:
        m_seq=transcript_sequence.get(int(trans_id),None)
        if strand=='+':
            cds_seq=m_seq[int(start):int(end)].upper()
        elif strand=='-':
            cds_seq_r=m_seq[int(start):int(end)].upper()
            cds_seq="".join(map(lambda x:complementation[x],cds_seq_r))[::-1]
        else:
            print 'error!'
        fout.write('>'+str(anno_id)+'_'+str(trans_id)+'\n')
        fout.write(cds_seq+'\n')
    fout.close()
    return outputfile       
def output_cds_seq2fasta(connection,outputfile): 
    sql_transcript_seq="select transcript_id,transcript_seq,transcript_name from main_table;"
    cursor=connection.cursor()
    cursor_cds=connection.cursor()
    cursor.execute(sql_transcript_seq)
    transcript_sequence={}
    id_name_dict={}
    for seq_id,sequence,transcript_name in cursor.fetchall():
        transcript_sequence[int(seq_id)]=sequence
        id_name_dict[int(seq_id)]=transcript_name
    sql_cds_seq="select annotation_id,transcript_id,cds_start,cds_end,strand from orf_find;"
    cursor_cds.execute(sql_cds_seq)
    cds_info=cursor_cds.fetchall()
    fout=open(outputfile,'w')
    complementation={'A':'T','C':'G','T':'A','G':'C','N':'N'}
    for anno_id,trans_id,start,end,strand in cds_info:
        m_seq=transcript_sequence.get(int(trans_id),None)
        m_name=id_name_dict[int(trans_id)]
        if strand=='+':
            cds_seq=m_seq[int(start):int(end)].upper()
        elif strand=='-':
            cds_seq_r=m_seq[int(start):int(end)].upper()
            cds_seq="".join(map(lambda x:complementation[x],cds_seq_r))[::-1]
        else:
            print 'error!'
        fout.write('>'+m_name+'.cds\n')
        fout.write(cds_seq+'\n')
    fout.close()
    return outputfile  
def cds_final(connection,outputfile,out_ident,out_cov):
    sql_transcript_seq="select transcript_id,transcript_seq,transcript_name from main_table;"
    cursor=connection.cursor()
    cursor_cds=connection.cursor()
    cursor.execute(sql_transcript_seq)
    transcript_sequence={}
    id_name_dict={}
    for seq_id,sequence,transcript_name in cursor.fetchall():
        transcript_sequence[int(seq_id)]=sequence
        id_name_dict[int(seq_id)]=transcript_name
    sql_cds_seq="select annotation_id,transcript_id,cds_start,cds_end,strand from orf_find;"
    cursor_cds.execute(sql_cds_seq)
    cds_info=cursor_cds.fetchall()
    sql_homo_id="select annotation_id,indent,coverage from usearch;"
    cursor_id=connection.cursor()
    cursor_id.execute(sql_homo_id)
    anno_list_usearch=[]
    for anno_id,indent,coverage in cursor_id.fetchall():
        if float(indent)>=float(out_ident*100) and float(coverage)>=float(out_cov*100):
            anno_list_usearch.append(int(anno_id))
    anno_set=set(anno_list_usearch)
    fout=open(outputfile,'w')
    complementation={'A':'T','C':'G','T':'A','G':'C','N':'N'}
    for anno_id,trans_id,start,end,strand in cds_info:
        if int(anno_id) in anno_set:
            pass
        else:
            continue
        m_seq=transcript_sequence.get(int(trans_id),None)
        m_name=id_name_dict[int(trans_id)]
        if strand=='+':
            cds_seq=m_seq[int(start):int(end)].upper()
        elif strand=='-':
            cds_seq_r=m_seq[int(start):int(end)].upper()
            cds_seq="".join(map(lambda x:complementation[x],cds_seq_r))[::-1]
        else:
            print 'error!'
        fout.write('>'+m_name+'.cds\n')
        fout.write(cds_seq+'\n')
    fout.close()
    return outputfile
