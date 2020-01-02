#!/usr/bin/env python

# Takes a PU file and a NOPU file and finds what entry number in the NOPU file corresponds to the event record number in the PU file

import ROOT, argparse

parser = argparse.ArgumentParser()
parser.add_argument("--depth"   , dest="depth"   , help="Use depth sample"      , default=False, action="store_true")
parser.add_argument("--contain" , dest="contain" , help="With pulse containment", default=False, action="store_true")
parser.add_argument("--oot"     , dest="oot"     , help="Use OOT sample"        , default=False, action="store_true")

args = parser.parse_args()

# Default to use OOT + IT sample: called 50PU.root
puStr = "50PU"
nopuStr = "0PU"
if args.oot:
    puStr = "OOT"
    nopuStr = "NOPU"

containStr = "NoContain"
if args.contain: containStr = "Contain"

depthStr = "NoDepth"
if args.depth: depthStr = "Depth"

INPUTLOC = "root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/WeightExtraction"
FULLPATH = "%s/TTbar/%s/%s"%(INPUTLOC,containStr,depthStr)

output = open("eventMap_%s_%s_%s.py"%(containStr,depthStr,puStr), "w")

nopu = "%s/%s.root"%(FULLPATH,nopuStr)
pu   = "%s/%s.root"%(FULLPATH,puStr)

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
