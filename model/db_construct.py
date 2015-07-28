#encoding:utf-8
#!/usr/bin/python
import sys,os
from sys import path
path.append(sys.path[0])
path.append(os.path.dirname(sys.path[0]))
import db_table_design
import config
import MySQLdb

def create_conn(host,username,password):
    conn=MySQLdb.connect(host,username,password)
    return conn
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
        sql_clean="delete from %s where %s==%d;" % (table)
    elif type(value)==float:
        sql_clean="delete from %s where %s==%f;" % (table)
    elif type(value)==str:
        sql_clean="delete from %s where %s=='%s';" % (table)
    try:
        cursor=connection.cursor
        cursor.excute(sql_clean)
        return True
    except:
        connection.rollback()
        return False
def create_conn_db(host,username,password,db):
    conn=MySQLdb.connect(host,username,password,db)
    return conn
def create_db(connection,db):
    sql_cdb="Create database %s;" % (db)
    sql_delete_database="drop database %s;" %(db)
    cursor=connection.cursor()
    sql_detect_db="show databases like '%s';" % (db)
    cursor.execute(sql_detect_db)
    database_search_value=cursor.fetchone()
    if not database_search_value:
        try:
            cursor.execute(sql_cdb)
            connection.commit()
            return 1
        except:
            conn.rollback()
            print "%s is not exist, however script could not create database, please check configure!" %(db)
            return 0
    else:
        is_db=1
        while is_db==1:
            print "warning \"%s\" had existed, do you want to delete it?(Y/N)" % (db)
            value=sys.stdin.readline()
            if value.strip().upper()=='N':
                is_db=0
                return 2
            elif value.strip().upper()=='Y':
                try:
                    cursor.execute(sql_delete_database)
                    cursor.execute(sql_cdb)
                    connection.commit()
                    return 1
                except:
                    conn.rollback()
                    print "Could not create database, please check configure!"
                    return 0
                is_db=0
            else:
                is_db=1
    connection.close()
def create_table(connection,db,table_name):
    sql_select_db="use %s;" % (db) #selecting a database in which created talbes.
    sql_create_table="create table %s;" % (table_name) #sql command for creating table.
    cursor=connection.cursor()
    try:
        cursor.execute(sql_select_db)
        cursor.execute(sql_create_table)
    except:
        connection.rollback()
        print "%s,creating table failure" %(table_name)

if __name__=="__main__":
    #____________Archieve configure value start_____________
    host=config.host
    user=config.username
    pw=config.password
    db=config.db
    #____________Archieve configure value end_______________
    #____________table creation method start_____________
    main_table=db_table_design.main_table_design
    orf_find=db_table_design.orf_find_table_design
    usearch=db_table_design.usearch_alignment_table_design
    #____________table creation method end_____________
    conn=create_conn(host,user,pw)#create connection
    db_value=create_db(conn,db) #create database
    if db_value==2:
        pass
    elif db_value==1:
        create_table(conn,db,main_table)
        create_table(conn,db,orf_find)
        create_table(conn,db,usearch)
        conn.close()
        print 'database have been completed.'
    else:
        print '%s is not found!' % (db)
