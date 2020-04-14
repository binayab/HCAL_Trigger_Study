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

def makeRHspectrumPlots(plotsDir, cPFAX):

    histo3D_RH = makeNDhisto(cPFAX, ["ieta" , "RH_energy", "soi_peak"], [57, -28.5, 28.5, 1440, -0.125, 359.875, 2, -0.5, 1.5], ["i#eta", "E_{T,RH}", "IsPeak"], "RH_energy>-1.0&&TP_energy>0.5"); histo3D_RH.SetDirectory(0)

    RH_vs_ieta_yespeak = make2Dhisto(histo3D_RH, ["Z", 1, 1], ["ieta", "RHET", "Peak"])
    RH_vs_ieta_nopeak  = make2Dhisto(histo3D_RH, ["Z", 0, 0], ["ieta", "RHET", "Peak"])

    for subdet, ranges in {"HB" : [-16, -1, 1, 16], "HE" : [-28, -17, 17, 28]}.iteritems():
        RH_yespeak = make1Dhisto(RH_vs_ieta_yespeak, ["X", ranges[0], ranges[1], ranges[2], ranges[3]], ["ieta", "RHET", "Peak"], "_wPeak")
        RH_nopeak  = make1Dhisto(RH_vs_ieta_nopeak,  ["X", ranges[0], ranges[1], ranges[2], ranges[3]], ["ieta", "RHET", "Peak"], "_woPeak")

        c = ROOT.TCanvas("c_%s_%s"%(RH_yespeak.GetName(), subdet), "c_%s_%s"%(RH_yespeak.GetName(), subdet), 1600, 900); c.cd(); c.SetLogy()
        ROOT.gPad.SetGridy(); ROOT.gPad.SetGridx()
        ROOT.gPad.SetTopMargin(0.026)
        ROOT.gPad.SetBottomMargin(0.15)
        ROOT.gPad.SetLeftMargin(0.11)
        ROOT.gPad.SetRightMargin(0.03)

        setAxisDims(RH_yespeak, 0.059, 0.059, 0.059, 0.072, 0.072, 0.072, 0.95, 0.75, 1.0)
        setAxisRanges(RH_yespeak, xMin = -0.5, xMax = 20.0)
        setAxisLabels(RH_yespeak, lab = "", yLab = "A.U.")
        set1Doptions(RH_yespeak, lineColor = ROOT.kBlack, markerSize = 0, lineWidth = 3, markerColor = ROOT.kBlack)
        set1Doptions(RH_nopeak,  lineColor = ROOT.kRed,   markerSize = 0, lineWidth = 3, markerColor = ROOT.kRed)

        RH_yespeak.Draw("HIST")
        RH_nopeak.Draw("HIST SAME")
        
        c.SaveAs("%s/%s_%s.pdf"%(plotsDir, RH_yespeak.GetName(), subdet))

    tm = 0.05; bm = 0.20; lm = 0.09; rm = 0.12; split = 0.542857; ratio = (1.0 - split) / split
    xl = 0.095; yl = 0.095; zl = 0.095; xt = 0.15; yt = 0.15; zt = 0.15; xo = 0.50; yo = 0.27; zo = 0.8 
    c = ROOT.TCanvas("c_%s_%s"%(RH_vs_ieta_yespeak.GetName(), subdet), "c_%s_%s"%(RH_vs_ieta_yespeak.GetName(), subdet), 1600, 1200)
    c.Divide(1,2) 
    c.cd(1); ROOT.gPad.SetLogz()
    ROOT.gPad.SetPad(0, split, 1, 1)
    ROOT.gPad.SetTopMargin(tm)
    ROOT.gPad.SetBottomMargin(0.0)
    ROOT.gPad.SetLeftMargin(lm)
    ROOT.gPad.SetRightMargin(rm)

    setAxisDims(RH_vs_ieta_yespeak, xl, yl, zl, xt, yt, zt, xo, yo, zo)
    setAxisRebins(RH_vs_ieta_yespeak, yReb = 1)
    setAxisRanges(RH_vs_ieta_yespeak, yMin = -0.99, yMax = 11.0, zMin = 2e-1, zMax = 2e6)
    setAxisLabels(RH_vs_ieta_yespeak, lab = "", xLab = "", yLab = "E_{T,RH} [GeV]")
    set2Doptions(RH_vs_ieta_yespeak)
    RH_vs_ieta_yespeak.Draw("COLZ")

    c.cd(2); ROOT.gPad.SetLogz()
    ROOT.gPad.SetPad(0, 0.0, 1, split)
    ROOT.gPad.SetTopMargin(0.0)
    ROOT.gPad.SetBottomMargin(bm)
    ROOT.gPad.SetLeftMargin(lm)
    ROOT.gPad.SetRightMargin(rm)

    setAxisDims(RH_vs_ieta_nopeak, xl*ratio, yl*ratio, zl*ratio, xt*ratio, yt*ratio, zt*ratio, xo/ratio, yo/ratio, zo/ratio)
    setAxisRanges(RH_vs_ieta_nopeak, yMin = -0.99, yMax = 11.0, zMin = 2e-1, zMax = 2e6)
    setAxisLabels(RH_vs_ieta_nopeak, lab = "", xLab = "i#eta", yLab = "")
    set2Doptions(RH_vs_ieta_nopeak)
    RH_vs_ieta_nopeak.Draw("COLZ")

    c.SaveAs("%s/%s.pdf"%(plotsDir, RH_vs_ieta_yespeak.GetName()))

