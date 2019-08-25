#!/usr/bin/env python

import os,sys
import argparse
import commands
import subprocess
import shutil
from time import strftime

date_and_time=strftime("%Y%m%d_%H%M%S")

usage = "usage: %prog [options]"
parser = argparse.ArgumentParser(usage)
parser.add_argument("--noSubmit", dest="noSubmit", help="do not submit to cluster"   , default=False, action="store_true")
parser.add_argument("--run"     , dest="run"     , help="Which run, you better know" , type=str, default="MC")
parser.add_argument("--pfa"     , dest="pfa"     , help="Which PFA to use"           , type=int, required=True)
parser.add_argument("--era"     , dest="era"     , help="Run2 or Run3"               , type=str, default="Run3")
parser.add_argument("--filelist", dest="filelist", help="Unique name for filelist"    , type=str, default="TTbar_50PU_Run3")
parser.add_argument("--tag"     , dest="tag"     , help="Unique tag"    , type=str, required=True)

arg = parser.parse_args()

inputFiles = []

inputFiles = ["root://cmsxrootd.fnal.gov/" + line.rstrip("\n") for line in open("./input/filelist/%s.txt"%(arg.filelist))]
if not os.path.isfile("./input/filelist/%s.txt"%(arg.tag)):
    print "Could not find input file list!"
    quit()

taskDir = date_and_time
outputDir = "root://cmseos.fnal.gov//store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/%s"%(str(arg.tag))
workingDir = "/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/condor/%s"%(taskDir)

subprocess.call(["eos", "root://cmseos.fnal.gov", "mkdir", "-p", outputDir[23:]])
os.makedirs(workingDir)

shutil.copy2("/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/scripts/analyze_HcalTrig.py", "/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/condor/%s"%(taskDir))

if outputDir.split("/")[-1] == "": outputDir = outputDir[:-1]
if workingDir.split("/")[-1] == "": workingDir = workingDir[:-1]

# Write .sh script to be run by Condor
scriptFile = open("%s/runJob.sh"%(workingDir), "w")
scriptFile.write("#!/bin/bash\n\n")
scriptFile.write("INPUTFILE=$1\n")
scriptFile.write("STUB=$2\n")

# Create directories to save log, submit, and mac files if they don't already exist
logDir="%s/logs"%(workingDir)
os.mkdir(logDir) # make the log directory

scriptFile.write("SCRAM_ARCH=slc7_amd64_gcc700\n")
scriptFile.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n") 
scriptFile.write("eval `scramv1 project CMSSW CMSSW_10_6_0_pre4`\n")
scriptFile.write("cd CMSSW_10_6_0_pre4\n")
scriptFile.write("tar -xf ./../CMSSW_10_6_0_pre4.tar.xz\n")
scriptFile.write("rm ./../CMSSW_10_6_0_pre4.tar.xz\n")
scriptFile.write("cd src\n")
scriptFile.write("eval `scramv1 runtime -sh`\n")
scriptFile.write("eval `scramv1 b -j 10`\n")
scriptFile.write("cd ./../..\n")
scriptFile.write("cmsRun analyze_HcalTrig.py %s %s %s ${INPUTFILE} ${STUB}\n"%(arg.pfa,arg.run,arg.era))
scriptFile.write("xrdcp -f hcalNtuple_${STUB}.root %s/hcalNtuple_${STUB}.root 2>&1\n"%(outputDir))
scriptFile.write("cd ${_CONDOR_SCRATCH_DIR}\n")
scriptFile.write("rm -r analyze_HcalTrig.py CMSSW_10_6_0_pre4 hcalNtuple_${STUB}.root\n")
scriptFile.close()

# Write Condor submit file 
condorSubmit = open("%s/condorSubmit.jdl"%(workingDir), "w")
condorSubmit.write("Executable          =  %s\n"%(scriptFile.name))
condorSubmit.write("Universe            =  vanilla\n")
condorSubmit.write("Requirements        =  OpSys == \"LINUX\" && Arch ==\"x86_64\"\n")
condorSubmit.write("Request_Memory      =  5 Gb\n")
condorSubmit.write("Output = ./logs/$(Cluster)_$(Process).stdout\n")
condorSubmit.write("Error = ./logs/$(Cluster)_$(Process).stderr\n")
condorSubmit.write("Log = ./logs/$(Cluster)_$(Process).log\n")
condorSubmit.write("Transfer_Input_Files = /uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/condor/%s/analyze_HcalTrig.py, /uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/input/CMSSW_10_6_0_pre4.tar.xz\n"%(taskDir))
condorSubmit.write("x509userproxy = $ENV(X509_USER_PROXY)\n")

for inputFile in inputFiles:
    
    stub = inputFile.split("/")[-1].split(".root")[0]
    condorSubmit.write("Arguments       = %s %s\n"%(inputFile, stub))
    condorSubmit.write("Queue\n\n")

condorSubmit.close()

os.system("chmod +x %s"%(scriptFile.name))

if arg.noSubmit: quit()

os.system("condor_submit " + condorSubmit.name)
