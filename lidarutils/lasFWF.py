# -*- coding: utf-8 -*-
import os
import struct

import laspy
import numpy as np


class FWFFile(laspy.file.File):
    def __init__(self, filename,
                   header=None,
                   vlrs=False,
                   mode='r',
                   in_srs=None,
                   out_srs=None,
                   evlrs = False):
        self.fwffilename=os.path.splitext(filename)[0]+'.wdp'
        self.fwfsize=os.path.getsize(self.fwffilename)
        self.fwffile=open(self.fwffilename,'rb')
        super(FWFFile,self).__init__(filename,header,vlrs,mode,in_srs,out_srs,evlrs)

    def GetWave(self, index=-1):
        #        if (index == -1):
        #            self.fwffile.seek(position, os.SEEK_SET)
        #            return np.fromfile(self.fwffile,dtype=np.int16,count=length)
        #        else:
        #            self.fwffile.seek(self.byte_offset_to_waveform_data[index], os.SEEK_SET)
        #            return np.fromfile(self.fwffile,dtype=np.int16,count=self.waveform_packet_size[index] / 2)
        return Waves(self, index)

    def close(self,ignore_header_changes=False,minmax_mode='scaled'):
        self.fwffile.close()
        super(FWFFile, self).close(ignore_header_changes,minmax_mode)


class Waves(object):
    def __init__(self, index):

        # jump to the start of the wave
        self.fwffile.seek(self.byte_offset_to_waveform_data[index], os.SEEK_SET)

        # get damples
        samples = np.fromfile(self.fwffile, dtype=np.int16, count=self.waveform_packet_size[index] / 2)

        # cycle through each sample
        for sample in range(samples):

            sample_record = sample_records[key]
            duration_anchor = struct.unpack("=L", wavebinary.read(sample_record.bits_anchor / 8))[0]
            num_samples = struct.unpack("=h", wavebinary.read(sample_record.bits_samples / 8))[0]

            samples = []
            for sample_num in range(num_samples):
                sample = struct.unpack("=h", wavebinary.read(sample_record.bits_per_sample / 8))[0]
                # calculate 3 dimensional sample coordinates
                x = pulse_record.x_anchor + (duration_anchor + sample_num) * pulse_record.dx
                y = pulse_record.y_anchor + (duration_anchor + sample_num) * pulse_record.dy
                z = pulse_record.z_anchor + (duration_anchor + sample_num) * pulse_record.dz
                samples.append([x, y, z, sample])

            self.segments[key] = np.array(samples).T

        wavebinary.close()
