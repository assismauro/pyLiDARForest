# -*- coding: utf-8 -*-
import argparse
import os
import sys

import EarthTones
import cv2
import laspy
import numpy as np
import pandas as pd


class las2img(object):

    def __init__(self, inputfname, palette, verbose):
        self.inputfname = inputfname
        try:
            self.inFile = laspy.file.File(self.inputfname, mode = 'r')
            self.palette=palette
            self.verbose=verbose
        except:
            print("Impossible to open file {0}".format(self.inputfname))
            raise

    @staticmethod
    def Header():
        print("LiDAR to Image v0.8")
        print("")
        print("Processing...")

    @staticmethod
    def ProcessCmdLine():
        # G:\TRANSECTS\T_002\NP_T-002_LAS\NP_T-002.LAS G:\TRANSECTS\T_002\NP_T-002_LAS -p 1 -f 0   
        # python D:\CCST\Software\pyLiDARForest\stuff\las2img.py 000_slice_norm_filtered_biomass_np_t-410.las . -f 2 -v 1 
        parser = argparse.ArgumentParser(description="Convert LiDAR (las) to image file.")
        parser.add_argument("inputfname", type=str, 
            help = "LiDAR file to process.")
        parser.add_argument("destinationpath", type=str, help = "Destination path of output image.")
        parser.add_argument("-s","--scale", help="image scale",type=float, default=0.0018) 
        parser.add_argument("-p","--palette", help=" 0: grayscale, 1: earthtones palette, 2. opencv 3. b&w",type=int, default=1) 
        parser.add_argument("-f","--imagefformat", help=" 0: tiff, 1: jpeg, 2. png",type=int, default=0) 
        parser.add_argument("-i","--intensity", help="Use intensity to color figure. If false (default), use elevation.", action='store_true', default=False)
        parser.add_argument("-t","--intensitythreshold", help="Maximum intensity value to be considered.", type =int, default=-1)
        parser.add_argument("-v", "--verbose", type=int, help="Show intermediate messages.", default=0)
        args=parser.parse_args()

        if not os.path.exists(args.inputfname):
            raise Exception("ERROR: Input file doesn't exists: {0}.\r\n".format(args.inputfname))
        if args.intensity and (args.intensitythreshold == -1):
            raise Exception("It´s mandatory to inform a valid intensitythreshold parameter to use intensity to color images.")
        return args

    def update_progress(self,progress):
        print('\r[{0}{1}] {2}%'.format('#' * int(progress / 10 + 1), '.' * int(10 - progress / 10), int(progress)),
              end='')

    def Execute(self,scale,intensity,intensitythreshold):
        imagewidth=int(scale*(np.amax(self.inFile.X) - np.amin(self.inFile.X)))
        imageheight=int(scale*(np.amax(self.inFile.Y) - np.amin(self.inFile.Y)))
        X=self.inFile.X-np.amin(self.inFile.X)
        X=np.around(X * scale).astype(int)-1
        Y=self.inFile.Y-np.amin(self.inFile.Y)
        Y = np.around(Y * scale).astype(int)-1
        if intensity:
            Z=self.inFile.Intensity-np.amin(self.inFile.Intensity)
            ts=np.less_equal(Z,intensitythreshold)
            Z=Z[ts]
            X=X[ts]
            Y=Y[ts]
        else:
            Z=self.inFile.Z-np.amin(self.inFile.Z)
        self.inFile.close()

        self.image = np.zeros(shape=(imageheight+1,imagewidth+1,3), dtype = "uint8")
        
        if self.palette == 3:
            Z[np.greater(Z,0)]=255
        else:
            if self.palette != 1:
                Z=(255.0/np.amax(Z)*Z).astype(int)
        m=np.column_stack((Z,X))
        m=np.column_stack((m,Y))
        Y=[]
        X=[]
        Z=[]
        df=pd.DataFrame(m).sort_values(0)
        i=0
        total=len(df)
        divider=1000000 if len(X) > 10000000 else 100000 if len(X) > 1000000 else 10000 if len(X) > 100000 else 100 
        if self.palette == 1:
            earthTones=EarthTones.EarthTones(0,df.min()[0],df.max()[0])
        for row in df.itertuples():
            if self.palette == 1:
                self.image[row[3],row[2]]=earthTones.MapColor(row[1])
            else:
                self.image[row[3],row[2]]=row[1]
            if self.verbose > 0:
                if (i % divider) == 0:
                    self.update_progress(float(i)/total*100)
            i+=1
        self.update_progress(100.0)
        print('')

    def Close(self,destinationpath):
        outputfname=destinationpath + ('\\' if destinationpath[-1:] != '\\'  else '')+os.path.splitext(os.path.basename(self.inFile.filename))[0]+\
            ('.tif' if args.imagefformat == 0 else ('.jpg' if  args.imagefformat == 1  else '.png'))
        if args.verbose > 0:
            print('Saving {0}...'.format(outputfname))

        fimg=cv2.flip(self.image,0)
        if self.palette == 2:
            fimg=cv2.applyColorMap(fimg,cv2.COLORMAP_SUMMER)
        if not cv2.imwrite(outputfname,fimg):
            print("Error saving image.")
            return False
        return True
       
if __name__ == "__main__":
    try:
        args=las2img.ProcessCmdLine()
    except Exception as e:
        print("Unexpected error:", sys.exc_info()[0])
        print(e)
        sys.exit(1)
        
    l2i = las2img(args.inputfname,args.palette,args.verbose)
    if args.verbose > 0:
        las2img.Header()
    l2i.Execute(args.scale,args.intensity,args.intensitythreshold)
    l2i.Close(args.destinationpath)
    if args.verbose > 0:
        print('Done.')
