#!/usr/bin/env python

# Takes a PU ntuple file and a NOPU ntuple file and finds what entry number
# in the NOPU file corresponds to the event record number in the PU file

# An example call to this script would be
# python extraction/makeEventMap.py --pu subpath/to/ootpu/hcalNtuple_0.root --nopu subpath/to/nopu/hcalNtuple_0.root

# Here the subpath is assumed to start inside of an HCAL_Trigger_Study folder in the user's area on EOS

import ROOT, argparse, os

parser = argparse.ArgumentParser()
parser.add_argument("--pu"  , dest="pu"  , help="Subfolder for PU file"  , required=True)
parser.add_argument("--nopu", dest="nopu", help="Subfolder for NOPU file", required=True)
args = parser.parse_args()

USER = os.getenv("USER")
INPUTLOC = "root://cmseos.fnal.gov///store/user/%s/HCAL_Trigger_Study"%(USER)

tag = args.pu.split("/")[-1].split(".root")[0]

output = open("eventMap_%s.py"%(tag), "w")

nopu = "%s/%s"%(INPUTLOC,args.nopu)
pu   = "%s/%s"%(INPUTLOC,args.pu)

tree = "compareReemulRecoSeverity9/events"

f_nopu = ROOT.TFile.Open(nopu, "r"); t_nopu = f_nopu.Get(tree)
f_pu   = ROOT.TFile.Open(pu,  "r");  t_pu   = f_pu.Get(tree)

t_pu.SetBranchStatus("*"    , 0); t_nopu.SetBranchStatus("*"    , 0)
t_pu.SetBranchStatus("event", 1); t_nopu.SetBranchStatus("event", 1)
puEntries = t_pu.GetEntriesFast(); nopuEntries = t_nopu.GetEntriesFast()

count = 0
tempStr = "    "
output.write("# Event matching for\n")
output.write("# %s\n"%(nopu))
output.write("# %s\n\n"%(pu))
output.write("PU2NOPUMAP = {\n")

for iEvent in xrange(0, puEntries):

    print "Processing event %d..."%(iEvent)
    t_pu.GetEntry(iEvent)
    iRecord = t_pu.event

    for jEvent in xrange(0, nopuEntries):

        t_nopu.GetEntry(jEvent)
        jRecord = t_nopu.event

        if iRecord == jRecord:
            count += 1
            
            if iEvent == puEntries-1: tempStr += "%s : %s "%(iRecord, jEvent)
            else: tempStr += "%s : %s, "%(iRecord, jEvent)

            if iEvent == puEntries-1 or count == 9: 
                output.write(tempStr + "\n")
                tempStr = "    "
                count = 0
            
            break

output.write("}")
output.close()