def makeTPRH_vs_rTS(plotsDir, cPFAX, tag):

    histo2D = makeNDhisto(cPFAX, ["rTPRH", "r43"], [68, 0.1, 1.3, 68, 0.11, 1.09], ["E_{T,TP} / E_{T,RH}", "TS4 / TS3"], "RH_energy>10.0&&tp_soi!=255")

    tm = 0.02; bm = 0.14; lm = 0.10; rm = 0.12; ratio = 1.0
    xl = 0.055; yl = 0.055; zl = 0.055; xt = 0.065; yt = 0.065; zt = 0.065; xo = 0.95; yo = 0.84; zo = 0.8 
    c = ROOT.TCanvas("c_%s_%s"%(histo2D.GetName(), tag), "c_%s_%s"%(histo2D.GetName(), tag), 2400, 1440)
    c.cd(); ROOT.gPad.SetLogz()
    ROOT.gPad.SetPad(0, 0.0, 1, 1.0)
    ROOT.gPad.SetTopMargin(tm)
    ROOT.gPad.SetBottomMargin(bm)
    ROOT.gPad.SetLeftMargin(lm)
    ROOT.gPad.SetRightMargin(rm)

    setAxisDims(histo2D, xl*ratio, yl*ratio, zl*ratio, xt*ratio, yt*ratio, zt*ratio, xo/ratio, yo/ratio, zo/ratio)
    setAxisRanges(histo2D, zMin = 1, zMax = 2e4)
    set2Doptions(histo2D)

    histo2D.Draw("COLZ")

    c.SaveAs("%s/TPRH_vs_%s.pdf"%(plotsDir, tag))

def makeTPRH_vs_RH(plotsDir, cPFAX):

    histo2D = makeNDhisto(cPFAX, ["RH_energy", "rTPRH"], [128, 0, 256, 68, 0.1, 2.0], ["E_{T,RH}", "E_{T,TP} / E_{T,RH}"], "soi_peak==1&&TP_energy>0.5")

    tm = 0.02; bm = 0.14; lm = 0.11; rm = 0.12; ratio = 1.0
    xl = 0.055; yl = 0.055; zl = 0.055; xt = 0.065; yt = 0.065; zt = 0.065; xo = 0.95; yo = 0.78; zo = 0.8 
    c = ROOT.TCanvas("c_%s_%s"%(histo2D.GetName(), tag), "c_%s_%s"%(histo2D.GetName(), tag), 2400, 1440)
    c.cd(); ROOT.gPad.SetLogz()
    ROOT.gPad.SetPad(0, 0.0, 1, 1.0)
    ROOT.gPad.SetTopMargin(tm)
    ROOT.gPad.SetBottomMargin(bm)
    ROOT.gPad.SetLeftMargin(lm)
    ROOT.gPad.SetRightMargin(rm)

    setAxisDims(histo2D, xl*ratio, yl*ratio, zl*ratio, xt*ratio, yt*ratio, zt*ratio, xo/ratio, yo/ratio, zo/ratio)
    setAxisRanges(histo2D, zMin = 1, zMax = 6e4)
    set2Doptions(histo2D)

    histo2D.Draw("COLZ")

    c.SaveAs("%s/TPRH_vs_RH.pdf"%(plotsDir))

