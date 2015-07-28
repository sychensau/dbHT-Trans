#encoding:utf-8
#!/usr/bin/python
import os,sys,getopt
from sys import path
path.append(sys.path[0])
path.append(os.path.dirname(sys.path[0]))
import db_construct
import config
def delete_all_table(conn,tablename):
    cursor=conn.cursor()
    sql_cancel_table='TRUNCATE %s;' %(tablename)
    cursor.execute(sql_cancel_table)
    return True
if "__main__"==__name__:
    #mysql infomation
    host=config.host
    user=config.username
    pw=config.password
    db=config.db
    conn=db_construct.create_conn_db(host,user,pw,db)
    cursor=conn.cursor()
    #extract option
    useage='''
    useage: python standard_code.py -t [sequence/orf_find/usearch]
        -t step name, which have insert data in mysql, but we want to delete now. It always include the data that make by previous steps.
    '''
    opts,arg=getopt.getopt(sys.argv[1:],"t:")
    if len(opts)==0:
        print useage
        sys.exit(1)
    for i,a in opts:
        if i in ("-t"):
            table_name=a.strip()
    if table_name=='usearch':
        delete_all_table(conn,'usearch')
    elif table_name=='orf_find':
        delete_all_table(conn,'orf_find')
        delete_all_table(conn,'usearch')
        sql_cancel_cds_select="update main_table set cds_select=0 where transcript_id;"
        cursor.execute(sql_cancel_cds_select)
        conn.commit()
    elif table_name=="sequence":
        delete_all_table(conn,'usearch')
        delete_all_table(conn,'orf_find')
        delete_all_table(conn,'main_table')
        sql_cancel_cds_select="update main_table set cds_select=0 where transcript_id;"
        cursor.execute(sql_cancel_cds_select)
        sql_cancel_cds_select="update main_table set aa_homology=0 where transcript_id;"
        cursor.execute(sql_cancel_cds_select)
        conn.commit()
    else:
        print 'delete %s error'%(table_name)
