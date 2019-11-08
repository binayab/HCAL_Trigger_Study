#!/usr/bin/env python

import sys, os, argparse, shutil, time

date_and_time=time.strftime("%Y%m%d_%H%M%S")

usage = "usage: %prog [options]"
parser = argparse.ArgumentParser(usage)
parser.add_argument("--tag"     , dest="tag"     , help="Unique tag for output"   , type=str     , required=True)
parser.add_argument("--algo"    , dest="algo"    , help="Which reco scheme"       , type=str     , required=True)
parser.add_argument("--noSubmit", dest="noSubmit", help="do not submit to cluster", default=False, action="store_true")
parser.add_argument("--nJobs"   , dest="nJobs"   , help="number of jobs"          , type=int     , default=30)

arg = parser.parse_args()

NEVENTS = 9000
nJobs = arg.nJobs
eventsPerJob = 9000 / arg.nJobs

exeStub = "python weightExtraction.py"
exeStub += " --algo %s"%(arg.algo)

taskDir = arg.algo + "_TP_" + arg.tag + "_" + date_and_time
outputDir  = "/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/plots/Weights/%s/TP/%s/root"%(arg.algo,arg.tag)
workingDir = "/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/condor/%s"%(taskDir)

if not os.path.exists(outputDir):  os.makedirs(outputDir)
if not os.path.exists(workingDir): os.makedirs(workingDir)

shutil.copy2("/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/scripts/weightExtraction.py", "/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/condor/%s"%(taskDir))
shutil.copy2("/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/scripts/pu2nopuMap.py", "/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/condor/%s"%(taskDir))

if outputDir.split("/")[-1] == "":  outputDir  = outputDir[:-1]
if workingDir.split("/")[-1] == "": workingDir = workingDir[:-1]

# Create directories to save log, submit, and mac files if they don't already exist
logDir="%s/logs"%(workingDir)
os.mkdir(logDir) # make the log directory

# Write .sh script to be run by Condor
scriptFile = open("%s/runJob.sh"%(workingDir), "w")
scriptFile.write("#!/bin/bash\n\n")
scriptFile.write("STARTEVENT=$1\n")
scriptFile.write("NUMEVENTS=$2\n\n")
scriptFile.write("export SCRAM_ARCH=sl6_amd64_gcc700\n")
scriptFile.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n") 
scriptFile.write("eval `scramv1 project CMSSW CMSSW_10_4_0_patch1`\n")
scriptFile.write("cd CMSSW_10_4_0_patch1/src\n")
scriptFile.write("eval `scramv1 runtime -sh`\n")
scriptFile.write("cd ./../..\n")
scriptFile.write("%s --evtRange ${STARTEVENT} ${NUMEVENTS}\n"%(exeStub))
scriptFile.write("ls -l\n")
scriptFile.write("cd ${_CONDOR_SCRATCH_DIR}\n")
scriptFile.write("rm -r weightExtraction.py CMSSW_10_4_0_patch1\n")
scriptFile.close()

# Write Condor submit file 
condorSubmit = open("%s/condorSubmit.jdl"%(workingDir), "w")
condorSubmit.write("Executable          =  %s\n"%(scriptFile.name))
condorSubmit.write("Universe            =  vanilla\n")
condorSubmit.write("Requirements        =  OpSys == \"LINUX\" && Arch ==\"x86_64\"\n")
condorSubmit.write("Request_Memory      =  2.5 Gb\n")
condorSubmit.write("Should_Transfer_Files = YES\n")
condorSubmit.write("WhenToTransferOutput = ON_EXIT\n")
condorSubmit.write("Output = %s/logs/$(Cluster)_$(Process).stdout\n"%(workingDir))
condorSubmit.write("Error = %s/logs/$(Cluster)_$(Process).stderr\n"%(workingDir))
condorSubmit.write("Log = %s/logs/$(Cluster)_$(Process).log\n"%(workingDir))
condorSubmit.write("Transfer_Input_Files = /uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/condor/%s/weightExtraction.py, /uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/condor/%s/pu2nopuMap.py\n"%(taskDir,taskDir))
condorSubmit.write("x509userproxy = $ENV(X509_USER_PROXY)\n\n")

for iJob in xrange(0,nJobs):

    condorSubmit.write("transfer_output_remaps = \"histoCache_%d.root = %s/histoCache_%d.root\"\n" %(iJob*eventsPerJob, outputDir, iJob*eventsPerJob))
    condorSubmit.write("Arguments       = %d %d\n"%(iJob*eventsPerJob, eventsPerJob))
    condorSubmit.write("Queue\n\n")

condorSubmit.close()

os.system("chmod +x %s"%(scriptFile.name))

if arg.noSubmit: quit()

os.system("condor_submit " + condorSubmit.name)