def make43_vs_RH(plotsDir, cPFAX):

    histo2D = makeNDhisto(cPFAX, ["RH_energy", "r43"], [256, 0, 256, 68, 0.1, 1.1], ["E_{T,RH}", "TS4 / TS3"], "soi_peak==1&&TP_energy>0.5")

    tm = 0.02; bm = 0.14; lm = 0.11; rm = 0.12; ratio = 1.0
    xl = 0.055; yl = 0.055; zl = 0.055; xt = 0.065; yt = 0.065; zt = 0.065; xo = 0.95; yo = 0.78; zo = 0.8 
    c = ROOT.TCanvas("c_%s_%s"%(histo2D.GetName(), tag), "c_%s_%s"%(histo2D.GetName(), tag), 2400, 1440)
    c.cd(); ROOT.gPad.SetLogz()
    ROOT.gPad.SetPad(0, 0.0, 1, 1.0)
    ROOT.gPad.SetTopMargin(tm)
    ROOT.gPad.SetBottomMargin(bm)
    ROOT.gPad.SetLeftMargin(lm)
    ROOT.gPad.SetRightMargin(rm)

    setAxisDims(histo2D, xl*ratio, yl*ratio, zl*ratio, xt*ratio, yt*ratio, zt*ratio, xo/ratio, yo/ratio, zo/ratio)
    setAxisRanges(histo2D, zMin = 1, zMax = 6e4)
    set2Doptions(histo2D)

    histo2D.Draw("COLZ")

    c.SaveAs("%s/r43_vs_RH.pdf"%(plotsDir))

def makeTS3_vs_RH(plotsDir, cPFAX):

    histo2D = makeNDhisto(cPFAX, ["RH_energy", "ts3"], [256, 0, 256, 200, 0, 2048], ["E_{T,RH}", "TS3 [ADC]"], "soi_peak==1&&TP_energy>0.5")

    tm = 0.02; bm = 0.14; lm = 0.11; rm = 0.12; ratio = 1.0
    xl = 0.055; yl = 0.055; zl = 0.055; xt = 0.065; yt = 0.065; zt = 0.065; xo = 0.95; yo = 0.86; zo = 0.8 
    c = ROOT.TCanvas("c_%s_%s"%(histo2D.GetName(), tag), "c_%s_%s"%(histo2D.GetName(), tag), 2400, 1440)
    c.cd(); ROOT.gPad.SetLogz()
    ROOT.gPad.SetPad(0, 0.0, 1, 1.0)
    ROOT.gPad.SetTopMargin(tm)
    ROOT.gPad.SetBottomMargin(bm)
    ROOT.gPad.SetLeftMargin(lm)
    ROOT.gPad.SetRightMargin(rm)

    setAxisDims(histo2D, xl*ratio, yl*ratio, zl*ratio, xt*ratio, yt*ratio, zt*ratio, xo/ratio, yo/ratio, zo/ratio)
    setAxisRanges(histo2D, zMin = 1, zMax = 6e4)
    set2Doptions(histo2D)

    histo2D.Draw("COLZ")

    c.SaveAs("%s/TS3_vs_RH.pdf"%(plotsDir))

def makeTPRH_vs_TS3(plotsDir, cPFAX):

    histo2D = makeNDhisto(cPFAX, ["ts3", "rTPRH"], [100, 0, 2048, 68, 0.1, 2.0], ["SOI [Linearized ADC]", "E_{T,TP} / E_{T,RH}"], "soi_peak==1&&TP_energy>0.5&&tp_soi!=255")

    tm = 0.02; bm = 0.14; lm = 0.11; rm = 0.12; ratio = 1.0
    xl = 0.055; yl = 0.055; zl = 0.055; xt = 0.065; yt = 0.065; zt = 0.065; xo = 0.95; yo = 0.78; zo = 0.8 
    c = ROOT.TCanvas("c_%s_%s"%(histo2D.GetName(), tag), "c_%s_%s"%(histo2D.GetName(), tag), 2400, 1440)
    c.cd(); ROOT.gPad.SetLogz()
    ROOT.gPad.SetPad(0, 0.0, 1, 1.0)
    ROOT.gPad.SetTopMargin(tm)
    ROOT.gPad.SetBottomMargin(bm)
    ROOT.gPad.SetLeftMargin(lm)
    ROOT.gPad.SetRightMargin(rm)

    setAxisDims(histo2D, xl*ratio, yl*ratio, zl*ratio, xt*ratio, yt*ratio, zt*ratio, xo/ratio, yo/ratio, zo/ratio)
    setAxisRanges(histo2D, zMin = 1, zMax = 6e4)
    set2Doptions(histo2D)

    histo2D.Draw("COLZ")

    c.SaveAs("%s/TPRH_vs_TS3.pdf"%(plotsDir))

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

    #makeTPRH_vs_rTS(plotsDir, cPFAX, "43")

    #makeTPRH_vs_RH(plotsDir, cPFAX)

    #make43_vs_RH(plotsDir, cPFAX)

    #makeTS3_vs_RH(plotsDir, cPFAX)

    makeTPRH_vs_TS3(plotsDir, cPFAX)

    #makeRHspectrumPlots(plotsDir, cPFAX)

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

    analysis(INPUTLOC + "/" + fileStub, OUTPUTLOC + "/" + tag + "/" + fileStub, PLOTSLOC + "/" + fileStub + "/" + tag)
