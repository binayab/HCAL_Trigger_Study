# First-step script directly running on HCAL ntuples files

# An example call could be:
# python studies/ratioStudyPlotter.py --inputSubPath subpath/to/scheme/ntuples

# The subpath is assumed to start inside HCAL_Trigger_Study/hcalNtuples path in the user's EOS area

import sys, os, ROOT, subprocess, argparse
from toolbox import *

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.TH1.SetDefaultSumw2()
ROOT.TH2.SetDefaultSumw2()
ROOT.TH3.SetDefaultSumw2()

def makeRHspectrumPlots(plotsDir, RH_vs_ieta_yespeak, RH_vs_ieta_nopeak):

    for subdet, ranges in {"HB" : [-16, -1, 1, 16], "HE" : [-28, -17, 17, 28]}.iteritems():
        RH_yespeak = make1Dhisto(RH_vs_ieta_yespeak, ["X", ranges[0], ranges[1], ranges[2], ranges[3]], ["ieta", "RHET", "Peak"], "_wPeak")
        RH_nopeak  = make1Dhisto(RH_vs_ieta_nopeak,  ["X", ranges[0], ranges[1], ranges[2], ranges[3]], ["ieta", "RHET", "Peak"], "_woPeak")

        c = ROOT.TCanvas("c_%s_%s"%(RH_yespeak.GetName(), subdet), "c_%s_%s"%(RH_yespeak.GetName(), subdet), 1600, 900); c.cd(); c.SetLogy()
        ROOT.gPad.SetGridy(); ROOT.gPad.SetGridx()
        ROOT.gPad.SetTopMargin(0.026)
        ROOT.gPad.SetBottomMargin(0.15)
        ROOT.gPad.SetLeftMargin(0.11)
        ROOT.gPad.SetRightMargin(0.03)

        setAxisDims(RH_nopeak, 0.059, 0.059, 0.059, 0.072, 0.072, 0.072, 0.95, 0.75, 1.0)
        setAxisRanges(RH_nopeak, xMin = -0.5, xMax = 20.0)
        setAxisLabels(RH_nopeak, lab = "", yLab = "A.U.")
        set1Doptions(RH_yespeak, lineColor = ROOT.kBlack, markerSize = 0, lineWidth = 3, markerColor = ROOT.kBlack)
        set1Doptions(RH_nopeak,  lineColor = ROOT.kRed,   markerSize = 0, lineWidth = 3, markerColor = ROOT.kRed)

        RH_nopeak.Draw("HIST")
        RH_yespeak.Draw("HIST SAME")
        
        c.SaveAs("%s/%s_%s.pdf"%(plotsDir, RH_yespeak.GetName(), subdet))

    tm = 0.05; bm = 0.20; lm = 0.09; rm = 0.12; split = 0.542857; ratio = (1.0 - split) / split
    xl = 0.095; yl = 0.095; zl = 0.095; xt = 0.15; yt = 0.15; zt = 0.15; xo = 0.50; yo = 0.27; zo = 0.8 
    c = ROOT.TCanvas("c_%s_%s"%(RH_vs_ieta_yespeak.GetName(), subdet), "c_%s_%s"%(RH_vs_ieta_yespeak.GetName(), subdet), 1600, 1200)
    c.Divide(1,2) 
    c.cd(2); ROOT.gPad.SetLogz()
    ROOT.gPad.SetPad(0, 0.0, 1, split)
    ROOT.gPad.SetTopMargin(0.0)
    ROOT.gPad.SetBottomMargin(bm)
    ROOT.gPad.SetLeftMargin(lm)
    ROOT.gPad.SetRightMargin(rm)

    setAxisDims(RH_vs_ieta_yespeak, xl*ratio, yl*ratio, zl*ratio, xt*ratio, yt*ratio, zt*ratio, xo/ratio, yo/ratio, zo/ratio)
    setAxisRebins(RH_vs_ieta_yespeak, yReb = 1)
    setAxisRanges(RH_vs_ieta_yespeak, yMin = -0.99, yMax = 11.0, zMin = 2e-1, zMax = 4e6)
    setAxisLabels(RH_vs_ieta_yespeak, lab = "", xLab = "i#eta", yLab = "")
    set2Doptions(RH_vs_ieta_yespeak)
    RH_vs_ieta_yespeak.Draw("COLZ")

    c.cd(1); ROOT.gPad.SetLogz()
    ROOT.gPad.SetPad(0, split, 1, 1)
    ROOT.gPad.SetTopMargin(tm)
    ROOT.gPad.SetBottomMargin(0.0)
    ROOT.gPad.SetLeftMargin(lm)
    ROOT.gPad.SetRightMargin(rm)

    setAxisDims(RH_vs_ieta_nopeak, xl, yl, zl, xt, yt, zt, xo, yo, zo)
    setAxisRanges(RH_vs_ieta_nopeak, yMin = -0.99, yMax = 11.0, zMin = 2e-1, zMax = 4e6)
    setAxisLabels(RH_vs_ieta_nopeak, lab = "", xLab = "", yLab = "E_{T,RH} [GeV]")
    set2Doptions(RH_vs_ieta_nopeak)
    RH_vs_ieta_nopeak.Draw("COLZ")

    c.SaveAs("%s/%s.pdf"%(plotsDir, RH_vs_ieta_yespeak.GetName()))

