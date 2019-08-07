# This script is used to archive /home/instrument and /home/environment/instrumentAnalysis folders
# Logic:
# - keep fastq files and delete everything from instrument folders
# - delete bam files and keep everythiong from instrumentAnalysis folders

import sys
import subprocess
import os
import glob
import optparse

class archiver:
    def __init__(self,input,output,tag):
        self.input = input
        self.output = output
        self.tag = tag
        self.runs = []

    def findRuns(self):

        #cmd = "find %s  -maxdepth 1 -type d -mtime +1250 -exec du -ks {} + | awk '$1 <= 50000000' | cut -d '/' -f 4" %self.instrument_home
        # cmd = "find %s -maxdepth 1 -type d -mtime +1250 | cut -d '/' -f 4" %self.instrument_home

        cmd = "find %s -maxdepth 1 -type d -name '19*' | awk -F/ '{print $NF}' " %self.input

        self.runs = [x for x in bashCommunicator(cmd,True) if "_" in x]

        print("processing:")
        if len(self.runs)>0:
            for run in self.runs:
                print(run)
        else: print("No runs to process!!")


    def deleteReqFiles(self):

        for run in self.runs:

            run_home = self.input+run+"/"

            tag_key = self.tag.split(':')[0]
            tag_ext = self.tag.split(':')[1]

            cmd = ""

            if tag_key == "keep":
                print("Processing run - "+run+" from " + self.input + " keeping files with extension "+tag_ext)
                cmd = "sudo find %s -mindepth 1  -type f -not -name  %s -not -name  %s " %(run_home , "*." + tag_ext ,"*." + tag_ext + ".gz")
            elif tag_key == "delete":
                print("Processing run - "+run+" from " + self.input + " deleting files with extension "+tag_ext)
                cmd = "sudo find %s -mindepth 1  -type f -name  %s " %(run_home , "*." + tag_ext)

            files_to_del = [x for x in bashCommunicator(cmd,True) if "/" in x]

            if len(files_to_del) >0:
                self.deleteFiles(files_to_del)
            else:
                print("No files to delete from run- " + run)

            break

    def deleteFiles(self,files_to_del):
        for file in files_to_del:
            # cmd = "sudo rm -f %s " %(file)
            # bashCommunicator(cmd)
            print("deleted- " + file)

    def compressRuns(self):
        for run in self.runs:
            archive_file = self.output+run+".tar.gz"
            org_file =self.input+run+'/'
            cmd = "sudo  tar -czf %s %s*" %(archive_file, org_file)
            bashCommunicator(cmd)
            print("compressed- " + org_file)
            print("archived- " + archive_file)


    def deleteOriginalRun(self):
        for run in self.runs:
            org_file =self.input+run
            cmd = "sudo rm -rf %s" %( org_file)
            bashCommunicator(cmd)
            print("deleted original run " + org_file)

def bashCommunicator(command,output_expected=False):
    process = subprocess.Popen([command],shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print("Process failed %s %d %s %s" % (command,process.returncode, stdout, stderr))
    else:
        if output_expected:
            return [x for x in stdout.split("\n")]


def run_archive(input,output,tag):

    worker = archiver(input,output,tag)
    worker.findRuns()

    if tag != "none":
        worker.deleteReqFiles()

    print("Processing without Deletion !")

    # worker.compressRuns()
    # worker.deleteOriginalRun()


if len(sys.argv) > 1:
    parser = optparse.OptionParser()
    parser.add_option('-i', '--input_directory')
    parser.add_option('-o', '--output_directory')
    parser.add_option('-t', '--tag')
    options,args = parser.parse_args()
    input = options.input_directory
    output = options.output_directory
    tag = options.tag
    run_archive(input,output,tag)

else:
    print("python archive_ngs.py -h for help")
