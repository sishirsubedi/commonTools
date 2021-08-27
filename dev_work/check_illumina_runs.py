import sys
import os
import subprocess
import optparse
from datetime import datetime
from pathlib import Path
import pandas as pd

def bashCommunicator(command,output_expected=False):
	process = subprocess.Popen([command],shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True)
	stdout, stderr = process.communicate()
	if process.returncode != 0:
		print("Process failed %s %d %s %s" % (command,process.returncode, stdout, stderr))
	else:
		if output_expected:
			return [x for x in stdout.split("\n")]

def read_xml(run_file,titles):
	from bs4 import BeautifulSoup
	infile = open(run_file,"r")
	contents = infile.read()
	soup = BeautifulSoup(contents,'xml')
	return  [soup.find_all(title)[0].get_text() for title in titles]

class Run:
	def __init__(self, elements):
		self.runid = elements[0]
		self.instrument = elements[1]
		self.experimentname = None
		self.start = None
		self.runstatus = None
		self.samplesheetstatus = None
		self.bcl2fastqstatus = None

	def check_run_params(self):
		run_params_file = HOME+"/"+self.instrument+"/"+self.runid+"/RunParameters.xml"
		self.experimentname = read_xml(run_params_file,["ExperimentName"])[0]

	def check_run_info(self):
		run_info_file = HOME+"/"+self.instrument+"/"+self.runid+"/RunInfo.xml"
		self.start = read_xml(run_info_file,["Date"])[0]

	def check_runstatus(self):
		chk_file = Path(HOME+"/"+self.instrument+"/"+self.runid+"/CopyComplete.txt")
		if chk_file.is_file(): self.runstatus = "Complete"
		else: self.runstatus = "NO"

	def check_samplesheetstatus(self):
		chk_file = Path(HOME+"/"+self.instrument+"/"+self.runid+"/SampleSheet.csv")
		if chk_file.is_file(): self.samplesheetstatus = "Present"
		else: self.samplesheetstatus = "NO"

	def check_bcl2fastqstatus(self):
		self.bcl2fastqstatus = "NO"
		chk_dir = Path(HOME+"/"+self.instrument+"/"+self.runid+"/out1")
		if chk_dir.is_dir(): self.bcl2fastqstatus = "Present_Clinical"

		chk_dir = Path(HOME+"/"+self.instrument+"/"+self.runid+"/out2")
		if chk_dir.is_dir(): self.bcl2fastqstatus = "Present_Research"

	def check_all(self):
		self.check_run_params()
		self.check_run_info()
		self.check_runstatus()
		self.check_samplesheetstatus()
		self.check_bcl2fastqstatus()

def find_runs(instrument,df):
	HOME_instrument=HOME+instrument+"/"
	cmd= " find "+HOME_instrument+" -maxdepth 1 -mtime -"+str(DAYS)+" -type d "
	dirs = bashCommunicator(cmd,output_expected=True)
	for d in dirs:
		path_list = d.split("/")
		if len(path_list)==5 and path_list[4]!="" and path_list[4]!="MyRun":
			runid = path_list[4]
			run = Run([runid,instrument])
			run.check_all()
			df = df.append((vars(run)),ignore_index=True)
	return df


try:
	HOME="/storage/instruments/"
	OUT="/storage/analysis/environments/ngs_maintain/"
	DAYS=30
	df=pd.DataFrame(columns=['runid','instrument','experimentname','start','runstatus','samplesheetstatus','bcl2fastqstatus'])
	df = find_runs("novaseq",df)
	df = find_runs("nextseq",df)
	df["to_check"] = [ 1 if (x!="Complete" or y!="Present" or "Present" not in z) else 0 for x,y,z in zip(df.runstatus,df.samplesheetstatus,df.bcl2fastqstatus)]
	df.to_csv(OUT+"illumina_runs.csv",index=False)


except TypeError:
	print ("python account_control.py -help for help"+TypeError)