def makeTPRHcorrelationPlots(plotsDir, histo3D_TPRH, aieta):

    h_aieta = make2Dhisto(histo3D_TPRH, ["Z", aieta, aieta], ["RHET", "TPET", str(aieta)])

    tm = 0.02; bm = 0.14; lm = 0.12; rm = 0.13; ratio = 1.0
    xl = 0.055; yl = 0.055; zl = 0.055; xt = 0.065; yt = 0.065; zt = 0.065; xo = 0.95; yo = 0.85; zo = 0.8 
    c = ROOT.TCanvas("c_%s"%(h_aieta.GetName()), "c_%s"%(h_aieta.GetName()), 2000, 1600)
    c.cd(); ROOT.gPad.SetLogz()
    ROOT.gPad.SetPad(0, 0.0, 1, 1.0)
    ROOT.gPad.SetTopMargin(tm)
    ROOT.gPad.SetBottomMargin(bm)
    ROOT.gPad.SetLeftMargin(lm)
    ROOT.gPad.SetRightMargin(rm)

    setAxisDims(h_aieta, xl*ratio, yl*ratio, zl*ratio, xt*ratio, yt*ratio, zt*ratio, xo/ratio, yo/ratio, zo/ratio)
    setAxisRebins(h_aieta, xReb = 1, yReb = 1)
    setAxisRanges(h_aieta, xMin = 0., xMax = 10.5, yMin = 0., yMax = 10.5, zMin = 1, zMax = 2e6)
    setAxisLabels(h_aieta, lab = "")
    set2Doptions(h_aieta)

    tpScale = h_aieta.ProfileX("tp_%s_%d"%(h_aieta.GetName(),h_aieta.GetUniqueID()), 1, -1, "s"); ROOT.SetOwnership(tpScale, False); tpScale.Sumw2()
    set1Doptions(tpScale, lineWidth = 0, markerSize = 2, markerColor = ROOT.kRed, markerStyle = 20)

    rhScale = h_aieta.ProfileY("rh_%s_%d"%(h_aieta.GetName(),h_aieta.GetUniqueID()), 1, -1, "s"); ROOT.SetOwnership(rhScale, False); rhScale.Sumw2()
    rhScale = remapProfile(rhScale)
    set1Doptions(rhScale, lineWidth = 0, markerSize = 2, markerColor = ROOT.kBlack, markerStyle = 21)

    l = ROOT.TLine(0, 0, 10.5, 10.5) 
    l.SetLineWidth(3)
    l.SetLineColor(ROOT.kBlack)
    l.SetLineStyle(2)

    h_aieta.Draw("COLZ")
    l.Draw("SAME")
    tpScale.Draw("EPSAME")
    rhScale.Draw("EPSAME")

    c.SaveAs("%s/TP_vs_RH_Corr_ieta%d.pdf"%(plotsDir, aieta))

def analysis(PFAXFileDir, outDir, plotsDir):

    onEOS = "store" in PFAXFileDir

    if not os.path.exists(outDir):   os.makedirs(outDir)
    if not os.path.exists(plotsDir): os.makedirs(plotsDir)

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

    histo3D_RH = makeNDhisto(cPFAX, ["ieta" , "RH_energy", "soi_peak"], [57, -28.5, 28.5, 1440, -0.125, 359.875, 2, -0.5, 1.5], ["i#eta", "E_{T,RH}", "IsPeak"], "RH_energy>-1.0&&TP_energy>-10.0"); histo3D_RH.SetDirectory(0)

    RH_vs_ieta_yespeak = make2Dhisto(histo3D_RH, ["Z", 1, 1], ["ieta", "RHET", "Peak"])
    RH_vs_ieta_nopeak  = make2Dhisto(histo3D_RH, ["Z", 0, 0], ["ieta", "RHET", "Peak"])

    makeRHspectrumPlots(plotsDir, RH_vs_ieta_yespeak, RH_vs_ieta_nopeak)

    histo3D_TPRH = makeNDhisto(cPFAX, ["RH_energy", "TP_energy", "abs(ieta)"], [1440, -0.0444, 127.9556, 257, -0.25, 128.25, 28, 0.5, 28.5], ["E_{T,RH}", "E_{T,TP}", "|i#eta|"], "soi_peak==1"); histo3D_TPRH.SetDirectory(0)

    makeTPRHcorrelationPlots(plotsDir, histo3D_TPRH, 27)

    makeTPRHcorrelationPlots(plotsDir, histo3D_TPRH, 28)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--inputSubPath" , dest="inputSubPath" , help="Subpath to input files"     , type=str , required=True)
    parser.add_argument("--tag"          , dest="tag"          , help="Unique tag for separating"  , type=str , default="")
    args = parser.parse_args()

    HOME = os.getenv("HOME"); USER = os.getenv("USER")
    INPUTLOC = "/eos/uscms/store/user/%s/HCAL_Trigger_Study/hcalNtuples"%(USER)
    OUTPUTLOC = "%s/nobackup/HCAL_Trigger_Study/input/Ratios"%(HOME)
    PLOTSLOC = "%s/nobackup/HCAL_Trigger_Study/plots/Ratios"%(HOME)

    # Let the output folder structure mirror the input folder structure
    fileStub = args.inputSubPath
    tag      = args.tag

    analysis(INPUTLOC + "/" + fileStub, OUTPUTLOC + "/" + tag + "/" + fileStub, PLOTSLOC + "/" + tag + "/" + fileStub)
