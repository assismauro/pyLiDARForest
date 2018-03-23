# -*- coding: utf-8 -*-
import argparse
import os
import random
import sys

import cv2
from matplotlib import pyplot as plt

# D:\CCST\Software\img2lidar\img\ebablog.png -x 807000 -y 9710000 -zf (z>0) -xr 0.5 -yr 0.5 -zr 0.20 -mz 100 -bz 100 -bxy 1 -d 5
parser = argparse.ArgumentParser(description="Convert image to LiDAR (xyz) file.")
parser.add_argument("inputfname", type=str, 
    help = "Image to process.")
parser.add_argument("-x", "--leftmostx", type=float, required = True,
    help = "leftmost X UTM coordinate")
parser.add_argument("-y", "--topmosty", type=float, required = True,
    help = "topmost Y UTM coordinate")
parser.add_argument("-xr", type=float, default = 1.0,
    help = "X ratio")
parser.add_argument("-d", "--density", type=int, default = 1,
    help = "Increase point density")
parser.add_argument("-yr", type=float, default = 1.0,
    help = "Y ratio")
parser.add_argument("-zr", type=float, default = 1.0,
    help = "Z ratio")
parser.add_argument("-bxy", "--blurrxy", type=float, default = 0.0,
    help = "Blurr in z")
parser.add_argument("-bz", "--blurrz", type=float, default = 0.0,
    help = "Blurr in z")
parser.add_argument("-mz", "--minz", type=float, default = 0.0,
    help = "Minimum Z")
parser.add_argument("-zf", "--zfilter", type=str, default = None,
    help = "Expression to supress points based in Z dmension")

parser.add_argument("-v","--verbose",type = int, help = "Show intermediate messages.")
args = parser.parse_args()

if not os.path.exists(args.inputfname):
    print("ERROR: Input file doesn't exists: {0}.\r\n".format(args.inputfname))
    parser.print_help()
    sys.exit(1)

image = cv2.imread(args.inputfname)
if args.verbose:
    cv2.imshow("Original", image)
image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

if args.verbose:
    cv2.imshow("BW", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    hist = cv2.calcHist([image],[0],None,[16],[0,256])
    counts, bins, bars = plt.hist(hist,bins=16)
    plt.title("Histogram")
    plt.show()
    cv2.waitKey(0)
    cv2.destroyAllWindows()

imgH = image.shape[0] - 1
imgW = image.shape[1] - 1

#xratio=400.0/imgH
#yratio=200.0/imgW

f=open(os.path.splitext(args.inputfname)[0]+".xyz","w")

xi=args.leftmostx
yi=args.topmosty

xratio=args.xr
yratio=args.yr
zratio=args.zr
blurrxy=args.blurrxy
blurrz=args.blurrz
minz=args.minz
zfilter=args.zfilter
random.seed()
added=0
for k in range(args.density):
    for i in range(imgH):          
       for j in range(imgW):
           z=image[i,j] 
           if zfilter != None and eval(zfilter):
               continue
           x=xi+j*xratio+random.random()*blurrxy
           y=yi-i*yratio+random.random()*blurrxy
           z=z*zratio+random.random()*blurrz + minz
           f.write("{0} {1} {2}\n".format(x,y,z))
           added+=1
           if (added % 10000) == 0:
               print(added)


f.close()