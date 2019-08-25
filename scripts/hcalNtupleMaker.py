import os
import argparse
import multiprocessing

parser = argparse.ArgumentParser("usage: %prog [options]")
parser.add_argument("--outputDir" , dest="outputDir" , help="directory to output ROOT files", type=str, required=True)
parser.add_argument("--pfa"       , dest="pfa"       , help="Which PFA to use"              , type=int, required=True)
parser.add_argument("--run"       , dest="run"       , help="Which run, you better know"    , type=int, required=True)
arg = parser.parse_args()

def analysis(aFile):

    stub = aFile.split("/")[-1].split(".")[0]
    outFile = outputDir + "/hcalNtuple_" + stub + ".root"
    
    print "cmsRun /uscms_data/d3/jhiltb/HCAL_Trigger_Study/CMSSW_10_4_0_patch1/src/scripts/analyze_HcalTrig.py %d %d %s %s"%(arg.pfa, arg.run, aFile, outFile)
    os.system("cmsRun /uscms_data/d3/jhiltb/HCAL_Trigger_Study/CMSSW_10_4_0_patch1/src/scripts/analyze_HcalTrig.py %d %d %s %s > /dev/null 2>&1"%(arg.pfa, arg.run, aFile, outFile))

if __name__ == '__main__':

    inputFiles = []
    if arg.run == 0:
        inputFiles = ["file:///uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/CMSSW_10_4_0_patch1/src/input/TTbar-DIGI-RAW.root"]
    elif arg.run == 50:
        inputFiles = ["file:///uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/CMSSW_10_4_0_patch1/src/input/TTbar-DIGI-RAW-PU.root"]
    else:
        if not os.path.isfile("./input/%s_ZeroBias.txt"%(arg.run)):
            print "Could not find input file list!"
            quit()
        inputFiles = ["root://cmsxrootd.fnal.gov/" + line.rstrip("\n") for line in open("./input/%s_ZeroBias.txt"%(arg.run))]
    
    outputDir = str(arg.outputDir)
    if outputDir[-1] == "/": outputDir = outputDir[:-1]
    
    if not os.path.exists(outputDir): os.makedirs(outputDir)
    
    pool = multiprocessing.Pool(processes=15)
    results = pool.map(analysis, inputFiles)
