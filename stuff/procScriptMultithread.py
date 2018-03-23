
# -*- coding: utf-8 -*-
import argparse
import fnmatch
import glob
import logging
import os
import subprocess
import sys
import time
from argparse import RawTextHelpFormatter
from multiprocessing import Pool, Process


def Header():
    print('Multithread exec v0.9')
    print

def ParseCmdLine():
    # procScriptMultithread.py E:\mauro.assis\Software\pyLiDARForest\stuff\calcParams.py  -ifn g:\transects\np_t-???.las -c 1 -o="-c 100 -ac 2 -rn 4 -csv E:\mauro.assis\Software\pyLiDARForest\stuff\calcresult2.csv" 
    # procScriptMultithread.py -c 1 -v 1 E:\mariana.andrade\cau.bat
    parser = argparse.ArgumentParser(description='Process python scripts in multiprocessing mode.',formatter_class=RawTextHelpFormatter)
    parser.add_argument('programname',help='''Script file. 
    If extension is .py, will run as a python script for each file in specified in -ifm parameter,
    else if extension is .bat, it will process all commands inside .bat file, one line per processor core,
    else it will run the command with each file specified in inputfname.''')
    parser.add_argument('-ifn','--inputfname',help='File mask to be processed. If is a file name with txt extension, it will consider as a txt file containing a file names list to be processed.', type=str, default='')
    parser.add_argument('-c','--processorcores', type=int, help='Processor cores to use.', default = 1)
    parser.add_argument('-o','--otherparams',type=str, help='complementary parameters.')
    parser.add_argument('-s', '--subdirs', type=int, help='get files in subdirectory.', default=1)
    parser.add_argument('-m','--commandonly', type=int, help='Just shows commands, without run.', default = 0)
    parser.add_argument("-v","--verbose",type=int, help = "Show intermediate messages.", default = 0)
    parser.add_argument("-l", "--log", type=str, default=None, help="Logs to a file. Default 'None'.")
    try:
        return parser.parse_args()
    except:
        print(sys.exc_info()[0])
        raise

def RunCommand(command, commandonly, verbose):
    if commandonly:
        print(command)
        return None, None
    command=command.strip()
    if command == '':
        return None, None
    if (command.strip().upper()+' ').startswith('REM '):
        return None, None
    try:
        p = subprocess.Popen(command,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT)
        out, err = p.communicate()
    except:
        logging.error(command)
        return None, None
    return out, err


def FindFiles(directory, pattern, subdirs):
    flist=[]
    if (subdirs):
        for root, dirs, files in os.walk(directory):
            for filename in fnmatch.filter(files, pattern):
                flist.append(os.path.join(root, filename))
    else:
        flist = glob.glob(r"{0}\{1}".format(directory, pattern))
    return flist

def ProcessFile(program,fname,options,verbose,batchProcess,commandonly):
    commandLine='{0}{1} {2} {3}'.format(('python ' if program.upper().endswith('.PY') > 0 else ''),program,fname,options if options != None else '')
    out,err = RunCommand(commandLine, commandonly, verbose)
    if verbose > 0:
        print(commandLine)
        logging.info(commandLine)
        if out != None:
            if (verbose == 2) and (out.upper().find("ERROR") > 0):
                print(out)

            logging.info(out)
        if err != None:
            logging.error(out)

if __name__ == '__main__':
    Header()
    args = ParseCmdLine()
    if args.log:
        logging.basicConfig(filename=args.log, level=logging.INFO)
        logging.getLogger().addHandler(logging.StreamHandler())
    else:
        logging.basicConfig(level=logging.INFO)
    start = time.time()
    failcount=0
    files=[]
    batchProcess=False
    if args.inputfname != '': 
        extension = os.path.splitext(args.inputfname)[1]
        if extension.upper() == '.TXT':
            f = open(args.inputfname)
            files = f.readlines()
        else:
            path, filemask = os.path.split(args.inputfname)
            files = FindFiles(path, filemask, args.subdirs)
        if len(files) == 0:
            print('There''s no file to process.')
            sys.exit(1)
        files = sorted(files)
#        batchProcess=False
    else:
        if args.programname.upper().endswith('.BAT'):
            f = open(args.programname)
            files = f.readlines()
            batchProcess=False
            args.programname = ''
        else:
            raise ValueError('Error in procScriptMultiThread.py parameters.')

    verystart = time.time()
    print('Processing {0} files.'.format(len(files)))
    threads=args.processorcores
    jobs=[]
    i=0

    while i < (len(files) / threads * threads):
        if threads == 1:
            ProcessFile(args.programname,files[i],args.otherparams,args.verbose,batchProcess,args.commandonly)
            i+=1
            continue
        startpool=time.time()
        p=Pool(threads)
        for thread in range(0,threads):
            params=(args.programname,files[i + thread],args.otherparams,args.verbose,batchProcess,args.commandonly)
            p=Process(target=ProcessFile,args=params)
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        print('Pool elapsed time: {0:.2f}s'.format(time.time()-startpool))    
        i+=threads
    while i < len(files):
        params=(args.programname,files[i],args.otherparams,args.verbose,batchProcess,args.commandonly)
        if threads == 1:
            ProcessFile(args.programname,files[i],args.otherparams,args.verbose,batchProcess,args.commandonly)    
            i+=1    
            continue        
        startpool = time.time()
        p=Process(target=ProcessFile,args=params)    
        jobs.append(p)
        p.start()
        i+=1
    for proc in jobs:
        proc.join()
    if threads > 1:
        print('Pool elapsed time: {0:.2f}s'.format(time.time()-startpool))    
    totalelapsedtime=time.time()-verystart
    print('Total elapsed time: {0:.2f}s, time/file: {1:.2f}'.format(totalelapsedtime,totalelapsedtime/len(files)))