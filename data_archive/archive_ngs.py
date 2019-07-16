import sys
import subprocess
import os
import glob
import optparse

class archiver:
    def __init__(self,instrument,delList):
        self.instrument = instrument
        self.instrument_home = "/home/"+self.instrument+"/"
        self.delList = delList
        self.runs = []

    def findRuns(self):
        cmd = "find %s -maxdepth 1 -type d -mtime +750 | cut -d '/' -f 4" %self.instrument_home
        self.runs = [x for x in bashCommunicator(cmd,True) if "_" in x]

    def deleteReqFiles(self):
        for run in self.runs:
            run_home = self.instrument_home+run
            for file_ext in self.delList:
                print("Processing run - "+run+" from " + self.instrument_home + " with extension "+file_ext)
                cmd = "sudo find %s -mindepth 1  -type f -name %s " %(run_home , "*."+file_ext)
                temp = [x for x in bashCommunicator(cmd,True) if "/" in x]
                if len(temp) >0:
                    print("ready to delete *." + file_ext + " files from run- "+run)
                    self.deleteFiles(temp)
                else:
                    print("No files to delete *." + file_ext + " files from run- "+run)
            break

    def deleteFiles(self,filestodel):
        for file in filestodel:
            # cmd = "sudo rm -f %s " %(file)
            # bashCommunicator(cmd)
            print("deleted- " + file)

    def compressRuns(self):
        for run in self.runs:
            archive_file = "/archive/"+self.instrument+"ARCHIVE/"+run+".tar.gz"
            org_file =self.instrument_home+run+'/'
            # check to make sure files is not already present
            cmd = "sudo  tar -czf %s %s*" %(archive_file, org_file)
            bashCommunicator(cmd)


def bashCommunicator(command,output_expected=False):
    process = subprocess.Popen([command],shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print("Process failed %s %d %s %s" % (command,process.returncode, stdout, stderr))
    else:
        if output_expected:
            return [x for x in stdout.split("\n")]


def run_archive(instrument,delList):
    worker = archiver(instrument,delList)
    worker.findRuns()
    worker.deleteReqFiles()
    # worker.compressRuns()


if len(sys.argv) > 1:
    parser = optparse.OptionParser()
    parser.add_option('-i', '--instrument')
    parser.add_option('-d', '--deleteList')
    options,args = parser.parse_args()
    instrument = options.instrument
    delList = options.deleteList.split(",")
    run_archive(instrument,delList)

else:
    print("python archive_ngs.py -h for help")
