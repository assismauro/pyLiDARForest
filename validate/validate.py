# -*- coding: utf-8 -*-
import collections
import fnmatch
import glob
import os
import subprocess
import sys
import traceback

import laspy
import numpy as np
import shapefile
from valParameters import valParameters

import lidarutils


class Validate(object):
    version = ''
    minimumpointsdensity = 4.0
    cellsize = -1
    maxpercentcellsbelowdensity = -0.1
    displayheader = False
    verbose = 0  
    validatefilespath = None 
    deletefiles = None
    validateok = []
    csvresults = None
    pointsdensity = -1,
    percentcellsbelowdensity = -1,
    activevalidations = []
        
    def __init__(self,inputfname, parameters):
        self.inputfname = inputfname
        self.inFile = laspy.file.File(self.inputfname, mode = 'r')
        self.areatransect=None
        self._errorMessages = '' 
        self.parameters = parameters
        if self.validatefilespath != None:
            if self.validatefilespath.find(':') == -1: # if wasn?t specified, it?s assumied to be relative to LAS file path
                self.validatefilespath = os.path.dirname(inputfname)+'\\'+self.validatefilespath
            if not os.path.isdir(self.validatefilespath):
                os.mkdir(self.validatefilespath)
            else:
                if self.deletefiles != None:
                    self.DeleteFiles(self.validatefilespath, self.deletefiles)

    def GetLASInfoStr(self, fname, header):
        s='{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16},{17},{18},{19},{20},'.format(
            os.path.basename(fname),
            header.file_source_id,
            header.global_encoding,
            '' if fname.upper().endswith('LAZ') else header.project_id,
            header.version,
            header.date,
            header.system_id.strip('\x00'),
            header.software_id.strip('\x00'),
            header.point_records_count,
            header.scale[0],header.scale[1],header.scale[2],
            header.offset[0],header.offset[1],header.offset[2],
            header.min[0],header.min[1],header.min[2],
            header.max[0],header.max[1],header.max[2])
        for i in range(len(header.point_return_count)):
            s+=str(header.point_return_count[i])+','
        s+=str(self.areatransect)

        return s

    def Close(self):
        if self.csvresults != None:
            try:
                with open(self.csvresults,'a') as csv:
                    line = '{0},{1},{2},{3},'.format(self.GetLASInfoStr(self.inputfname, self.inFile.header),
                                                     self.pointsdensity, self.percentcellsbelowdensity, \
                                                     np.sum(self.inFile.waveform_packet_size) / 2 if hasattr(
                                                         self.inFile, 'waveform_packet_size') else '')

                    for i in range(0,len(self.validateok)):
                        line+=str(self.validateok[i])+','
                    csv.write('{0},{1}\n'.format(line[:-1],self._errorMessages.replace('\r',' ').replace('\n',' ').replace(",","")))                    
                    csv.close()
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise
    
    @property
    def errorMessages(self):
        return '' if len(self._errorMessages) == 0 else self._errorMessages[:-1]

    def TestOk(self):
        self.validateok+=[1]
        if Validate.verbose > 0:
            print('Test passed.')
            print
        
    def TestFail(self, errormessage):
        self._errorMessages+=errormessage+','
        self.validateok+=[0]
        if Validate.verbose > 0:
            print('Test failed: {0}'.format(errormessage))
            print

    @staticmethod
    def CreateCsv(return_point_count,csvresults,activevalidations):
        csv=open(csvresults,'w')
        line = 'LAS_file,file_source_id,global_encoding,project_id,version,date,system_id,software_id,point_records_count,' + \
               'scale_X,scale_Y,scale_Z,offset_X,offset_Y,offset_Z,min_X,min_Y,min_Z,max_X,max_Y,max_Z,'
        for i in range(return_point_count):
            line+='point_return_count_{0},'.format(i+1)
        line += 'areatransect,points_density,cells_below_min_density,number_of_fwf_recs,' + ','.join(
            [str(i) for i in activevalidations])
        csv.write('{0},error_messages\n'.format(line))
        csv.close()

    @staticmethod
    def FindFiles(directory, pattern):
        flist=[]
        for root, dirs, files in os.walk(directory):
            for filename in fnmatch.filter(files, pattern):
                flist.append(os.path.join(root, filename))
        return flist

    def RunCommand(self,command):
        p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
        return p.communicate()

    def Area(self,points):
        n = len(points) - 1 # of corners
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += points[i][0] * points[j][1]
            area -= points[j][0] * points[i][1]
        return abs(area) / 2.0

    def DeleteFiles(self,path,delfiles):
        delfilesarray = delfiles.split(',')
        for pattern in delfilesarray:
            try:
                map(os.remove, glob.glob(path+'\\'+pattern))
            except OSError:
                pass
    
    def CheckLiDARFileSignature(self):
        if Validate.verbose > 0:        
            print('LiDAR file signature')
        if self.inFile.header.file_signature != 'LASF':
            self.TestFail('Not a valid las file')
            return 1
        self.TestOk()
        return 0
        
    def CheckFileVersion(self):
        if(Validate.version == None and Validate.verbose):
            print('LiDAR file version not specified.')
            return 0
        if Validate.verbose > 0:       
            print('LiDAR file version ({0} expected)'.format(Validate.version))
        if self.inFile.header.version != Validate.version:
            self.TestFail('File version is {0} and should be {1}.\r\n'.format(self.inFile.header.version,Validate.version))
            return 1
        self.TestOk()
        return 0

    def CheckNumberofReturns(self):        
        if Validate.verbose > 0:        
            print('Check number of points informed in header and existing')
        if self.inFile.header.point_records_count != len(self.inFile.x):
            self.TestFail('There are {0} points indicated by reader and exists {1} points'.format(self.inFile.header.point_records_count,len(inFile.x)))
            return 1
        self.TestOk()
        return 0

    def CheckReturnNumbers(self):
        if Validate.verbose > 0: 
            print
            print('Check return numbers')
        errorMessage=''
        cr=collections.Counter(self.inFile.return_num)
        if len(cr) != len(self.inFile.header.point_return_count):
            errorMessage='There are more return number values ({0}) than described in header ({1}).\r\n'.format(len(cr),len(self.inFile.header.point_return_count))
        for i in range(len(self.inFile.header.point_return_count)):
            if (cr[i+1] != self.inFile.header.point_return_count[i]):
                errorMessage+="Number of returns ({0}) specified in header ({1}) is different of the existing in the point cloud ({2})\r\n".format(i+1,self.inFile.header.point_return_count[i],cr[i+1])
        if(errorMessage != ''):
            self.TestFail(errorMessage)
            return 1
        else:
            self.TestOk()
            return 0

    def CheckGlobalPointsDensity(self):
        if Validate.verbose > 0: 
            print
            print('Check global point density')
        self.pointsdensity = self.inFile.header.point_records_count / self.areatransect

        if Validate.verbose > 0:
            print('Cloud points density: {0}, Minimum expected points density: {1}'.format(self.pointsdensity,
                                                                                           Validate.minimumpointsdensity))
        if (self.pointsdensity < float(Validate.minimumpointsdensity)):
            self.TestFail(
                'Points density below minimum: is {0} and should be at least {1}\r\n'.format(self.pointsdensity,
                                                                                             Validate.minimumpointsdensity))
            return 1
        else:
            self.TestOk()
            return 0
                
    def CreateShpFileLAS(self):
        if Validate.verbose > 0:        
            print('Creating boundary shape file')
        shpfname=self.validatefilespath+'\\'+os.path.basename(self.inputfname)[:-4]+'.shp'
        return self.RunCommand('{0}lasboundary -i {1} -o {2} -oshp'.format(self.parameters.lastoolspath,self.inputfname,shpfname))
 
    def CalcShapeFileArea(self):
        if Validate.verbose > 0:        
            print('Calculating shape file area')
        shpfname=self.validatefilespath+'\\'+os.path.basename(self.inputfname)[:-4]+'.shp'
        sf=shapefile.Reader(shpfname)
        shapes=sf.shapes()
        if len(shapes) != 1:
            raise ValueError('{0} should have one and only one polygon.')
        else:
            self.areatransect=self.Area(shapes[0].points)
            if Validate.verbose > 0:
                print('Area LAS file: {0} ha'.format(self.areatransect/10000))

