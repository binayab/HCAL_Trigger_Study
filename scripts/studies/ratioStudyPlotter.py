# First script directly running on HCAL ntuples files

# An example call could be:
# python studies/ratioStudyPlotter.py --inputSubPath subpath/to/scheme/ntuples

# The subpath is assumed to start inside HCAL_Trigger_Study/hcalNtuples in the user's EOS area

import sys, os, ROOT, subprocess, argparse

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetFrameLineWidth(4)
ROOT.TH1.SetDefaultSumw2()
ROOT.TH2.SetDefaultSumw2()

# From the events do a draw to make a 3D histo with RH or TP ET on z, TP/RH ratio on y and ieta on x
# Regardless if RH or TP ET on z, always impose TP ET > 0.5
def ratioTPVsRH_Eta_ET(evtsTree, basis = "TP", bx = "(1==1)"):

    etBranch = ""; tpMinSelection = "TP_energy>0.5"
    if basis == "TP": etBranch = "TP_energy"
    else:             etBranch = "RH_energy"

    h3 = ROOT.TH3F("h3_%sET"%(basis), "h3_%sET"%(basis), 57, -28.5, 28.5, 720, 0., 20.0, 257, -0.25, 128.25)

    evtsTree.Draw("%s:TP_energy/RH_energy:ieta>>h3_%sET"%(etBranch,basis), "tp_soi!=255 && %s && RH_energy>0. && %s"%(tpMinSelection,bx))

    h3 = ROOT.gDirectory.Get("h3_%sET"%(basis))

    return h3

# Make a TP/RH vs ieta 2D plot
def ratioTPVsRH_Eta(outfile, histo, basis, etRange = []):

    outfile.cd()

    htemp = histo.Clone()

    h2 = 0
    if   len(etRange) == 0: htemp.GetZaxis().SetRange(1, htemp.GetZaxis().GetNbins())
    elif len(etRange) == 1: htemp.GetZaxis().SetRange(htemp.GetZaxis().FindBin(etRange[0]),htemp.GetZaxis().FindBin(etRange[0]))
    elif len(etRange) == 2: htemp.GetZaxis().SetRange(htemp.GetZaxis().FindBin(etRange[0])+1,htemp.GetZaxis().FindBin(etRange[1]))

    htemp.GetZaxis().SetBit(ROOT.TAxis.kAxisRange)
    h2 = htemp.Project3D("yx")

    h2.SetTitle("")
    h2.GetXaxis().SetTitle("i#eta")
    h2.GetYaxis().SetTitle("E_{T,TP} / E_{T,RH}")

    if   len(etRange) == 0: h2.Write("TPRH_vs_Eta")
    elif len(etRange) == 1: h2.Write("TPRH_vs_Eta_%sET%0.1f"%(basis,etRange[0]))
    elif len(etRange) == 2: h2.Write("TPRH_vs_Eta_%sET%0.1fto%0.1f"%(basis,etRange[0],etRange[1]))

# 1D histo of TP/RH values for range of TP ET and ieta
def ratioTPVsRH(outfile, histo, basis, etRange = [], ietaRange = []):

    outfile.cd()

    htemp = histo.Clone()

    h2 = 0; etStr = ""
    if len(etRange) == 0:
        htemp.GetZaxis().SetRange(1, htemp.GetZaxis().GetNbins())
    elif len(etRange) == 1:
        htemp.GetZaxis().SetRange(htemp.GetZaxis().FindBin(etRange[0]),htemp.GetZaxis().FindBin(etRange[0]))
        etStr = "%sET%0.1f"%(basis,etRange[0])
    elif len(etRange) == 2:
        htemp.GetZaxis().SetRange(htemp.GetZaxis().FindBin(etRange[0])+1,htemp.GetZaxis().FindBin(etRange[1]))
        etStr = "%sET%0.1fto%0.1f"%(basis,etRange[0],etRange[1])

    htemp.GetZaxis().SetBit(ROOT.TAxis.kAxisRange)
    h2 = htemp.Project3D("yx")

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
    h.GetXaxis().SetTitle("E_{T,TP} / E_{T,RH}")
    h.GetYaxis().SetTitle("A.U.")

    h.Write("TPRH_%s_%s"%(etStr,ietaStr))

