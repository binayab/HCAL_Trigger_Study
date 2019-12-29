#!/usr/bin/env python

# Takes a PU file and a NOPU file and finds what entry number in the NOPU file corresponds to the event record number in the PU file

import ROOT

output = open("outputMap.txt", "w")

nopu = "root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/WeightExtraction/TTbar/NoContain/Depth/NOPU.root"
oot  = "root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/WeightExtraction/TTbar/NoContain/Depth/OOT.root"

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
            count++
            tempStr += "%s : %s, "%(iRecord, jEvent)

            if count == 9: 
                output.write(tempStr + "\n")
                tempStr = ""
                count = 0
            
            break