#    def Create image file

    def RunCatalog(self):
        if Validate.verbose > 0:        
            print('Running Fusion catalog command')
        catalogfname=self.validatefilespath+'\\'+os.path.basename(self.inputfname)[:-4]
    
        command='{0}catalog /image /density:{5},{1},{2} {3} {4}'.format(self.parameters.fusionpath,\
        Validate.minimumpointsdensity,int(Validate.minimumpointsdensity) * 2,self.inputfname,catalogfname,self.cellsize)        
        try:
            return self.RunCommand(command)     
        except:
            print('Catalog command error.')
            return False
        return True         
#       catalog /rawcounts /coverage /intensity:1,0,255 /firstdensity:1,4,20 /density:1,4,20

    def CheckMinMaxValues(self):
        if Validate.verbose > 0:                
            print('Check min and max X,Y,Z values in header against ''real'' values in file')
#        print('Header bounding box:')
#        bb = zip(['X', 'Y', 'Z'], self.inFile.header.min, self.inFile.header.max)
#        for i in bb:
#            print('...' + str(i))
        errorMsg=''
        x_invalid = np.logical_or((self.inFile.x - self.inFile.header.min[0]) < -0.01,\
            (self.inFile.x - self.inFile.header.max[0]) > 0.01)
        bad_x = np.where(x_invalid)
        if len(bad_x) == 0:
            errorMsg+='There are x coordinates that are not between header.min[0] and header.max[0]\r\n'
        y_invalid = np.logical_or((self.inFile.y - self.inFile.header.min[1]) < -0.01,\
            (self.inFile.y - self.inFile.header.max[1]) > 0.01)
        bad_y = np.where(y_invalid)
        if len(bad_y) == 0:
            errorMsg+='There are y coordinates that are not between header.min[1] and header.max[1]\r\n'
        z_invalid = np.logical_or((self.inFile.z - self.inFile.header.min[2]) < -0.01,\
            (self.inFile.x - self.inFile.header.max[2]) > 0.01)
        bad_z = np.where(z_invalid)
        if len(bad_z) == 0:
            errorMsg+='There are z coordinates that are not between header.min[2] and header.max[2]\r\n'
        if len(errorMsg) != 0:
            self.TestFail(errorMsg)
            return 1
        self.TestOk()
        return 0

    def CheckXtYtZt(self):
        if(float(self.inFile.header.version) >= 1.3):
            if not hasattr(self.inFile, 'x_t'):
                self.validateok += [-1]
                return 0
            errorMsg=''
            if Validate.verbose > 0:                
                print('Check if X(t),Y(t),Z(t) contains only valid values')
            valueisbad=np.logical_or(np.isnan(self.inFile.x_t),np.isinf(self.inFile.x_t))
            bad_values = np.where(valueisbad)
            count=len(bad_values[0])
            if count > 0:
                errorMsg=' {0} not valid values in X(t),'.format(count)
            valueisbad=np.logical_or(np.isnan(self.inFile.y_t),np.isinf(self.inFile.y_t))
            bad_values = np.where(valueisbad)
            count=len(bad_values[0])
            if count > 0:
                errorMsg+=' {0} not valid values in Y(t),'.format(count)
            valueisbad=np.logical_or(np.isnan(self.inFile.z_t),np.isinf(self.inFile.z_t))
            bad_values = np.where(valueisbad)
            count=len(bad_values[0])
            if count > 0:
                errorMsg+=' {0} not valid values in Z(t)'.format(count)

            if len(errorMsg) != 0:
                errorMsg='There are ' + (errorMsg[:-1] if errorMsg[:1] == ',' else errorMsg)
                self.TestFail(errorMsg)
                return 1
            self.TestOk()
        else:
            self.validateok+=[-1]
        return 0


    def CheckMaxCellsBelowDensity(self):
        if Validate.verbose > 0:                
            print('Check points density per area unit, showing the percent of area units below the limit')    
        try:
            fName=self.validatefilespath+'\\'+os.path.basename(self.inputfname)[:-4]+'.html'
            fstr=open(fName,'r').read().replace('\r','').replace('\n','')
            fstr=fstr[fstr.index('Density less than minimum specification'):]
            fstr=fstr[fstr.index('%\">'):]
            self.percentcellsbelowdensity = float(fstr[3:fstr.index('<')])
        except:
            self.validateok+=[-1]
            if self.verbose > 0:
                print('Impossible to check density value in {0} '.format(fName))
            return 0
        if Validate.verbose > 0:
            print('Cells with percent below minimum are {0}%'.format(self.percentcellsbelowdensity))
        if self.percentcellsbelowdensity > self.maxpercentcellsbelowdensity:
            self.TestFail('Cells with density below minimum: is {0} and should be lower than {1}\r\n'.format(
                self.percentcellsbelowdensity, Validate.maxpercentcellsbelowdensity))
            return 1
        else:
            self.TestOk()
            return 0

