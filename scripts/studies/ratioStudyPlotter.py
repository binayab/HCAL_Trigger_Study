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

# From the events TChain, do a TTree draw to make a 3D histo with RH or TP ET on z, a user-specified variable on the y and ieta on x
# Regardless if RH or TP ET on z, always impose TP ET > 0.5
def make3Dhisto(evtsTree, variable = "TP_energy/RH_energy", basis = "TP", pu = "(1==1)"):

    etBranch = ""; tpMinSelection = "TP_energy>0.5"
    if basis == "TP": etBranch = "TP_energy"
    else:             etBranch = "RH_energy"

    h3 = ROOT.TH3F("h3_%sET"%(basis), "h3_%sET"%(basis), 57, -28.5, 28.5, 720, 0., 20.0, 257, -0.25, 128.25)

    evtsTree.Draw("%s:%s:ieta>>h3_%sET"%(etBranch,variable,basis), "tp_soi!=255 && %s && RH_energy>0. && %s"%(tpMinSelection,pu))

    h3 = ROOT.gDirectory.Get("h3_%sET"%(basis))

    return h3

# 1D histo of user variable for range of TP ET and ieta
def make1D_Var(outfile, package, etRange = [], ietaRange = []):

    outfile.cd()

    histo = package[0]; basis = package[1]; tag = package[2]
    var = package[3]; title = package[4]

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
    h.GetXaxis().SetTitle(title)
    h.GetYaxis().SetTitle("A.U.")

    h.Write("%s_%s_%s%s"%(var,etStr,ietaStr,tag))

# Make a user variable vs ieta 2D plot
def make2D_Var_vs_Eta(outfile, package, etRange = []):

    outfile.cd()

    histo = package[0]; basis = package[1]; tag = package[2]
    var = package[3]; title = package[4]

    htemp = histo.Clone()

    h2 = 0
    if   len(etRange) == 0: htemp.GetZaxis().SetRange(1, htemp.GetZaxis().GetNbins())
    elif len(etRange) == 1: htemp.GetZaxis().SetRange(htemp.GetZaxis().FindBin(etRange[0]),htemp.GetZaxis().FindBin(etRange[0]))
    elif len(etRange) == 2: htemp.GetZaxis().SetRange(htemp.GetZaxis().FindBin(etRange[0])+1,htemp.GetZaxis().FindBin(etRange[1]))

    htemp.GetZaxis().SetBit(ROOT.TAxis.kAxisRange)
    h2 = htemp.Project3D("yx")

    h2.SetTitle("")
    h2.GetXaxis().SetTitle("i#eta")
    h2.GetYaxis().SetTitle(title)

    if   len(etRange) == 0: h2.Write("%s_vs_Eta%s"%(var,tag))
    elif len(etRange) == 1: h2.Write("%s_vs_Eta_%sET%0.1f%s"%(var,basis,etRange[0],tag))
    elif len(etRange) == 2: h2.Write("%s_vs_Eta_%sET%0.1fto%0.1f%s"%(var,basis,etRange[0],etRange[1],tag))


