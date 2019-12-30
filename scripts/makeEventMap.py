#!/usr/bin/env python

# Takes a PU file and a NOPU file and finds what entry number in the NOPU file corresponds to the event record number in the PU file

import ROOT, argparse

parser = argparse.ArgumentParser()
parser.add_argument("--depth"   , dest="depth"   , help="Depth?", default=False, action="store_true")
args = parser.parse_args()

depthStr = "NoDepth"
if args.depth: depthStr = "Depth"

output = open("outputMap%s.txt"%(depthStr), "w")

nopu = "root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/WeightExtraction/TTbar/NoContain/%s/NOPU.root"%(depthStr)
oot  = "root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/WeightExtraction/TTbar/NoContain/%s/OOT.root"%(depthStr)

f_nopu = ROOT.TFile.Open(nopu, "r"); t_nopu = f_nopu.Get("compareReemulRecoSeverity9/events")
f_oot  = ROOT.TFile.Open(oot,  "r"); t_oot  = f_oot.Get("compareReemulRecoSeverity9/events")

t_oot.SetBranchStatus("*", 0);     t_nopu.SetBranchStatus("*", 0)
t_oot.SetBranchStatus("event", 1); t_nopu.SetBranchStatus("event", 1)

NEVENTS = t_nopu.GetEntriesFast()

count = 0
tempStr = ""
for iEvent in xrange(0, NEVENTS):

    t_oot.GetEntry(iEvent)
    iRecord = t_oot.event

    for jEvent in xrange(0, NEVENTS):

        t_nopu.GetEntry(jEvent)
        jRecord = t_nopu.event

        if iRecord == jRecord:
            count += 1
            tempStr += "%s : %s, "%(iRecord, jEvent)

            if count == 9: 
                output.write(tempStr + "\n")
                tempStr = ""
                count = 0
            
            break

output.close()
