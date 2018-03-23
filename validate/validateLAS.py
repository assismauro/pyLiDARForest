# -*- coding: utf-8 -*-
import argparse
import os
import sys
import time
import traceback
from argparse import RawTextHelpFormatter
from multiprocessing import Pool, Process

from valParameters import valParameters

from validate import Validate


def Header():
    print('LiDAR file checker v0.8')
    print

def ParseCmdLine():
    parser = argparse.ArgumentParser(description='Validate LAS files.',formatter_class=RawTextHelpFormatter)
    parser.add_argument('inputfname',help='las file to be processed.')
    parser.add_argument('-l','--lasversion', help='LAS file version.', default = None)
    parser.add_argument('-m','--minimumpointsdensity', help='Minimum points density in cloud', required=True)
    parser.add_argument('-d','--displayheader', help='Display LAS file header information', type=int, default = False)
    parser.add_argument('-c','--processorcores', type=int, help='Processor cores to use.', default = 1)
    parser.add_argument('-z','--cellsize', type=int, help='Size (in the same LAS distance unit) of the cell to be checked.',default = -1)
    parser.add_argument('-x','--maxpercentcellsbelowdensity', type=float, help='Maximum percent of cells below points density.', default = -1.0)
    parser.add_argument('-sv','--selectedvalidations',type=str,default=None,help='''
Select validations to run (by number):
1 - File signature
2 - LAS file version
3 - Number of returns
4 - Return numbers
5 - Minimum and maximum values
6 - Global points density
7 - Percent 
8 - Xt,Yt,Zt values

Ex: -sv 5,6 
''')
    parser.add_argument('-del','--deletefiles', help='Delete auxiliar files created in a previous run.', type=str, default = None)
    parser.add_argument('-vfp','--validatefilespath', help='Path to files created by this software.', type=str, default = None)
    parser.add_argument('-csv','--csvresults', help='Create and populate a csv file containing data about files and validation results.', type=str, default = None)
    parser.add_argument('-v','--verbose', type=int, help='Level of processing messages.', default = False)
    return parser.parse_args()
        
def ProcessFile(inputfname,lasversion,minimumpointsdensity,displayheader,cellsize,maxpercentcellsbelowdensity,activevalidations,deletefiles,validatefilespath,csvresults,verbose):
    Validate.version = lasversion
    Validate.minimumpointsdensity = minimumpointsdensity
    Validate.displayheader = displayheader
    Validate.cellsize = cellsize
    Validate.maxpercentcellsbelowdensity = maxpercentcellsbelowdensity
    Validate.validatefilespath = validatefilespath
    Validate.deletefiles = deletefiles
    Validate.csvresults = csvresults
    Validate.activevalidations=activevalidations
    Validate.verbose = verbose
    
    start = time.time()
    failCount=0
    if(Validate.displayheader):
        lidarutils.displayInfo(inputfname)
    parameters = valParameters()
    try:
        validate=Validate(inputfname,parameters)
        if 1 in validate.activevalidations:
            failCount+=validate.CheckLiDARFileSignature()

        if 2 in validate.activevalidations:
            failCount+=validate.CheckFileVersion()

        if 3 in validate.activevalidations:
            failCount+=validate.CheckNumberofReturns()

        if 4 in validate.activevalidations:
            failCount+=validate.CheckReturnNumbers()

        if 5 in validate.activevalidations:
            failCount+=validate.CheckMinMaxValues()

        if (6 in validate.activevalidations) or (7 in validate.activevalidations):
            validate.CreateShpFileLAS()
            catalogOk=validate.RunCatalog()
            if catalogOk:
                validate.CalcShapeFileArea()

        if 6 in validate.activevalidations:
            failCount+=validate.CheckGlobalPointsDensity()

        if 7 in validate.activevalidations:
            if catalogOk:
                failCount+=validate.CheckMaxCellsBelowDensity()

        if 8 in validate.activevalidations:
            failCount+=validate.CheckXtYtZt()
    except:
        if 'validate' in locals():
            validate.TestFail('Exception: {0}'.format(traceback.format_exc()))
        else:
            print("Error {0} opening file {1}".format(traceback.format_exc(),inputfname))
            os._exit(0)

        failCount += 1
               
    if Validate.verbose > 0:
        if failCount == 0:
            print('All validations passed successfully.')
        else:
            print('{0} validation(s) failed.'.format(failCount))
            print(validate.errorMessages)
    print('File: {0},'.format(inputfname)),
    print('{0} (elapsed time: {1:.2f}s)'.format('ok' if failCount == 0 else 'failed: '+validate.errorMessages.strip(),time.time()-start))
    validate.Close()
       
# In[ ]:
if __name__ == '__main__':
    Header()
    args=ParseCmdLine()
    if args.selectedvalidations == None:
        selectedvalidations = '1,2,3,4,5,6,7,8'
    else:
        selectedvalidations=args.selectedvalidations
    activevalidations=map(int,selectedvalidations.split(','))
    if (args.csvresults != None):
        Validate.CreateCsv(5,args.csvresults,activevalidations)
    path, filemask = os.path.split(args.inputfname)
    files=sorted(Validate.FindFiles(path,filemask))
    if len(files) == 0:
        print('There''s no file to process.')
        sys.exit(1)
    verystart = time.time()
    print('Processing {0} files.'.format(len(files)))
    threads=args.processorcores
    jobs=[]
    i=0

    while i < (len(files) / threads * threads):
        if threads == 1:
            ProcessFile(files[i],args.lasversion,args.minimumpointsdensity,args.displayheader,args.cellsize,args.maxpercentcellsbelowdensity,
                        activevalidations,args.deletefiles,args.validatefilespath,args.csvresults,args.verbose)
            i+=1
            continue
        startpool = time.time()
        p=Pool(threads)
        for thread in range(0,threads):
            params=(files[i + thread],args.lasversion,args.minimumpointsdensity,args.displayheader,args.cellsize,args.maxpercentcellsbelowdensity,
                    activevalidations,args.deletefiles,args.validatefilespath,args.csvresults,args.verbose)
            p=Process(target=ProcessFile,args=params)
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        print('Pool elapsed time: {0:.2f}s'.format(time.time()-startpool))    
        i+=threads
    while i < len(files):
        params=(files[i],args.lasversion,args.minimumpointsdensity,args.displayheader,args.cellsize,args.maxpercentcellsbelowdensity,
                activevalidations,args.deletefiles,args.validatefilespath,args.csvresults,args.verbose)
        if threads == 1:
            ProcessFile(files[i],args.lasversion,args.minimumpointsdensity,args.displayheader,args.cellsize,args.maxpercentcellsbelowdensity,
                        activevalidations,args.deletefiles,args.validatefilespath,args.csvresults,args.verbose)    
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
