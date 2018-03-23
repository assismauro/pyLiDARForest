# -*- coding: utf-8 -*-
import argparse
import sys

import pyForestLASTools


def Header():
    print('Calculate metrics using LASTools v0.8')
    print


def ParseCmdLine():
    #   G:\TRANSECTS\LAZ\NP_T-0645.laz -step 20 -lp c:\lastools\bin -metrics "-p 5 10 25 50 75 90 -b 5 10 25 50 75 90 -min -max- avg -std -ske -kur -qav -cov -dns -c 0.5 2 4 10 20 50 -d 0.5 2 4 10 20 50" -fo ASC -co 1 -v 1
    #   G:\TRANSECTS\LAZ\NP_T-0645.laz -o G:\TRANSECTS\LAZ\  -lp 'c:\lastools\bin' -v 1
    parser = argparse.ArgumentParser(description='# Calculate transect metrics.')
    parser.add_argument('inputfname', help='File mask to be processed.')
    parser.add_argument('-o', '--outputpath', help='Output file path.', default="")
    parser.add_argument('-df', '--destinationformat',
                        help='CSV, BIL, ASC, IMG, TIF, XYZ, FLT, or DTM format, default CSV.', default='CSV')
    parser.add_argument('-lp', '--lastoolspath', help=r'LASTools bin path, default c:\lastools\bin',
                        default=r'c:\lastools\bin')
    parser.add_argument('-s', '--step', help='Side length of grid', type=float, default=20)
    parser.add_argument('-opt', '--options', help='Additional options.', default="")
    parser.add_argument('-t', '--tile', help='Tile files before lasground', action='store_true')
    parser.add_argument('-d', '--deletetempfiles', help='Delete temporary files', action='store_true')
    parser.add_argument('-p', '--prepare', help='If false, calculates only metrics, without any LAS preprocessing.',
                        action='store_true')
    parser.add_argument('-c', '--cores', help='Number of cores to be used', type=int, default=1)
    parser.add_argument('-topt', '--tileoptions', help='Tile options', type=str, default='-tile_size 1000 -buffer 100')
    #    parser.add_argument('-m','--metrics', help = 'Metrics to be calculated.',default="")
    parser.add_argument('-co', '--commandonly', help='Just show commands, withou run it.', action='store_true')
    parser.add_argument('-v', '--verbose', help='Show intermediate messages.', action='store_true')

    try:
        return parser.parse_args()
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise


if __name__ == '__main__':
    Header()

    args = ParseCmdLine()
    forestLT = pyForestLASTools.pyForestLASTools(inputfname=args.inputfname, outputpath=args.outputpath, rootdir="",
                                                 lastoolspath=args.lastoolspath, commandonly=args.commandonly,
                                                 verbose=args.verbose, cores=args.cores)
    try:
        # lascanopy -i G:\TRANSECTS\LAZ\metrics\????????????????_ch1_5.laz -odir G:\TRANSECTS\LAZ\metrics\ -step 50.0 -all -min -max -avg -std -ske -kur -qav -p 5 10 20 30 40 50 60 70 80 90 -b 5 10 20 30 40 50 60 70 80 90  -c 0 1 2.5 5.0 7.5 10 15 20 25 30 -d 0 1 2.5 5.0 7.5 10 15 20 25 30  -int_min -int_max -int_avg -int_std -int_ske -int_kur -int_qav -cov -dns -gap -height_cutoff 0.0 -drop_z_below 0.0
        metrics = '-all -min -max -avg -std -ske -kur -qav -p 1 5 10 20 25 30 40 50 60 70 75 80 90 95 99 -b 5 10 20 30 40 50 60 70 80 90  -c 0 1 2.5 5.0 7.5 10 15 20 25 30 -d 0 1 2.5 5.0 7.5 10 15 20 25 30 -cov -dns -gap -height_cutoff 0.1 -drop_z_below 0.1 -fractions'
        #        if args.options == "":
        #            options='-cov -dns -gap -cover_cutoff 1.3 -height_cutoff 1.3'
        #        else:
        #            options=args.options
        forestLT.metrics(extension=args.destinationformat, step=args.step, metrics=metrics, tile=args.tile,
                         tileoptions=args.tileoptions, deletetempfiles=args.deletetempfiles, prepare=args.prepare)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