# 2D plot of TP/RH as a function of RH or TP ET with a selection on ieta
def ratioTPVsRH_ET(outfile, histo, basis, ietaRange = [1,28]):

    outfile.cd()

    htempp = histo.Clone(histo.GetName()+"_pos")
    htempn = histo.Clone(histo.GetName()+"_neg")

    h2pos = 0; h2neg = 0; ietaStr = ""
    if len(ietaRange) == 1:
        htempp.GetXaxis().SetRange(htempp.GetXaxis().FindBin(ietaRange[0]),htempp.GetXaxis().FindBin(ietaRange[0]))
        htempn.GetXaxis().SetRange(htempn.GetXaxis().FindBin(-ietaRange[0]),-htempn.GetXaxis().FindBin(-ietaRange[0]))

        ietaStr = "_ieta%d"%(ietaRange[0])
    elif len(ietaRange) == 2:
        htempp.GetXaxis().SetRange(htempp.GetXaxis().FindBin(ietaRange[0]),htempp.GetXaxis().FindBin(ietaRange[1]))
        htempn.GetXaxis().SetRange(htempn.GetXaxis().FindBin(-ietaRange[1]),htempn.GetXaxis().FindBin(-ietaRange[0]))

        ietaStr = "_ieta%dto%d"%(ietaRange[0],ietaRange[1])

    htempp.GetXaxis().SetBit(ROOT.TAxis.kAxisRange)
    htempn.GetXaxis().SetBit(ROOT.TAxis.kAxisRange)

    h2pos = htempp.Project3D("yz")
    h2neg = htempn.Project3D("yz")

    h2pos.Add(h2neg)

    h2pos.SetTitle("")
    h2pos.GetYaxis().SetTitle("E_{T,TP} / E_{T,RH}")
    h2pos.GetXaxis().SetTitle("E_{T,%s} [GeV]"%(basis))

    h2pos.Write("TPRH_%sET%s"%(basis,ietaStr))

def analysis(PFAXFileDir, outDir):

    onEOS = "store" in PFAXFileDir

    if not os.path.exists(outDir): os.makedirs(outDir)

    outFile = ROOT.TFile.Open(outDir + "/ratios.root", "RECREATE")

    cPFAX = ROOT.TChain("compareReemulRecoSeverity9/matches")

    # Whether on EOS or locally, get the list of files to run on 
    proc = 0;  allItems = []
    if onEOS: 
        proc = subprocess.Popen(["xrdfs", "root://cmseos.fnal.gov", "ls", PFAXFileDir], stdout=subprocess.PIPE)
        allItems = proc.stdout.readlines();  allItems = [item.rstrip() for item in allItems]
    else:
        allItems = os.listdir(PFAXFileDir)

    # Add only honest root files to TChain
    for item in allItems:
        
        if ".root" not in item: continue
        if "ratio" in item:     continue
    
        if onEOS: cPFAX.AddFile("root://cmseos.fnal.gov/"+item)
        else:     cPFAX.AddFile(item)

    TPETvRatiovEta_TP = ratioTPVsRH_Eta_ET(cPFAX,"TP"); TPETvRatiovEta_TP.SetDirectory(0)
    TPETvRatiovEta_RH = ratioTPVsRH_Eta_ET(cPFAX,"RH"); TPETvRatiovEta_RH.SetDirectory(0)

    # When providing ET ranges it always for PFA2 when in TP basis
    for ieta in xrange(1,29):
        ratioTPVsRH(outFile,TPETvRatiovEta_TP,"TP",[0.5,10],[ieta])
        ratioTPVsRH(outFile,TPETvRatiovEta_TP,"TP",[10, 1000],[ieta])

        ratioTPVsRH(outFile,TPETvRatiovEta_RH,"RH",[0.0,10],[ieta])
        ratioTPVsRH(outFile,TPETvRatiovEta_RH,"RH",[0.5,10],[ieta])
        ratioTPVsRH(outFile,TPETvRatiovEta_RH,"RH",[10, 1000],[ieta])

    ratioTPVsRH(outFile,TPETvRatiovEta_RH,"RH",[0.0,10],[1,28])
    ratioTPVsRH(outFile,TPETvRatiovEta_RH,"RH",[0.5,10],[1,28])
    ratioTPVsRH(outFile,TPETvRatiovEta_RH,"RH",[10, 1000],[1,28])

    ratioTPVsRH_Eta(outFile,TPETvRatiovEta_TP,"TP",[0.5,10])
    ratioTPVsRH_Eta(outFile,TPETvRatiovEta_TP,"TP",[10, 1000])
    ratioTPVsRH_Eta(outFile,TPETvRatiovEta_TP,"TP",[0.0,1000])

    ratioTPVsRH_Eta(outFile,TPETvRatiovEta_RH,"RH",[0.0,10])
    ratioTPVsRH_Eta(outFile,TPETvRatiovEta_RH,"RH",[0.5,10])
    ratioTPVsRH_Eta(outFile,TPETvRatiovEta_RH,"RH",[10, 1000])
    ratioTPVsRH_Eta(outFile,TPETvRatiovEta_RH,"RH",[0.0, 1000])

    ratioTPVsRH_ET(outFile,TPETvRatiovEta_TP,"TP")
    ratioTPVsRH_ET(outFile,TPETvRatiovEta_RH,"RH")

    outFile.Close()
   
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--inputSubPath"  , dest="inputSubPath"   , help="Subpath to input files"  , type=str , required=True)
    args = parser.parse_args()


    HOME = os.getenv("HOME")
    USER = os.getenv("USER")
    INPUTLOC = "/eos/uscms/store/user/%s/HCAL_Trigger_Study/hcalNtuples"%(USER)
    OUTPUTLOC = "%s/nobackup/HCAL_Trigger_Study/input/Ratios"%(HOME)

    # Let the output folder structure mirror the input folder structure
    PFAXFileStub = args.inputSubPath
    outputStub   = PFAXFileStub

    analysis(INPUTLOC + "/" + PFAXFileStub, OUTPUTLOC + "/" + outputStub)
