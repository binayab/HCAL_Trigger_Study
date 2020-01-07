#!/usr/bin/env python

import os, sys, argparse, subprocess, shutil
from time import strftime

# With either a local EOS directory or dataset from DAS, get the list of files
def files4Dataset(dataset):

    onEOS = os.getenv("USER") in dataset

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
def generate_job_steerer(workingDir, algo, outputDir, CMSSW_VERSION):

    scriptFile = open("%s/runJob.sh"%(workingDir), "w")
    scriptFile.write("#!/bin/bash\n\n")
    scriptFile.write("INPUTFILE=$1\n")
    scriptFile.write("JOB=$2\n\n")
    scriptFile.write("export SCRAM_ARCH=slc7_amd64_gcc700\n\n")
    scriptFile.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n") 
    scriptFile.write("eval `scramv1 project CMSSW %s`\n\n"%(CMSSW_VERSION))
    scriptFile.write("tar -xf %s.tar.gz\n"%(CMSSW_VERSION))
    scriptFile.write("rm %s.tar.gz\n"%(CMSSW_VERSION))
    scriptFile.write("mv algo_weights.py analyze_HcalTrig.py %s/src\n\n"%(CMSSW_VERSION))
    scriptFile.write("cd %s/src\n"%(CMSSW_VERSION))
    scriptFile.write("scramv1 b ProjectRename\n")
    scriptFile.write("eval `scramv1 runtime -sh`\n\n")
    scriptFile.write("cmsRun analyze_HcalTrig.py %s ${INPUTFILE} ${JOB}\n\n"%(algo))
    scriptFile.write("xrdcp -f hcalNtuple_${JOB}.root %s 2>&1\n"%(outputDir))
    scriptFile.write("cd ${_CONDOR_SCRATCH_DIR}\n")
    scriptFile.write("rm -r %s\n"%(CMSSW_VERSION))
    scriptFile.close()

# Write Condor submit file 
def generate_condor_submit(workingDir, inputFiles, CMSSW_VERSION):

    condorSubmit = open("%s/condorSubmit.jdl"%(workingDir), "w")
    condorSubmit.write("Executable           =  %s/runJob.sh\n"%(workingDir))
    condorSubmit.write("Universe             =  vanilla\n")
    condorSubmit.write("Requirements         =  OpSys == \"LINUX\" && Arch ==\"x86_64\"\n")
    condorSubmit.write("Request_Memory       =  5 Gb\n")
    condorSubmit.write("Output               =  %s/logs/$(Cluster)_$(Process).stdout\n"%(workingDir))
    condorSubmit.write("Error                =  %s/logs/$(Cluster)_$(Process).stderr\n"%(workingDir))
    condorSubmit.write("Log                  =  %s/logs/$(Cluster)_$(Process).log\n"%(workingDir))
    condorSubmit.write("x509userproxy        =  $ENV(X509_USER_PROXY)\n")
    condorSubmit.write("Transfer_Input_Files =  %s/analyze_HcalTrig.py, %s/algo_weights.py, %s/%s.tar.gz\n\n"%(workingDir, workingDir, workingDir, CMSSW_VERSION))

    iJob = 0
    for inputFile in inputFiles:
        
        condorSubmit.write("Arguments       = %s %d\n"%(inputFile, iJob))
        condorSubmit.write("Queue\n\n")

        iJob += 1
    
    condorSubmit.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--noSubmit", dest="noSubmit", help="do not submit to cluster", default=False, action="store_true")
    parser.add_argument("--scheme"  , dest="scheme"  , help="Which PFA to use"        , type=str , required=True)
    parser.add_argument("--dataset" , dest="dataset" , help="Unique path to dataset"  , type=str , default="50PU")
    parser.add_argument("--tag"     , dest="tag"     , help="Unique tag"              , type=str , default="NULL")
    args = parser.parse_args()

    scheme   = args.scheme
    tag      = args.tag
    dataset  = args.dataset
    noSubmit = args.noSubmit
   
    taskDir = strftime("%Y%m%d_%H%M%S")
    hcalDir = "%s/nobackup/HCAL_Trigger_Study"%(os.getenv("HOME"))
    
    physProcess = "";  inputFiles = []
    if "/" not in dataset:
        physProcess = dataset
        inputFiles.append(dataset)
    else:
        inputFiles = files4Dataset(dataset)
        physProcess = dataset.split("/")[1].split("_")[0]
    
    outputDir = "root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/%s/%s/%s"%(physProcess, tag, scheme)
    workingDir = "%s/condor/%s_%s_%s_%s"%(hcalDir, physProcess, scheme, tag, taskDir)
    
    # After defining the directory to work the job in and output to, make them
    subprocess.call(["eos", "root://cmseos.fnal.gov", "mkdir", "-p", outputDir[23:]])
    os.makedirs(workingDir)
    
    # Send the cmsRun config to the working dir as well as the algo weights
    shutil.copy2("%s/scripts/analyze_HcalTrig.py"%(hcalDir), workingDir)
    shutil.copy2("%s/scripts/algo_weights.py"%(hcalDir), workingDir)
    
    if outputDir.split("/")[-1] == "":  outputDir  = outputDir[:-1]
    if workingDir.split("/")[-1] == "": workingDir = workingDir[:-1]

    # Create directories to save logs
    os.makedirs("%s/logs"%(workingDir))
    
    # Get CMSSW environment
    CMSSW_BASE = os.getenv("CMSSW_BASE");  CMSSW_VERSION = os.getenv("CMSSW_VERSION")

    # Make the .sh to run the show
    generate_job_steerer(workingDir, scheme, outputDir, CMSSW_VERSION)

    # Make the jdl to hold condor's hand
    generate_condor_submit(workingDir, inputFiles, CMSSW_VERSION)

    subprocess.call(["chmod", "+x", "%s/runJob.sh"%(workingDir)])

    # Right here we need to edit a src file in CMSSW and recompile to change the input LUT based on 1TS or 2TS scheme...
    # After that is done, tar up CMSSW and send to the working directory
    oneTS = "containmentCorrection1TS;"; twoTS = "pulseCorr_->correction(cell, 2, correctionPhaseNS, correctedCharge);"
    filePath = '%s/src/CalibCalorimetry/HcalTPGAlgos/src/HcaluLUTTPGCoder.cc'%(CMSSW_BASE)

    # Let's be smart and determine if sed has to do a replacement which requires a recompile.
    recompile = False; replaceStr = ""
    if "1" not in scheme:
        p = subprocess.Popen(["grep", oneTS, filePath], stdout=subprocess.PIPE)
        recompile = bool(p.stdout.readline())
        replaceStr = 's#%s#%s#g'%(oneTS,twoTS)
    else:
        p = subprocess.Popen(["grep", twoTS, filePath], stdout=subprocess.PIPE)
        recompile = bool(p.stdout.readline())
        replaceStr = 's#%s#%s#g'%(twoTS,oneTS)

    # Only change the file and recompile if necessary
    if recompile:
        subprocess.call(['sed', '-i', replaceStr, filePath])
        subprocess.call(['scram', 'b', '-f', '-j', '8'], cwd=CMSSW_BASE+"/src")

    subprocess.call(["tar", "--exclude-caches-all", "--exclude-vcs", "-zcf", "%s/%s.tar.gz"%(workingDir,CMSSW_VERSION), "-C", "%s/.."%(CMSSW_BASE), CMSSW_VERSION, "--exclude=tmp"])
    
    if args.noSubmit: quit()
    
    os.system("condor_submit %s/condorSubmit.jdl"%(workingDir))
