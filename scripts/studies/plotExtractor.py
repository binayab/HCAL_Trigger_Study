# First-step script directly running on HCAL ntuples files

# An example call could be:
# python studies/ratioStudyPlotter.py --inputSubPath subpath/to/scheme/ntuples

# The subpath is assumed to start inside HCAL_Trigger_Study/hcalNtuples path in the user's EOS area

import sys, os, ROOT, subprocess, argparse

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetFrameLineWidth(4)
ROOT.TH1.SetDefaultSumw2()
ROOT.TH2.SetDefaultSumw2()

# 1D histo of user variable for range of TP ET and ieta
def make1D_Var(histoMap, histo, ietaRange = []):

    h2 = histo.Clone()

    h = 0; ietaStr = ""
    if len(ietaRange) == 0:
        h = h2.ProjectionY("%s_proj"%(h2.GetTitle()), 1, h2.GetXaxis().GetNbins())
    elif len(ietaRange) == 1:
        hpos = h2.ProjectionY("%s_proj_pos_%d"%(h2.GetTitle(),ietaRange[0]), h2.GetXaxis().FindBin(ietaRange[0]),h2.GetXaxis().FindBin(ietaRange[0]))
        hneg = h2.ProjectionY("%s_proj_neg_%d"%(h2.GetTitle(),ietaRange[0]), h2.GetXaxis().FindBin(-ietaRange[0]),h2.GetXaxis().FindBin(-ietaRange[0]))
        h = hpos; h.Add(hneg)
        ietaStr = "ieta%d"%(ietaRange[0])
    elif len(ietaRange) == 2:
        hpos = h2.ProjectionY("%s_proj_pos_%dto%d"%(h2.GetTitle(),ietaRange[0],ietaRange[1]), h2.GetXaxis().FindBin(ietaRange[0]),h2.GetXaxis().FindBin(ietaRange[1]))
        hneg = h2.ProjectionY("%s_proj_neg_%dto%d"%(h2.GetTitle(),ietaRange[0],ietaRange[1]), h2.GetXaxis().FindBin(-ietaRange[1]),h2.GetXaxis().FindBin(-ietaRange[0]))
        h = hpos; h.Add(hneg)
        ietaStr = "ieta%dto%d"%(ietaRange[0],ietaRange[1])

    h.SetTitle("")

    variable = histo.GetName().split("_")[0]; variableName = ""
    if variable == "TPRH"   : variableName = "E_{T,TP} / E_{T,RH}"
    if variable == "r43"    : variableName = "TS4 / TS3"
    if variable == "r4Total": variableName = "TS4 / Total"

    h.GetXaxis().SetTitle(variableName)
    h.GetYaxis().SetTitle("A.U.")

    theName = "%s_%s"%(histo.GetName(),ietaStr)

    if theName in histoMap: histoMap[theName].Add(h)
    else: 
        h.SetDirectory(0)
        histoMap[theName] = h

def analysis(PFAXFileDir, outDir):

    onEOS = "store" in PFAXFileDir

    if not os.path.exists(outDir): os.makedirs(outDir)

    outFile = ROOT.TFile.Open(outDir + "/ratios.root", "RECREATE")

    # Whether on EOS or locally, get the list of files to run on 
    proc = 0;  allItems = []
    if onEOS: 
        proc = subprocess.Popen(["xrdfs", "root://cmseos.fnal.gov", "ls", PFAXFileDir], stdout=subprocess.PIPE)
        allItems = proc.stdout.readlines();  allItems = [item.rstrip() for item in allItems]
    else:
        allItems = os.listdir(PFAXFileDir)

    theHistoMap = {}

    # Add only honest root files to TChain
    for item in allItems:
        
        if ".root" not in item or "ratio" in item: continue
    
        theFile = "" 
        if onEOS: theFile = "root://cmseos.fnal.gov/"+item
        else:     theFile = item

        f = ROOT.TFile.Open(theFile, "READ")

        d = f.GetDirectory("compareReemulRecoSeverity9")

        # Loop over the keys in the file to get the histograms
        for hkey in d.GetListOfKeys():
            
            # We only want histos
            if "TH" not in hkey.GetClassName(): continue 

            name  = hkey.GetName()
            histo = hkey.ReadObj()

            histo.Sumw2()

            if name in theHistoMap: theHistoMap[name].Add(histo)
            else:
                histo.SetDirectory(0)
                theHistoMap[name] = histo

        f.Close()
        print "Done reading in %s!"%(theFile)

    print "Now making derived histograms!"
    derivedHistoMap = {}
    for name, histo in theHistoMap.iteritems():

        if "vs_ieta" in name:
            for ieta in xrange(1,29):
            
                make1D_Var(derivedHistoMap, histo, [ieta])   

            make1D_Var(derivedHistoMap, histo, [1,28])
        
        outFile.cd()
        histo.Write(name) 

    outFile.cd()
    for name, histo in derivedHistoMap.iteritems(): histo.Write(name)

    outFile.Close()
   
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--inputSubPath" , dest="inputSubPath" , help="Subpath to input files"     , type=str , required=True)
    parser.add_argument("--tag"          , dest="tag"          , help="Unique tag for separating"  , type=str , default="")
    args = parser.parse_args()

    HOME = os.getenv("HOME"); USER = os.getenv("USER")
    INPUTLOC = "/eos/uscms/store/user/%s/HCAL_Trigger_Study/hcalNtuples"%(USER)
    OUTPUTLOC = "%s/nobackup/HCAL_Trigger_Study/input/Ratios"%(HOME)

    # Let the output folder structure mirror the input folder structure
    fileStub = args.inputSubPath
    tag      = args.tag

    analysis(INPUTLOC + "/" + fileStub, OUTPUTLOC + "/" + fileStub + "/" + tag)
