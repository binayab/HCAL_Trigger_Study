# This script runs on two HCAL ntuple files, assumed to be from the same GEN-SIM file(s) 
# and matches TPs between the files (same event, same iphi, same ieta) to the get the TP ET
# ratio. An example call to the script would be:
# python studies/closureStudyPlotter.py subpath/to/nopu/ntuples/ subpath/to/ootpu/ntuples 0.5
# The last argument is the minimum TP ET to accept for both TPs in a match when computing the ratio

import sys, os, ROOT, subprocess
from pu2nopuMap import PU2NOPUMAP 

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetLineWidth(4)
ROOT.gStyle.SetFrameLineWidth(4)
ROOT.TH1.SetDefaultSumw2()

# The main looping function that takes in a TChain for nopu and oot pu files, finds the
# matched TPs and fills a raw 2D histogram with the ratio.
def eventLoop(minTPET, nopuChain, ootChain, outfile):

    outfile.cd()
    h2 = ROOT.TH2F("tpET_ratio", ";i#eta;TP E_{T} Ratio", 57, -28.5, 28.5, 720, -0.014, 19.986)

    ootChain.SetBranchStatus("*", 0);     nopuChain.SetBranchStatus("*", 0)
    ootChain.SetBranchStatus("et", 1);    nopuChain.SetBranchStatus("et", 1)
    ootChain.SetBranchStatus("ieta", 1);  nopuChain.SetBranchStatus("ieta", 1)
    ootChain.SetBranchStatus("iphi", 1);  nopuChain.SetBranchStatus("iphi", 1)
    ootChain.SetBranchStatus("event", 1); nopuChain.SetBranchStatus("event", 1)
    ootChain.SetBranchStatus("depth", 1); nopuChain.SetBranchStatus("depth", 1)

    NEVENTS = ootChain.GetEntries()

    for iEvent in xrange(0, NEVENTS):

        ootChain.GetEntry(iEvent)
        nopuChain.GetEntry(PU2NOPUMAP[ootChain.event])
        #nopuChain.GetEntry(iEvent)

        if ootChain.event != nopuChain.event:
            print "EVENT MISMATCH, SKIPPING THIS EVENT ENTRY!"
            continue

        # Due to ordering of TPs in depth, ieta, iphi we can be smart about breaking out of the inner loop as soon as possible
        # Use the hotStart to move the starting line for the inner loop as we go along
        hotStart = 0
        for iTP in xrange(0, len(ootChain.ieta)):
            ieta = ootChain.ieta[iTP]
            iphi = ootChain.iphi[iTP]
            idepth = ootChain.depth[iTP]
            iET = ootChain.et[iTP]

            # Due to ordering once we hit HF ieta stop looping!
            if abs(ieta) > 28: break
            if iET <= minTPET: continue 

            for jTP in xrange(hotStart, len(nopuChain.ieta)):
                jeta = nopuChain.ieta[jTP]
                jphi = nopuChain.iphi[jTP]
                jdepth = nopuChain.depth[jTP]
                jET = nopuChain.et[jTP]
        
                # Due to ordering once we hit HF ieta stop looping! 
                if abs(jeta) > 28: break
                if jET <= minTPET: continue

                # If we passed in depth then there was no match; break the inner loop and go back to outer loop
                elif jdepth > idepth:
                    hotStart = jTP
                    break

                # For same depth, if we pass in phi there was and will not be a match 
                elif idepth == jdepth:

                    # If we pass in ieta then there is no match; break the inner loop and go back to outer loop
                    if jeta * ieta < 0 or (jeta < 0 and ieta < 0 and jeta < ieta) or (jeta > 0 and ieta > 0 and jeta > ieta):
                        hotStart = jTP
                        break

                    # If eta also match then check at phi level
                    elif jeta == ieta:

                        # If we pass in phi then there was no match; break the inner loop and go back to outer loop
                        if jphi > iphi:
                            hotStart = jTP
                            break

                        # Here we match in depth, ieta and phi
                        elif jphi == iphi:

                            # We are here so we must have found a match!
                            #print "category   PU | event %s | ieta %d | iphi %d | depth %d | TP ET %f]"%(ootChain.event, ieta, iphi, idepth, ootChain.et[iTP])
                            #print "category NOPU | event %s | ieta %d | iphi %d | depth %d | TP ET %f]\n"%(nopuChain.event, jeta, jphi, jdepth, nopuChain.et[jTP])
                            
                            if jET > 0:
                                etFrac = iET / jET
                                h2.Fill(ieta, etFrac)
                                hotStart = jTP
                                break

        print "Processed event %d => %d..."%(iEvent,NEVENTS)

    h2.Write()
    outfile.Close()

# The analysis method does the handling of the input file path and gets the list of files.
# From there the TChains are created and passed to the eventLoop
def analysis(NOPUFileDir, OOTFileDir, minTPET):

    HCALNTUPLES = "/eos/uscms/store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/"

    onEOS = "store" in NOPUFileDir

    nopuStub = ""; puStub = ""
    for sub in NOPUFileDir.split("/"):
        if "PFA" in sub:
            nopuStub = sub
            break
    for sub in OOTFileDir.split("/"):
        if "PFA" in sub:
            puStub = sub
            break

    outDir = "%s/nobackup/HCAL_Trigger_Study/input/Closure/%s_NOPU_%s_PU/TPETgt%0.1f"%(os.getenv("HOME"), nopuStub, puStub, minTPET)
    if not os.path.exists(outDir): os.makedirs(outDir)

    outFilePath = outDir + "/closure.root"
    outFile = ROOT.TFile.Open(outFilePath, "RECREATE")

    cNOPU = ROOT.TChain("compareReemulRecoSeverity9/events", "NOPU")
    cOOT  = ROOT.TChain("compareReemulRecoSeverity9/events", "OOT")

    # Whether on EOS or locally, get the list of files to run on 
    proc = subprocess.Popen(["xrdfs", "root://cmseos.fnal.gov", "ls", HCALNTUPLES + NOPUFileDir], stdout=subprocess.PIPE)
    allItems = proc.stdout.readlines();  allItems = [item.rstrip() for item in allItems]

    # Add only honest root files to TChain
    for item in allItems:
        
        if ".root" not in item: continue
        if "ratio" in item:     continue
    
        cNOPU.AddFile("root://cmseos.fnal.gov/"+item)

    # Whether on EOS or locally, get the list of files to run on 
    proc = subprocess.Popen(["xrdfs", "root://cmseos.fnal.gov", "ls", HCALNTUPLES + OOTFileDir], stdout=subprocess.PIPE)
    allItems = proc.stdout.readlines();  allItems = [item.rstrip() for item in allItems]

    # Add only honest root files to TChain
    for item in allItems:
        
        if ".root" not in item: continue
        if "ratio" in item:     continue
    
        cOOT.AddFile("root://cmseos.fnal.gov/"+item)

    eventLoop(minTPET, cNOPU, cOOT, outFile)    

    print "Done writing to ==> \"%s\""%(outFilePath)
    outFile.Close()
   
if __name__ == '__main__':

    NOPUFileDir = str(sys.argv[1])
    OOTFileDir  = str(sys.argv[2])

    minTPET = -1.
    try: minTPET = float(sys.argv[3])
    except: minTPET = 0.0

    analysis(NOPUFileDir, OOTFileDir, minTPET)
