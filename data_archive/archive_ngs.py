import sys
import subprocess
import os
import glob
import optparse

class archiver:
    def __init__(self,instrument,keepExt):
        self.instrument = instrument
        self.instrument_home = "/home/"+self.instrument+"/"
        self.keepExt = keepExt
        self.runs = []

    def findRuns(self):
        # cmd = "find %s -maxdepth 1 -type d -mtime +1520 | cut -d '/' -f 4" %self.instrument_home
        cmd = "find %s -maxdepth 1 -type d -name '150429_NS500761_0003xx_AH73NJBGXX' | cut -d '/' -f 4" %self.instrument_home
        self.runs = [x for x in bashCommunicator(cmd,True) if "_" in x]
        print("processing:")
        if len(self.runs)>0:
            for run in self.runs:print(run)
        else: print("No runs to process!!")


    def deleteReqFiles(self):
        for run in self.runs:
            run_home = self.instrument_home+run
            print("Processing run - "+run+" from " + self.instrument_home + " keeping files with extension "+self.keepExt)
            cmd = "sudo find %s -mindepth 1  -type f -not -name  %s -not -name  %s " %(run_home , "*."+self.keepExt ,"*."+self.keepExt+".gz")
            files_to_del = [x for x in bashCommunicator(cmd,True) if "/" in x]
            if len(files_to_del) >0:
                self.deleteFiles(files_to_del)
            else:
                print("No files to delete from run- "+run)

    def deleteFiles(self,files_to_del):
        for file in files_to_del:
            cmd = "sudo rm -f %s " %(file)
            bashCommunicator(cmd)
            print("deleted- " + file)

    def compressRuns(self):
        for run in self.runs:
            archive_file = "/archive/"+self.instrument+"ARCHIVE/"+run+".tar.gz"
            org_file =self.instrument_home+run+'/'
            cmd = "sudo  tar -czf %s %s*" %(archive_file, org_file)
            bashCommunicator(cmd)

    def deleteOriginalRun(self):
        for run in self.runs:
            org_file =self.instrument_home+run
            cmd = "sudo rm -rf %s" %( org_file)
            bashCommunicator(cmd)

def bashCommunicator(command,output_expected=False):
    process = subprocess.Popen([command],shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print("Process failed %s %d %s %s" % (command,process.returncode, stdout, stderr))
    else:
        if output_expected:
            return [x for x in stdout.split("\n")]


def run_archive(instrument,keepExt):

    worker = archiver(instrument,keepExt)
    worker.findRuns()

    if keepExt != "none":
        worker.deleteReqFiles()

    worker.compressRuns()
    worker.deleteOriginalRun()


if len(sys.argv) > 1:
    parser = optparse.OptionParser()
    parser.add_option('-i', '--instrument')
    parser.add_option('-d', '--keepExt')
    options,args = parser.parse_args()
    instrument = options.instrument
    keepExt = options.keepExt
    run_archive(instrument,keepExt)

else:
    print("python archive_ngs.py -h for help")
