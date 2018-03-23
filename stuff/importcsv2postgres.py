# -*- coding: utf-8 -*-
import argparse
import csv
import os
import sys

import dbutils


def Header():
    print('Import csv PostGre v0.8')
    print

def ParseCmdLine():
    # python importcsv2postgres.py g:\transects\laz\metrics\NP_T-0002_dn_g_n_ch1_5.csv -s localhost -u postgres -p ebaeba18 -c -t tempimport -d eba -sf 3 -cn -nv -
    parser = argparse.ArgumentParser(description='Import CSV to Postgre.')
    parser.add_argument('inputfname',help='Csv file to be imported.')
    parser.add_argument('-s','--server',help='server host IP', default = 'localhost')
    parser.add_argument('-u','--user',help='Database user name', default = 'postgre')
    parser.add_argument('-p','--pwd',help='Password')
    parser.add_argument('-d','--database',help='Database name')
    parser.add_argument('-sc','--schema',help='Database schema', default = 'public')
    parser.add_argument('-t','--tablename',help='Destination table.')
    parser.add_argument('-c','--createtable',help=r'Recreate table if it exists.', default = False, action = 'store_true')
    parser.add_argument('-sf','--skipfields',type=int,help='Fields to skip when checking null values.',default=0)
    parser.add_argument('-cn', '--createfilenamefield', help='Create a field to store filename.', default = False, action = 'store_true')
    parser.add_argument('-nv', '--nullvalue', help='Null value to be checked', default='')
    parser.add_argument('-del', '--delimiter', help='CSF file value delimiter', default=',')
    parser.add_argument('-ncols', '--numberofcolumns', help='Number of columns to be considered', type=int, default=-1)
    parser.add_argument('-v','--verbose', type=int, help = 'Show intermediate messages.',default=0)

    try:
        return parser.parse_args()
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

if __name__ == '__main__':
    Header()
    args=ParseCmdLine()
    db=dbutils.dbutils(args.server,args.user,args.pwd,args.database,args.schema)
    data=[]
    with open(args.inputfname,'r') as f:
        reader=csv.DictReader(f,delimiter=args.delimiter)
        for line in reader:
            data.append(line)
    ncols = args.numberofcolumns if args.numberofcolumns > -1 else len(reader.fieldnames)
    fnames = reader.fieldnames
    db.initsqlvalidfieldnames(fnames)
    if(args.createtable):
        db.createtable(args.tablename, fnames, data, args.skipfields, args.nullvalue, args.createfilenamefield)
    added = db.addrecs(args.tablename, fnames, data, args.skipfields, args.nullvalue)
    if (args.createfilenamefield):
        db.execute("UPDATE {0} SET filename = '{1}' WHERE filename IS NULL".format(args.tablename, os.path.basename(
            args.inputfname).upper()), True)
    print('File {0} imported, {1} lines processed, {2} recs added'.format(args.inputfname, len(data), added))