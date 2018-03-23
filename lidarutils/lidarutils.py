# -*- coding: utf-8 -*-
# Code built by Gorgens E. B. and Assis M.
# Brazil, Aug 2015

# Dependencies: numpy, laspy, math

# Environment setting

# In[3]:
# 52I212_plot10.las -ts -sn 1 -sb 30 -st 40
# 52I212_plot10.las -tx 
# 52I212_plot10.las -ty

import argparse
import math
import os.path
import time
import warnings
from argparse import RawTextHelpFormatter

import numpy as np
from laspy import file


def saveCloud(fname, header, cloud):
    outFile = file.File(fname, mode="w", header=header)
    outFile.points = cloud
    outFile.close()


def ParseCmdLine():
    parser = argparse.ArgumentParser(description="Some useful features to deal with LiDAR files.",
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument("inputfname", help="las file to be process.")
    parser.add_argument("-t", "--task", choices=['p', 'b', 'd', 'e', 's', 't', 'f', 'diff', 'pxy', 'py'], required=True,
                        help="""
Define task to be done.
  'd' display information about LAS file.
  'f' create new file with z coord = floor parameter
  't' create one slice from top, with p percent 
  'b' create one slice from bottom, with p percent 
  'p' split LAS file generating cellsize squared or numerofcells clouds.
  's' slices file in 'ns' slices, or get a slice excluding percbottom and perctop
  'e' export LAS points to csv file
  'diff' generate a new cloud that's a difference between two others
  'py' project all points to min y
  'pxy' project all points to min x, min y 
        """)
    parser.add_argument("-o", "--outputfname", help="output file name.", default=None)
    parser.add_argument("-c", "--cellsize", type=float, help="size of the cells that will be processed.", default=-1)
    parser.add_argument("-n", "--numberofcells", type=float, help="amount of cells.", default=-1)
    parser.add_argument("-f", "--floor", type=float, help="floor value for toFloor function", default=0.0)
    parser.add_argument("-sn", "--nslices", type=int, help="number of slices", default=5)
    parser.add_argument("-sz", "--slicesize", type=float, help="size of a slice", default=0.0)
    parser.add_argument("-sb", "--percbottom", type=int, help="percentual to be excluded in bottom", default=5)
    parser.add_argument("-st", "--perctop", type=int, help="percentual to be excluded on top", default=5)
    parser.add_argument("-p", "--percent", type=float, help="percent value for t or b function", default=10)
    parser.add_argument("-si", "--secondinput", type=str, help="second input file name (see -t diff option)",
                        default="")
    parser.add_argument("-v", "--verbose", type=int, help="show processing messages.", default=True)
    try:
        args = parser.parse_args()
    except Exception as e:
        print("Unexpected error:", sys.exc_info()[0])
        print(e)
        sys.exit(1)
    return args


def checkParams(args):
    if not os.path.exists(args.inputfname):
        raise Exception("File {0} doesn't exists.".format(args.inputfname))
    if (args.cellsize != -1) and (args.numberofcells != -1):
        raise Exception("You should specify only one parameter: cellsize or numberofcells")
    if (args.numberofcells > 0) and (int(args.numberofcells) % 2 != 0):
        raise Exception("numbeofcells should be odd")


def displayHeader(header):
    print("Header:")
    print("File signature : {0}".format(header.file_signature))
    print("File source id : {0}".format(header.file_source_id))
    print("Global encoding: {0}".format(header.global_encoding))
    print("Project id     : {0}".format(header.project_id))
    print("Version        : {0}".format(header.version))
    print("System id      : {0}".format(header.system_id))
    print("Software id    : {0}".format(header.software_id))
    print("Date           : {0}".format(header.date))
    print("Points count   : {0}".format(header.point_records_count))
    print("Scale x,y,z    : {0}".format(header.scale))
    print("Offset x,y,z   : {0}".format(header.offset))
    print("Min Values     : {0}".format(header.min))
    print("Max Values     : {0}".format(header.max))


def splitCells(inputfname, cellsize=-1, numberofcells=-1, verbose=False):
    start = time.time()

    inFile = file.File(inputfname, mode="r")
    accepted_logic = []  # List to save the true/false for each looping
    maxStep = []  # List to save the number of cells in X and Y dimension of original data
    warningMsg = []

    cellsizeX = 0.0
    cellSizeY = 0.0

    xmin = inFile.x.min()
    xmax = inFile.x.max()
    ymin = inFile.y.min()
    ymax = inFile.y.max()

    if (numberofcells > 0):
        cellsizeX = math.ceil((xmax - xmin) / numberofcells / 2)
        cellsizeY = math.ceil((ymax - ymin) / numberofcells / 2)
        maxStep.append(numberofcells / 2)
        maxStep.append(numberofcells / 2)
    else:
        cellsizeX = cellsize
        cellsizeY = cellsize
        maxStep.append(math.ceil((xmax - xmin) / cellsizeX))
        maxStep.append(math.ceil((ymax - ymin) / cellsizeY))

    if verbose:
        print("The original cloud was divided in {0} by {1} cells.".format(maxStep[0], maxStep[1]))

    # In[44]:

    n = 0
    for stepX in range(int(maxStep[0])):  # Looping over the lines
        for stepY in range(int(maxStep[1])):  # Looping over the columns
            # Step 1 - Filter data from the analized cell
            # Return True or False for return inside the selected cell

            X_valid = np.logical_and((inFile.x >= xmin + (stepX * cellsizeX)),
                                     (inFile.x < xmin + ((stepX + 1) * cellsizeX)))
            Y_valid = np.logical_and((inFile.y >= ymin + (stepY * cellsizeY)),
                                     (inFile.y < ymin + ((stepY + 1) * cellsizeY)))
            logicXY = np.logical_and(X_valid, Y_valid)
            validXY = np.where(logicXY)

            # show progress before 'continue'
            n += 1
            if (verbose):
                percent = n / (maxStep[0] * maxStep[1])
                hashes = '#' * int(round(percent * 20))
                spaces = ' ' * (20 - len(hashes))
                print("\r[{0}] {1:.2f}%".format(hashes + spaces, percent * 100)),

            if (len(validXY[0]) == 0):
                accepted_logic.append(False)
                if (verbose):
                    warningMsg.append(
                        "Cell {0},{1} has no points, corresponding file was not created.".format(stepX, stepY))
                continue

            fnametile = r"{0}\{1}_{2}_{3}".format(os.path.dirname(inputfname), stepX, stepY,
                                                  os.path.basename(inputfname))
            points = inFile.points[validXY]
            saveCloud(fnametile, inFile.header, points)
        # In[48]:
    inFile.close()
    if (verbose):
        print
        if (len(warningMsg) > 0):
            print
            print("Warnings:")
            print("{0}".format("\r\n".join(str(i) for i in warningMsg)))
        print
        print("Done in {0}s.".format(int(time.time() - start)))


def slices(inputfname, outputfname, nslices=1, percbottom=-1.0, perctop=-1.0, slicesize=0.0, verbose=True):
    start = time.time()
    inFile = file.File(inputfname, mode="r")
    zmin = inFile.z.min()
    zmax = inFile.z.max()
    if nslices == 1:  # one slice from percbottom to perctop
        if (percbottom == -1.0) or (perctop == -1.0):
            raise Exception("You must specify nslices > 0 or bottom and and top > 0")
        hbottom = (zmax - zmin) * percbottom / 100.0 + zmin
        htop = (zmax - zmin) * (100 - perctop) / 100.0 + zmin

        Z_valid = np.logical_and((inFile.z >= hbottom), (inFile.z <= htop))
        validZ = np.where(Z_valid)
        fnameslice = "slice{0}_{1}_{2}".format(percbottom, perctop, os.path.basename(inputfname))
        saveCloud(fnameslice, inFile.header, inFile.points[validZ])
        return
    else:
        if slicesize > 0.0:
            nslices = (zmax - zmin) / slicesize
    warningMsg = []

    hn = (zmax - zmin) / nslices
    accepted_logic = []  # List to save the true/false for each looping
    for stepZ in range(int(nslices) + 1):
        Z_valid = np.logical_and(inFile.z >= zmin + (stepZ * hn),
                                 inFile.z < zmin + ((stepZ + 1) * hn))
        validZ = np.where(Z_valid)

        # show progress before 'continue'
        if (verbose):
            percent = float(stepZ + 1) / nslices
            hashes = '#' * int(round(percent * 20))
            spaces = ' ' * (20 - len(hashes))
            print("\r[{0}] {1:.2f}%".format(hashes + spaces, percent * 100)),
        if (len(validZ[0]) == 0):
            accepted_logic.append(False)
            if (verbose):
                warningMsg.append("Slice {0} has no points, corresponding file was not created.".format(stepZ))
            continue
        if outputfname != None:
            fnameslice = r"{0}\{1:03d}_{2}".format(os.path.dirname(outputfname), stepZ, os.path.basename(outputfname))
        else:
            fnameslice = r"{0}\{1:03d}_{2}".format(os.path.dirname(inputfname), stepZ, os.path.basename(inputfname))
        valid = inFile.points[validZ]
        saveCloud(fnameslice, inFile.header, valid)

    inFile.close()
    if (verbose):
        print
        if (len(warningMsg) > 0):
            print
            print("Warnings:")
            print("{0}".format("\r\n".join(str(i) for i in warningMsg)))
        print
        print("Done in {0}s.".format(int(time.time() - start)))


def toFloor(inputfname, outputfname=None, floor=0.0):
    inFile = file.File(inputfname, mode="r")
    outputfname = outputfname if not (outputfname == None) else "toFloor_" + os.path.basename(inputfname)
    outFile = file.File(outputfname, mode="w", header=inFile.header)
    outFile.points = inFile.points
    z = outFile.z
    z.fill(floor)
    outFile.z = z
    inFile.close()
    outFile.close()


def topBottom(command, inputfname, outputfname=None, cut=None, cutpercent=None):
    if (cut == None) and (cutpercent == None):
        Exception("You should inform cut or cutpercent")
    inFile = file.File(inputfname, mode="r")
    if (cutpercent > 0):
        r = (inFile.z.max() - inFile.z.min()) * cutpercent / 100.0 + inFile.z.min()
    else:
        r = cut
    if (command == 'b'):
        Z_valid = np.logical_and(inFile.z <= r, True)
        strFunc = 'bottom_'
    else:  # top
        Z_valid = np.logical_and(inFile.z >= r, True)
        strFunc = 'top_'
    validZ = np.where(Z_valid)
    outputfname = outputfname if not (outputfname == None) else strFunc + os.path.basename(inputfname)
    saveCloud(outputfname, inFile.header, inFile.points[validZ])
    inFile.close()


def exportToCSV(inputfname, outputfname=None, delimiter=";"):
    inFile = file.File(inputfname, mode="r")
    if (outputfname == None):
        outputfname = inputfname.rsplit(".", 1)[0] + ".csv"
    headercsv = ""
    for spec in inFile.point_format:
        headercsv += "{0}{1}".format(spec.name, delimiter)
    headercsv = headercsv[:-1]

    output = open(outputfname, "w")

    output.write(headercsv + "\n")

    for data_tile in inFile.points:
        txtline = ""
        for line in data_tile:
            for value in line:
                txtline += "{0}{1}".format(value, delimiter)
            output.write(txtline[:-1] + "\n")
    output.close()
    inFile.close()


def displayInfo(inputfname):
    inFile = file.File(inputfname, mode="r")
    displayHeader(inFile.header)
    print("\r\nPoint format:")
    for spec in inFile.point_format:
        print(spec.name)
    inFile.close()


def projectY(inputfname, outputfname=None):
    inFile = file.File(inputfname, mode="r")
    outputfname = outputfname if not (outputfname == None) else "projectY_" + os.path.basename(inputfname)
    outFile = file.File(outputfname, mode="w", header=inFile.header)
    outFile.points = inFile.points
    y = outFile.y
    y.fill(outFile.header.min[1])
    outFile.y = y
    outFile.close()
    inFile.close()


def projectXY(inputfname, outputfname=None):
    inFile = file.File(inputfname, mode="r")
    outputfname = outputfname if not (outputfname == None) else "projectXY_" + os.path.basename(inputfname)
    outFile = file.File(outputfname, mode="w", header=inFile.header)
    outFile.points = inFile.points
    x = outFile.x
    x.fill(outFile.header.min[0])
    outFile.x = x
    y = outFile.y
    y.fill(outFile.header.min[1])
    outFile.y = y
    outFile.close()
    inFile.close()


def cloudDifference(firstfilename, secondfilename, outputfname=None):
    firstFile = file.File(firstfilename, mode="r")
    secondFile = file.File(secondfilename, mode="r")
    outputfname = outputfname if not (outputfname == None) else "Diff_{0}_{1}".format(
        os.path.splitext(os.path.basename(firstfilename))[0], os.path.basename(secondfilename))
    points = np.setdiff1d(firstFile.points, secondFile.points)
    saveCloud(outputfname, firstFile.header, points)


def main():
    warnings.simplefilter("error", RuntimeWarning)
    args = ParseCmdLine()
    checkParams(args)
    if (args.task == 'p'):
        splitCells(args.inputfname, args.cellsize, args.numberofcells, args.verbose)
    elif (args.task == 's'):
        #        inputfname,nslices=1,percbottom=-1.0,perctop=-1.0,slicesize=0.0,verbose=True
        slices(args.inputfname, args.outputfname, args.nslices, args.percbottom, args.perctop, args.slicesize,
               args.verbose)
    elif (args.task == 'd'):
        displayInfo(args.inputfname)
    elif (args.task == 'e'):
        exportToCSV(args.inputfname, args.outputfname, ";")
    elif (args.task == 'f'):
        toFloor(args.inputfname, args.outputfname, args.floor)
    elif ((args.task == 'b') or (args.task == 't')):
        topBottom(args.task, args.inputfname, args.outputfname, args.percent)
    elif (args.task == 'diff'):
        cloudDifference(args.inputfname, args.secondinput, args.outputfname)
    elif (args.task == 'py'):
        projectY(args.inputfname, args.outputfname)
    elif (args.task == 'pxy'):
        projectXY(args.inputfname, args.outputfname)


# In[ ]:

if __name__ == "__main__":
    main()
