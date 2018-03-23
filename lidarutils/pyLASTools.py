import os
import subprocess
from sys import platform as _platform

class pyLASTools(object):
    """Implements a Python interface to LASTools command line tools"""

    def __init__(self, lastoolspath, cores=1):
        self.isamac = _platform == "darwin"

        if not self.isamac and (lastoolspath == ""):
            lastoolspath = r"c:\lastools\bin"

        self.lastoolspath = lastoolspath + ("" if lastoolspath.endswith(os.sep) else os.sep)
        self.cores=cores

    def runcommand(self,command,commandonly,verbose):
        cmd="{0}{1}".format(self.lastoolspath,command)
        if self.isamac:
            command="wine "+cmd
        else:
            command=cmd
        print command
        if commandonly:
            return None,
        if verbose > 0:
            print command
        if self.isamac:
            p = subprocess.Popen(command,shell=True)
        else:
            p = subprocess.Popen(command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT)
        out, err = p.communicate()
        if ((out != None) and ("ERROR" in out)) or ((err != None) and ("ERROR" in err)):
            Exception("Error in command: {0} Message: {1}{2}".format(command,out,err))
        if verbose > 0:
            print(out)
        return out, err

    def lasnoise(self,inputfname,outputfname="",options="",commandonly=False,verbose=False):
        self.runcommand(r"lasnoise -i {0} {1} {2} -cores {3}".format(inputfname,"-o {0}".format(outputfname) if outputfname != "" else "",options,self.cores),commandonly,verbose)

    def lasground(self,inputfname,outputfname="",options="",commandonly=False,verbose=False):
        self.runcommand(r"lasground -i {0} {1} {2} -cores {3}".format(inputfname,"-o {0}".format(outputfname) if outputfname != "" else "",options,self.cores),commandonly,verbose)
       
    def lasheight(self,inputfname,outputfname="",options="",commandonly=False,verbose=False):
        self.runcommand(r"lasheight -i {0} {1} {2} -cores {3}".format(inputfname,"-o {0}".format(outputfname) if outputfname != "" else "",options,self.cores),commandonly,verbose)
    
    def las2las(self,inputfname,outputfname="",options="",commandonly=False,verbose=False):
        self.runcommand(r"las2las -i {0} {1} {2} -cores {3}".format(inputfname,"-o {0}".format(outputfname) if outputfname != "" else "",options,self.cores),commandonly,verbose)

    def lasclassify(self,inputfname,outputfname="",options="",commandonly=False,verbose=False):
        self.runcommand(r"lasclassify -i {0} {1} {2} -cores {3}".format(inputfname,"-o {0}".format(outputfname) if outputfname != "" else "",options,self.cores),commandonly,verbose)

    def blast2dem(self,inputfname,outputfname="",step=0.5,options="",commandonly=False,verbose=False):
        self.runcommand(r"blast2dem -i {0} {1} -step {2} {3} -cores {4}".format(inputfname,"-o {0}".format(outputfname) if outputfname != "" else "",step,options,self.cores),commandonly,verbose)

    def lastile(self,inputfname,outputfname="",options="",commandonly=False,verbose=False):
        # cores = 1, it looks like there is a problem if we put more than 1 core in lastile
        self.runcommand(r"lastile -i {0} {1} {2} -cores {3}".format( \
            inputfname, "-o {0}".format(outputfname) if outputfname != "" else "", options, 1), commandonly, verbose)

    def lasthin(self,inputfname,outputfname="",options="",commandonly=False,verbose=False):
        self.runcommand(r"lasthin -i {0} {1} {2} -cores {3}".format(\
            inputfname,"-o {0}".format(outputfname) if outputfname != "" else "",options,self.cores),commandonly,verbose)

    def lasmerge(self,inputfname,outputfname="",options="",commandonly=False,verbose=False):
        self.runcommand(r"lasmerge -i {0} {1} {2} -cores {3}".format(\
            inputfname,"-o {0}".format(outputfname) if outputfname != "" else "",options,self.cores),commandonly,verbose)

    def lasgrid(self,inputfname,outputfname,step=0.5,options="",commandonly=False,verbose=False):
        self.runcommand(r"lasgrid -i {0} -step {1} -average {2} -mem 1900 -cores {3}".format(inputfname,step,"-o {0}".format(outputfname) if outputfname != "" else "",self.cores),commandonly,verbose)

    def lascanopy(self,inputfname,outputfname="",step=0.5,options="",
                  commandonly=False,verbose=False):
        self.runcommand(r"lascanopy -i {0} {1} {2} {3} -cores {4}".format(inputfname, "-o {0}".format(
            outputfname) if outputfname != "" else "", "-step {0}" if step > 0.0 else "", options, self.cores),
                        commandonly, verbose)

    def lasinfo(self, inputfname, outputfname="", options="", commandonly=False, verbose=False):
        return self.runcommand(r"lasinfo -i {0} {1} {2} -cores {3}".format(inputfname, "-o {0}".format(
            outputfname) if outputfname != "" else "", options, self.cores), commandonly, verbose)
