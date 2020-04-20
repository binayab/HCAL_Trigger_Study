#!/usr/bin/env python

import os, sys, argparse, subprocess, shutil, random
from time import strftime

# Should be initialized by system time...
random.seed()

# With either a local EOS directory or dataset from DAS, get the list of files
def files4Dataset(dataset, onEOS):

    # If my name is in the path then we are on EOS
    if onEOS: proc = subprocess.Popen(['xrdfs', 'root://cmseos.fnal.gov', 'ls', dataset], stdout=subprocess.PIPE) 

    # Construct dasgoclient call and make it, reading back the standard out to get the list of files
    else:     proc = subprocess.Popen(['dasgoclient', '--query=file dataset=%s'%(dataset)], stdout=subprocess.PIPE)

    files = proc.stdout.readlines();  files = [file.rstrip() for file in files]

    # Prep the files for insertion into cmsRun config by adding the global redirector
    returnFiles = []
    for file in files:
        if onEOS: returnFiles.append(file.replace("/store/", "root://cmsxrootd.fnal.gov///store/"))
        else:     returnFiles.append(file.replace("/store/", "root://cms-xrd-global.cern.ch///store/"))

    return returnFiles 

# Write .sh script to be run by Condor
def generate_job_steerer(workingDir, step2, outputDir, CMSSW_VERSION):

    scriptFile = open("%s/runJob.sh"%(workingDir), "w")
    scriptFile.write("#!/bin/bash\n\n")
    scriptFile.write("SEED=$1\n")
    scriptFile.write("INPUTFILE=$2\n\n")
    scriptFile.write("export SCRAM_ARCH=slc7_amd64_gcc700\n\n")
    scriptFile.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n") 
    scriptFile.write("eval `scramv1 project CMSSW %s`\n\n"%(CMSSW_VERSION))
    scriptFile.write("tar -xf %s.tar.gz\n"%(CMSSW_VERSION))
    scriptFile.write("rm %s.tar.gz\n"%(CMSSW_VERSION))
    scriptFile.write("mv %s %s/src\n"%(step2,CMSSW_VERSION))
    scriptFile.write("cd %s/src\n"%(CMSSW_VERSION))
    scriptFile.write("scramv1 b ProjectRename\n")
    scriptFile.write("eval `scramv1 runtime -sh`\n\n")
    scriptFile.write("cmsRun %s ${SEED} ${INPUTFILE}\n\n"%(step2))
    scriptFile.write("xrdcp -f step2.root %s/${SEED}.root 2>&1\n"%(outputDir))
    scriptFile.write("cd ${_CONDOR_SCRATCH_DIR}\n")
    scriptFile.write("rm -r %s\n"%(CMSSW_VERSION))
    scriptFile.close()

# Write Condor submit file 
def generate_condor_submit(workingDir, step2, inputFiles, CMSSW_VERSION):

    condorSubmit = open("%s/condorSubmit.jdl"%(workingDir), "w")
    condorSubmit.write("Executable           =  %s/runJob.sh\n"%(workingDir))
    condorSubmit.write("Universe             =  vanilla\n")
    condorSubmit.write("Requirements         =  OpSys == \"LINUX\" && Arch ==\"x86_64\"\n")
    condorSubmit.write("Request_Memory       =  2 Gb\n")
    condorSubmit.write("Output               =  %s/logs/$(Cluster)_$(Process).stdout\n"%(workingDir))
    condorSubmit.write("Error                =  %s/logs/$(Cluster)_$(Process).stderr\n"%(workingDir))
    condorSubmit.write("Log                  =  %s/logs/$(Cluster)_$(Process).log\n"%(workingDir))
    condorSubmit.write("x509userproxy        =  $ENV(X509_USER_PROXY)\n")
    condorSubmit.write("Transfer_Input_Files =  %s/%s, %s/%s.tar.gz\n\n"%(workingDir, step2, workingDir, CMSSW_VERSION))

    for inputFile in inputFiles:

        iStub = inputFile.split("/")[-1]

        seed = random.randint(0, 2147483647)
        seedStr = "%s"%(seed); seedStr = seedStr.rjust(10, "0")

        condorSubmit.write("Arguments       = %s %s\n"%(seedStr, inputFile))
        condorSubmit.write("Queue\n\n")

    condorSubmit.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--noSubmit", dest="noSubmit", help="do not submit to cluster", default=False, action="store_true")
    parser.add_argument("--dataset" , dest="dataset" , help="Unique path to dataset"  , type=str , default="NULL")
    parser.add_argument("--step2"   , dest="step2"   , help="Name of script for step2", type=str , default="NULL")
    parser.add_argument("--tag"     , dest="tag"     , help="Unique tag"              , type=str , default="NULL")
    parser.add_argument("--process" , dest="process" , help="Physics process"         , type=str , default="NULL")
    args = parser.parse_args()

    tag      = args.tag
    step2    = args.step2
    dataset  = args.dataset
    noSubmit = args.noSubmit
    process  = args.process

    if tag == "NULL" or dataset == "NULL": quit()
   
    # Get environment for CMSSW
    CMSSW_BASE = os.getenv("CMSSW_BASE")
    CMSSW_VERSION = os.getenv("CMSSW_VERSION")
    HOME = os.getenv("HOME")
    USER = os.getenv("USER")

    taskDir = strftime("%Y%m%d_%H%M%S")
    hcalDir = "%s/nobackup/HCAL_Trigger_Study"%(HOME)

    onEOS = False
    if USER in dataset: onEOS = True
    
    inputFiles = files4Dataset(dataset, onEOS)
    
    outputDir = "root://cmseos.fnal.gov///store/user/%s/HCAL_Trigger_Study/production/%s/RAW/%s"%(USER, process, tag)
    workingDir = "%s/condor/%s_%s_%s"%(hcalDir, physProcess, tag, taskDir)
    
    # After defining the directory to work the job in and output to, make them
    subprocess.call(["eos", "root://cmseos.fnal.gov", "mkdir", "-p", outputDir[23:]])
    os.makedirs(workingDir)
    
    # Send the cmsRun config to the working dir
    try: shutil.copy2("%s/scripts/production/%s"%(hcalDir,step2), workingDir)
    except:
        print "Unable to copy cmsRun config \"%s\""%(step2)
        print "Exiting..."
        quit() 
    
    if outputDir.split("/")[-1] == "":  outputDir  = outputDir[:-1]
    if workingDir.split("/")[-1] == "": workingDir = workingDir[:-1]

    # Create directories to save logs
    os.makedirs("%s/logs"%(workingDir))

    # Make the .sh to run the show
    generate_job_steerer(workingDir, step2, outputDir, CMSSW_VERSION)

    # Make the jdl to hold condor's hand
    generate_condor_submit(workingDir, step2, inputFiles, CMSSW_VERSION)

    subprocess.call(["chmod", "+x", "%s/runJob.sh"%(workingDir)])

    subprocess.call(["tar", "--exclude-caches-all", "--exclude-vcs", "-zcf", "%s/%s.tar.gz"%(workingDir,CMSSW_VERSION), "-C", "%s/.."%(CMSSW_BASE), CMSSW_VERSION, "--exclude=tmp", "--exclude=src"])
    
    if args.noSubmit: quit()
    
    os.system("condor_submit %s/condorSubmit.jdl"%(workingDir))
