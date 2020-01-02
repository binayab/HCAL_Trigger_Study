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
parser.add_argument("--run"     , dest="run"     , help="Which run, you better know" , type=str, required=True)
parser.add_argument("--tag"     , dest="tag"     , help="Unique tag" , type=str, default="")

arg = parser.parse_args()

rootDir = "store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples"
inputFilesPFA2 = ["root://cmsxrootd.fnal.gov//%s/%s/%s/PFA2/"%(rootDir,arg.run,arg.tag) + aFile for aFile in os.listdir("/eos/uscms/%s/%s/%s/PFA2/"%(rootDir,arg.run,arg.tag))]
inputFilesPFA3 = ["root://cmsxrootd.fnal.gov//%s/%s/%s/PFA3/"%(rootDir,arg.run,arg.tag) + aFile for aFile in os.listdir("/eos/uscms/%s/%s/%s/PFA3/"%(rootDir,arg.run,arg.tag))]

taskDir = date_and_time
outputDir = "/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/plots/%s/ratios/%s"%(arg.run,arg.tag)
workingDir = "/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/condor/%s"%(taskDir)

#subprocess.call(["eos", "root://cmseos.fnal.gov", "mkdir", "-p", outputDir[23:]])
if not os.path.exists(outputDir): os.makedirs(outputDir)
if not os.path.exists(workingDir): os.makedirs(workingDir)

shutil.copy2("/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/scripts/ratioStudyPlotter.py", "/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/condor/%s"%(taskDir))

if outputDir.split("/")[-1] == "": outputDir = outputDir[:-1]
if workingDir.split("/")[-1] == "": workingDir = workingDir[:-1]

# Write .sh script to be run by Condor
scriptFile = open("%s/runJob.sh"%(workingDir), "w")
scriptFile.write("#!/bin/bash\n\n")
scriptFile.write("INPUTFILEPFA2=$1\n")
scriptFile.write("INPUTFILEPFA3=$2\n")

# Create directories to save log, submit, and mac files if they don't already exist
logDir="%s/logs"%(workingDir)
os.mkdir(logDir) # make the log directory

scriptFile.write("SCRAM_ARCH=sl6_amd64_gcc700\n")
scriptFile.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n") 
scriptFile.write("eval `scramv1 project CMSSW CMSSW_10_4_0_patch1`\n")
scriptFile.write("cd CMSSW_10_4_0_patch1/src\n")
scriptFile.write("eval `scramv1 runtime -sh`\n")
scriptFile.write("cd ./../..\n")
scriptFile.write("python ratioStudyPlotter.py ${INPUTFILEPFA2} ${INPUTFILEPFA3}\n")
scriptFile.write("ls -l\n")
scriptFile.write("cd ${_CONDOR_SCRATCH_DIR}\n")
scriptFile.write("rm -r ratioStudyPlotter.py CMSSW_10_4_0_patch1\n")
scriptFile.close()

# Write Condor submit file 
condorSubmit = open("%s/condorSubmit.jdl"%(workingDir), "w")
condorSubmit.write("Executable          =  %s\n"%(scriptFile.name))
condorSubmit.write("Universe            =  vanilla\n")
condorSubmit.write("Requirements        =  OpSys == \"LINUX\" && Arch ==\"x86_64\"\n")
condorSubmit.write("Request_Memory      =  2 Gb\n")
condorSubmit.write("Should_Transfer_Files = YES\n")
condorSubmit.write("WhenToTransferOutput = ON_EXIT\n")
condorSubmit.write("Output = %s/logs/$(Cluster)_$(Process).stdout\n"%(workingDir))
condorSubmit.write("Error = %s/logs/$(Cluster)_$(Process).stderr\n"%(workingDir))
condorSubmit.write("Log = %s/logs/$(Cluster)_$(Process).log\n"%(workingDir))
condorSubmit.write("Transfer_Input_Files = /uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/condor/%s/ratioStudyPlotter.py\n"%(taskDir))
condorSubmit.write("x509userproxy = $ENV(X509_USER_PROXY)\n\n")

for inputFilePFA2 in inputFilesPFA2:

    aNamePFA2 = inputFilePFA2.split("/")[-1].split(".root")[0]
    for inputFilePFA3 in inputFilesPFA3:
        
        if aNamePFA2 in inputFilePFA3:

            aNamePFA3 = inputFilePFA3.split("/")[-1].split(".root")[0]
            condorSubmit.write("transfer_output_remaps = \"%s_plots.root = %s/%s_plots.root\"\n" %(aNamePFA2, outputDir, aNamePFA2))
            condorSubmit.write("Arguments       = %s %s\n"%(inputFilePFA2, inputFilePFA3))
            condorSubmit.write("Queue\n\n")
            break

condorSubmit.close()

os.system("chmod +x %s"%(scriptFile.name))

if arg.noSubmit: quit()

os.system("condor_submit " + condorSubmit.name)