# 2D plot of user variable as a function of RH or TP ET with a selection on ieta
def make2D_Var_vs_ET(outfile, package, ietaRange = [1,28]):

    outfile.cd()

    histo = package[0]; basis = package[1]; tag = package[2]
    var = package[3]; title = package[4]

    htempp = histo.Clone(histo.GetName()+"_pos"); htempn = histo.Clone(histo.GetName()+"_neg")

    h2pos = 0; h2neg = 0; ietaStr = ""
    if len(ietaRange) == 1:
        htempp.GetXaxis().SetRange(htempp.GetXaxis().FindBin(ietaRange[0]),htempp.GetXaxis().FindBin(ietaRange[0]))
        htempn.GetXaxis().SetRange(htempn.GetXaxis().FindBin(-ietaRange[0]),-htempn.GetXaxis().FindBin(-ietaRange[0]))

        ietaStr = "_ieta%d"%(ietaRange[0])
    elif len(ietaRange) == 2:
        htempp.GetXaxis().SetRange(htempp.GetXaxis().FindBin(ietaRange[0]),htempp.GetXaxis().FindBin(ietaRange[1]))
        htempn.GetXaxis().SetRange(htempn.GetXaxis().FindBin(-ietaRange[1]),htempn.GetXaxis().FindBin(-ietaRange[0]))

        ietaStr = "_ieta%dto%d"%(ietaRange[0],ietaRange[1])

    htempp.GetXaxis().SetBit(ROOT.TAxis.kAxisRange); htempn.GetXaxis().SetBit(ROOT.TAxis.kAxisRange)

    h2pos = htempp.Project3D("yz"); h2neg = htempn.Project3D("yz")

    h2pos.Add(h2neg)

    h2pos.SetTitle("")
    h2pos.GetYaxis().SetTitle(title)
    h2pos.GetXaxis().SetTitle("E_{T,%s} [GeV]"%(basis))

    h2pos.Write("%s_%sET%s%s"%(var,basis,ietaStr,tag))

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
        
        if ".root" not in item or "ratio" in item: continue
    
        if onEOS: cPFAX.AddFile("root://cmseos.fnal.gov/"+item)
        else:     cPFAX.AddFile(item)

    rawHistoPackages = []
    histo3D_TP        = make3Dhisto(cPFAX, basis="TP");  histo3D_TP.SetDirectory(0);  rawHistoPackages.append([histo3D_TP, "TP", "", "TPRH", "E_{T,TP} / E_{T,RH}"])
    histo3D_RH        = make3Dhisto(cPFAX, basis="RH");  histo3D_RH.SetDirectory(0);  rawHistoPackages.append([histo3D_RH, "RH", "", "TPRH", "E_{T,TP} / E_{T,RH}"])

    histo3D_r43       = make3Dhisto(cPFAX,variable="ts4/ts3",basis="RH");                   histo3D_r43.SetDirectory(0);     rawHistoPackages.append([histo3D_r43, "RH", "", "r43", "TS4 / TS3"])
    histo3D_r4total   = make3Dhisto(cPFAX,variable="ts4/(ts3+ts4+ts5+ts6+ts7)",basis="RH"); histo3D_r4total.SetDirectory(0); rawHistoPackages.append([histo3D_r4total, "RH", "", "r4total", "TS4 / Total"])

    #histo3D_RH_low  = make3Dhisto(cPFAX,"RH","pu>=55&&pu<62");  histo3D_RH_low.SetDirectory(0);  rawHistoPackages.append([histo3D_RH_low, "RH", "_PU55to62"]); print "Done making histo3D_RH_low!"
    #histo3D_RH_mid  = make3Dhisto(cPFAX,"RH","pu>=62&&pu<69");  histo3D_RH_mid.SetDirectory(0);  rawHistoPackages.append([histo3D_RH_mid, "RH", "_PU62to69"]); print "Done making histo3D_RH_mid!"
    #histo3D_RH_high = make3Dhisto(cPFAX,"RH","pu>=69&&pu<=75"); histo3D_RH_high.SetDirectory(0); rawHistoPackages.append([histo3D_RH_high,"RH", "_PU69to75"]); print "Done making histo3D_RH_high!"

    for histoPackage in rawHistoPackages:
        
        for ieta in xrange(1,29):
        
            # If the basis is TP than the lower limit is already 0.5
            make1D_Var(outFile, histoPackage, [0.0,10], [ieta])   
            make1D_Var(outFile, histoPackage, [10, 1000], [ieta])

        make2D_Var_vs_ET(outFile, histoPackage)

        # If the basis is TP than the lower limit is already 0.5
        make2D_Var_vs_Eta(outFile, histoPackage, [0.0,10])
        make1D_Var(outFile, histoPackage, [0.0,10],[1,28])
        make1D_Var(outFile, histoPackage, [10, 1000],[1,28])

        make2D_Var_vs_Eta(outFile, histoPackage, [10, 1000])

    outFile.Close()
   
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--inputSubPath"  , dest="inputSubPath"   , help="Subpath to input files"  , type=str , required=True)
    args = parser.parse_args()

    HOME = os.getenv("HOME"); USER = os.getenv("USER")
    INPUTLOC = "/eos/uscms/store/user/%s/HCAL_Trigger_Study/hcalNtuples"%(USER)
    OUTPUTLOC = "%s/nobackup/HCAL_Trigger_Study/input/Ratios"%(HOME)

    # Let the output folder structure mirror the input folder structure
    fileStub = args.inputSubPath

    analysis(INPUTLOC + "/" + fileStub, OUTPUTLOC + "/" + fileStub)