def main():

    inputfname = r'H:\NP_T-054_FWF.las'

    Validate.version = '1.2'
    Validate.minimumpointsdensity = 4
    Validate.displayheader = False
    Validate.cellsize = 1
    Validate.maxpercentcellsbelowdensity = 20
    Validate.validatefilespath = r'c:\temp'
    Validate.deletefiles = True
    Validate.csvresults = 'results_test.csv'
    Validate.activevalidations = (1, 2, 3, 4, 5, 6, 7, 8)
    Validate.verbose = 1

    if (Validate.csvresults != None):
        Validate.CreateCsv(5,Validate.csvresults,Validate.activevalidations)

    if(Validate.displayheader):
        lidarutils.displayInfo(inputfname)
    
    failCount = 0
    parameters = valParameters()
    try:
        validate=Validate(inputfname,parameters)
    except:
        if 'validate' in locals():
            validate.TestFail('Exception: {0}'.format(traceback.format_exc()))
        else:
            print("Error {0} opening file {1}".format(traceback.format_exc(),inputfname))
            os._exit(0)

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
    if Validate.verbose > 0:
        if failCount == 0:
            print('All validations passed successfully.')
        else:
            print('{0} validation(s) failed.'.format(failCount))
            print(validate.errorMessages)
    print('File: {0},'.format(inputfname)),
    validate.Close()

# In[ ]:

if __name__ == "__main__":
    main()
