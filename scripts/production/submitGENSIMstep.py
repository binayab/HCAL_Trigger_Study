#!/usr/bin/env python

import os, sys, argparse, subprocess, shutil, random
from time import strftime

# Should seed with system time...
random.seed()

# Write .sh script to be run by Condor
def generate_job_steerer(workingDir, step1, outputDir, CMSSW_VERSION):

    scriptFile = open("%s/runJob.sh"%(workingDir), "w")
    scriptFile.write("#!/bin/bash\n\n")
    scriptFile.write("SEED=$1\n")
    scriptFile.write("EVENTS=$2\n")
    scriptFile.write("RUN=$3\n\n")
    scriptFile.write("export SCRAM_ARCH=slc7_amd64_gcc700\n\n")
    scriptFile.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n") 
    scriptFile.write("eval `scramv1 project CMSSW %s`\n\n"%(CMSSW_VERSION))
    scriptFile.write("tar -xf %s.tar.gz\n"%(CMSSW_VERSION))
    scriptFile.write("rm %s.tar.gz\n"%(CMSSW_VERSION))
    scriptFile.write("mv %s %s/src\n"%(step1,CMSSW_VERSION))
    scriptFile.write("cd %s/src\n"%(CMSSW_VERSION))
    scriptFile.write("scramv1 b ProjectRename\n")
    scriptFile.write("eval `scramv1 runtime -sh`\n\n")
    scriptFile.write("cmsRun %s ${SEED} ${EVENTS} ${RUN}\n\n"%(step1))
    scriptFile.write("xrdcp -f step1.root %s/${SEED}_${RUN}.root 2>&1\n"%(outputDir))
    scriptFile.write("cd ${_CONDOR_SCRATCH_DIR}\n")
    scriptFile.write("rm -r %s\n"%(CMSSW_VERSION))
    scriptFile.close()

# Write Condor submit file 
def generate_condor_submit(workingDir, step1, eventsPerJob, njobs, CMSSW_VERSION):

    condorSubmit = open("%s/condorSubmit.jdl"%(workingDir), "w")
    condorSubmit.write("Executable           =  %s/runJob.sh\n"%(workingDir))
    condorSubmit.write("Universe             =  vanilla\n")
    condorSubmit.write("Requirements         =  OpSys == \"LINUX\" && Arch ==\"x86_64\"\n")
    condorSubmit.write("Request_Memory       =  2 Gb\n")
    condorSubmit.write("Output               =  %s/logs/$(Cluster)_$(Process).stdout\n"%(workingDir))
    condorSubmit.write("Error                =  %s/logs/$(Cluster)_$(Process).stderr\n"%(workingDir))
    condorSubmit.write("Log                  =  %s/logs/$(Cluster)_$(Process).log\n"%(workingDir))
    condorSubmit.write("x509userproxy        =  $ENV(X509_USER_PROXY)\n")
    condorSubmit.write("Transfer_Input_Files =  %s/%s, %s/%s.tar.gz\n\n"%(workingDir, step1, workingDir, CMSSW_VERSION))

    for iJob in xrange(0, njobs):
        
        seed = random.randint(0, 2147483647)

        seedStr = "%s"%(seed); seedStr = seedStr.rjust(10, "0")

        condorSubmit.write("Arguments       = %s %d %d\n"%(seedStr, eventsPerJob, iJob+1))
        condorSubmit.write("Queue\n\n")

    condorSubmit.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--noSubmit"     , dest="noSubmit"     , help="do not submit to cluster", default=False, action="store_true")
    parser.add_argument("--tag"          , dest="tag"          , help="Unique tag"              , type=str , default="NULL")
    parser.add_argument("--step1"        , dest="step1"        , help="Script file for step1"   , type=str , default="NULL")
    parser.add_argument("--process"      , dest="process"      , help="Friendly process name"   , type=str , default="NULL")
    parser.add_argument("--njobs"        , dest="njobs"        , help="Number of jobs"          , type=int , default=-1)
    parser.add_argument("--eventsPerJob" , dest="eventsPerJob" , help="Script file for step1"   , type=int , default=-1)
    args = parser.parse_args()

    tag          = args.tag
    step1        = args.step1
    njobs        = args.njobs
    eventsPerJob = args.eventsPerJob
    process      = args.process
    noSubmit     = args.noSubmit

    if tag == "NULL" or step1 == "NULL": quit()
    if njobs == -1 or eventsPerJob == -1: quit()
   
    # Get CMSSW environment
    CMSSW_BASE = os.getenv("CMSSW_BASE")
    CMSSW_VERSION = os.getenv("CMSSW_VERSION")
    HOME = os.getenv("HOME")
    USER = os.getenv("USER")

    taskDir = strftime("%Y%m%d_%H%M%S")
    hcalDir = "%s/nobackup/HCAL_Trigger_Study"%(HOME)
    
    outputDir = "root://cmseos.fnal.gov///store/user/%s/HCAL_Trigger_Study/production/%s/GEN-SIM/%s"%(USER,process,tag)
    workingDir = "%s/condor/%s_%s_%s"%(hcalDir, tag, process, taskDir)
    
    # After defining the directory to work the job in and output to, make them
    subprocess.call(["eos", "root://cmseos.fnal.gov", "mkdir", "-p", outputDir[23:]])
    os.makedirs(workingDir)
    
    # Send the cmsRun config to the working dir
    try: shutil.copy2("%s/scripts/production/%s"%(hcalDir,step1), workingDir)
    except:
        print "Unable to copy cmsRun config \"%s\""%(step1)
        print "Exiting..."
        quit() 
    
    if outputDir.split("/")[-1] == "":  outputDir  = outputDir[:-1]
    if workingDir.split("/")[-1] == "": workingDir = workingDir[:-1]

    # Create directories to save logs
    os.makedirs("%s/logs"%(workingDir))

    # Make the .sh to run the show
    generate_job_steerer(workingDir, step1, outputDir, CMSSW_VERSION)

    # Make the jdl to hold condor's hand
    generate_condor_submit(workingDir, step1, eventsPerJob, njobs, CMSSW_VERSION)

    subprocess.call(["chmod", "+x", "%s/runJob.sh"%(workingDir)])

    subprocess.call(["tar", "--exclude-caches-all", "--exclude-vcs", "-zcf", "%s/%s.tar.gz"%(workingDir,CMSSW_VERSION), "-C", "%s/.."%(CMSSW_BASE), CMSSW_VERSION, "--exclude=tmp", "--exclude=src"])
    
    if args.noSubmit: quit()
    
    os.system("condor_submit %s/condorSubmit.jdl"%(workingDir))
