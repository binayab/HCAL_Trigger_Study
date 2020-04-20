import sys, os, ROOT, subprocess, argparse
from toolbox import *

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.TH1.SetDefaultSumw2()
ROOT.TH2.SetDefaultSumw2()
ROOT.TH3.SetDefaultSumw2()

def makeTPRHratioPlot(plotsDir, histos, noPeakFind, tag = ""):

    tm = 0.05; bm = 0.30; lm = 0.11; rm = 0.03

    split4 = 0.318792; split1 = 0.234899; split2 = 0.223154
    ratio4 = split2 / split4; ratio1 = split2 / split1

    xl = 0.16; yl = 0.16; zl = 0.16; xt = 0.22; yt = 0.15; zt = 0.22; xo = 0.55; yo = 0.32; zo = 0.4 
    c = ROOT.TCanvas("c", "c", 2000, 1800)
    c.Divide(1,4) 

    schemes = histos.keys()

    colors = {schemes[0] : [ROOT.TColor.GetColor("#cbc9e2"), ROOT.TColor.GetColor("#9e9ac8"), ROOT.TColor.GetColor("#756bb1"), ROOT.TColor.GetColor("#54278f")],
              schemes[1] : [ROOT.TColor.GetColor("#bae4b3"), ROOT.TColor.GetColor("#74c476"), ROOT.TColor.GetColor("#31a354"), ROOT.TColor.GetColor("#006d2c")],
              schemes[2] : [ROOT.TColor.GetColor("#bdd7e7"), ROOT.TColor.GetColor("#6baed6"), ROOT.TColor.GetColor("#3182bd"), ROOT.TColor.GetColor("#08519c")],
              schemes[3] : [ROOT.TColor.GetColor("#cccccc"), ROOT.TColor.GetColor("#969696"), ROOT.TColor.GetColor("#636363"), ROOT.TColor.GetColor("#252525")]
    }

    hline = ROOT.TH1F("hline", "hline", 57, -28.5, 28.5)
    for xbin in xrange(1, 58): hline.SetBinContent(xbin, 1.0)
    hline.SetLineWidth(3)
    hline.SetLineColor(ROOT.kRed)
    hline.SetLineStyle(2)

    for scheme, histoList in histos.iteritems():

        if "PFA1p" in scheme:
            c.cd(4)
            ROOT.gPad.SetPad(0, 0.0, 1, split4)
            ROOT.gPad.SetGridx(); ROOT.gPad.SetGridy();
            ROOT.gPad.SetTopMargin(0.0)
            ROOT.gPad.SetBottomMargin(bm)
            ROOT.gPad.SetLeftMargin(lm)
            ROOT.gPad.SetRightMargin(rm)

            for histo in histoList:
                profile = histo.ProfileX("%s_%d_%s_%d"%(histo.GetName(),histo.GetUniqueID(), scheme, histoList.index(histo)), 1, -1, "s"); profile.Sumw2()

                profile.GetYaxis().SetNdivisions(6,5,0)
                setAxisDims(profile, xl*ratio4, yl*ratio4, zl*ratio4, xt*ratio4, yt*ratio4, zt*ratio4, xo/ratio4, yo/ratio4, zo/ratio4)
                setAxisRanges(profile, yMin = 0.61, yMax = 1.95)
                setAxisLabels(profile, lab = "", xLab = "i#eta")

                if "NOPU" in histo.GetName(): set1Doptions(profile, lineWidth = 0, markerSize = 3, markerColor = ROOT.kBlack, markerStyle = 24)
                else:                         set1Doptions(profile, lineWidth = 0, markerSize = 3, markerColor = colors[scheme][histoList.index(histo)-1], markerStyle = 20)

                profile.Draw("EPSAME")

            hline.Draw("][ HIST SAME")

        elif scheme == "PFA1":
            c.cd(3)
            ROOT.gPad.SetPad(0, split4, 1, split2+split4)
            ROOT.gPad.SetGridx(); ROOT.gPad.SetGridy();
            ROOT.gPad.SetTopMargin(0.0)
            ROOT.gPad.SetBottomMargin(0.0)
            ROOT.gPad.SetLeftMargin(lm)
            ROOT.gPad.SetRightMargin(rm)

            for histo in histoList:
                profile = histo.ProfileX("%s_%d_%s_%d"%(histo.GetName(),histo.GetUniqueID(), scheme, histoList.index(histo)), 1, -1, "s"); profile.Sumw2()

                profile.GetYaxis().SetNdivisions(6,5,0)
                setAxisDims(profile, xl, yl, zl, xt, yt, zt, xo, yo, zo)
                setAxisRanges(profile, yMin = 0.61, yMax = 1.95)

                if "NOPU" in histo.GetName(): set1Doptions(profile, lineWidth = 0, markerSize = 3, markerColor = ROOT.kBlack, markerStyle = 32)
                else:                         set1Doptions(profile, lineWidth = 0, markerSize = 3, markerColor = colors[scheme][histoList.index(histo)-1], markerStyle = 23)

                profile.Draw("EPSAME")

            hline.Draw("][ HIST SAME")

        elif "PFA2p" in scheme:
            c.cd(2)
            ROOT.gPad.SetPad(0, split2+split4, 1, 2.0*split2+split4)
            ROOT.gPad.SetGridx(); ROOT.gPad.SetGridy();
            ROOT.gPad.SetTopMargin(0.0)
            ROOT.gPad.SetBottomMargin(0.0)
            ROOT.gPad.SetLeftMargin(lm)
            ROOT.gPad.SetRightMargin(rm)

            for histo in histoList:
                profile = histo.ProfileX("%s_%d_%s_%d"%(histo.GetName(),histo.GetUniqueID(), scheme, histoList.index(histo)), 1, -1, "s"); profile.Sumw2()

                profile.GetYaxis().SetNdivisions(6,5,0)
                setAxisDims(profile, xl, yl, zl, xt, yt, zt, xo, yo, zo)
                setAxisRanges(profile, yMin = 0.61, yMax = 1.95)
                setAxisLabels(profile, lab = "")

                if "NOPU" in histo.GetName(): set1Doptions(profile, lineWidth = 0, markerSize = 3, markerColor = ROOT.kBlack, markerStyle = 25)
                else:                         set1Doptions(profile, lineWidth = 0, markerSize = 3, markerColor = colors[scheme][histoList.index(histo)-1], markerStyle = 21)

                profile.Draw("EPSAME")

            hline.Draw("][ HIST SAME")

        elif "PFA2" in scheme:
            c.cd(1)
            ROOT.gPad.SetPad(0, 1.0-split1, 1, 1.0)
            ROOT.gPad.SetGridx(); ROOT.gPad.SetGridy();
            ROOT.gPad.SetTopMargin(tm)
            ROOT.gPad.SetBottomMargin(0.0)
            ROOT.gPad.SetLeftMargin(lm)
            ROOT.gPad.SetRightMargin(rm)

            for histo in histoList:
                profile = histo.ProfileX("%s_%d_%s_%d"%(histo.GetName(),histo.GetUniqueID(), scheme, histoList.index(histo)), 1, -1, "s"); profile.Sumw2()

                profile.GetYaxis().SetNdivisions(6,5,0)
                setAxisDims(profile, xl*ratio1, yl*ratio1, zl*ratio1, xt*ratio1, yt*ratio1, zt*ratio1, xo/ratio1, yo/ratio1, zo/ratio1)
                setAxisRanges(profile, yMin = 0.61, yMax = 1.95)
                setAxisLabels(profile, lab = "", yLab = "#mu#left(E_{T,TP} / E_{T,RH}#right)")

                if "NOPU" in histo.GetName(): set1Doptions(profile, lineWidth = 0, markerSize = 3, markerColor = ROOT.kBlack, markerStyle = 26)
                else:                         set1Doptions(profile, lineWidth = 0, markerSize = 3, markerColor = colors[scheme][histoList.index(histo)-1], markerStyle = 22)

                profile.Draw("EPSAME")

            hline.Draw("][ HIST SAME")

    if noPeakFind: c.SaveAs("%s/n%s_%s_%s_EtScale_PU%s.pdf"%(plotsDir,schemes[0].split("_")[0], schemes[1].split("_")[0], schemes[2].split("_")[0], tag))
    else:        c.SaveAs("%s/%s_%s_%s_EtScale_PU%s.pdf"%(plotsDir,schemes[0].split("_")[0], schemes[1].split("_")[0], schemes[2].split("_")[0], tag))

def makeTPRHresPlot(plotsDir, histos, noPeakFind, tag = ""):

    tm = 0.05; bm = 0.30; lm = 0.11; rm = 0.03

    split4 = 0.318792; split1 = 0.234899; split2 = 0.223154
    ratio4 = split2 / split4; ratio1 = split2 / split1

    xl = 0.16; yl = 0.16; zl = 0.16; xt = 0.22; yt = 0.15; zt = 0.22; xo = 0.55; yo = 0.32; zo = 0.4 
    c = ROOT.TCanvas("c", "c", 2000, 1800)
    c.Divide(1,4) 

    schemes = histos.keys()

    colors = {schemes[0] : [ROOT.TColor.GetColor("#cbc9e2"), ROOT.TColor.GetColor("#9e9ac8"), ROOT.TColor.GetColor("#756bb1"), ROOT.TColor.GetColor("#54278f")],
              schemes[1] : [ROOT.TColor.GetColor("#bae4b3"), ROOT.TColor.GetColor("#74c476"), ROOT.TColor.GetColor("#31a354"), ROOT.TColor.GetColor("#006d2c")],
              schemes[2] : [ROOT.TColor.GetColor("#bdd7e7"), ROOT.TColor.GetColor("#6baed6"), ROOT.TColor.GetColor("#3182bd"), ROOT.TColor.GetColor("#08519c")],
              schemes[3] : [ROOT.TColor.GetColor("#cccccc"), ROOT.TColor.GetColor("#969696"), ROOT.TColor.GetColor("#636363"), ROOT.TColor.GetColor("#252525")]
    }

    for scheme, histoList in histos.iteritems():

        if "PFA1p" in scheme:
            c.cd(4)
            ROOT.gPad.SetPad(0, 0.0, 1, split4)
            ROOT.gPad.SetGridx(); ROOT.gPad.SetGridy();
            ROOT.gPad.SetTopMargin(0.0)
            ROOT.gPad.SetBottomMargin(bm)
            ROOT.gPad.SetLeftMargin(lm)
            ROOT.gPad.SetRightMargin(rm)

            for histo in histoList:
                profile = histo.ProfileX("%s_%d_%s_%d_res"%(histo.GetName(),histo.GetUniqueID(), scheme, histoList.index(histo)), 1, -1, "s"); profile.Sumw2()
    
                stdProfile = stdDevProfile(profile)

                stdProfile.GetYaxis().SetNdivisions(6,5,0)
                setAxisDims(stdProfile, xl*ratio4, yl*ratio4, zl*ratio4, xt*ratio4, yt*ratio4, zt*ratio4, xo/ratio4, yo/ratio4, zo/ratio4)
                setAxisRanges(stdProfile, yMin = 0.01, yMax = 0.65)
                setAxisLabels(stdProfile, lab = "", xLab = "i#eta")
                
                if "NOPU" in histo.GetName(): set1Doptions(stdProfile, lineWidth = 3, markerSize = 3, markerColor = ROOT.kBlack, markerStyle = 24)
                else:                         set1Doptions(stdProfile, lineWidth = 3, markerSize = 3, markerColor = colors[scheme][histoList.index(histo)-1], markerStyle = 20)

                stdProfile.Draw("EPSAME")

        elif scheme == "PFA1":
            c.cd(3)
            ROOT.gPad.SetPad(0, split4, 1, split2+split4)
            ROOT.gPad.SetGridx(); ROOT.gPad.SetGridy();
            ROOT.gPad.SetTopMargin(0.0)
            ROOT.gPad.SetBottomMargin(0.0)
            ROOT.gPad.SetLeftMargin(lm)
            ROOT.gPad.SetRightMargin(rm)

            for histo in histoList:
                profile = histo.ProfileX("%s_%d_%s_%d_res"%(histo.GetName(),histo.GetUniqueID(), scheme, histoList.index(histo)), 1, -1, "s"); profile.Sumw2()
                stdProfile = stdDevProfile(profile)

                stdProfile.GetYaxis().SetNdivisions(6,5,0)
                setAxisDims(stdProfile, xl, yl, zl, xt, yt, zt, xo, yo, zo)
                setAxisRanges(stdProfile, yMin = 0.01, yMax = 0.65)
                setAxisLabels(stdProfile, lab = "", yLab = "")

                if "NOPU" in histo.GetName(): set1Doptions(stdProfile, lineWidth = 3, markerSize = 3, markerColor = ROOT.kBlack, markerStyle = 32)
                else:                         set1Doptions(stdProfile, lineWidth = 3, markerSize = 3, markerColor = colors[scheme][histoList.index(histo)-1], markerStyle = 23)

                stdProfile.Draw("EPSAME")

        elif "PFA2p" in scheme:
            c.cd(2)
            ROOT.gPad.SetPad(0, split2+split4, 1, 2.0*split2+split4)
            ROOT.gPad.SetGridx(); ROOT.gPad.SetGridy();
            ROOT.gPad.SetTopMargin(0.0)
            ROOT.gPad.SetBottomMargin(0.0)
            ROOT.gPad.SetLeftMargin(lm)
            ROOT.gPad.SetRightMargin(rm)

            for histo in histoList:
                profile = histo.ProfileX("%s_%d_%s_%d_res"%(histo.GetName(),histo.GetUniqueID(), scheme, histoList.index(histo)), 1, -1, "s"); profile.Sumw2()
                stdProfile = stdDevProfile(profile)

                stdProfile.GetYaxis().SetNdivisions(6,5,0)
                setAxisDims(stdProfile, xl, yl, zl, xt, yt, zt, xo, yo, zo)
                setAxisRanges(stdProfile, yMin = 0.01, yMax = 0.65)
                setAxisLabels(stdProfile, lab = "", yLab = "")

                if "NOPU" in histo.GetName(): set1Doptions(stdProfile, lineWidth = 3, markerSize = 3, markerColor = ROOT.kBlack, markerStyle = 25)
                else:                         set1Doptions(stdProfile, lineWidth = 3, markerSize = 3, markerColor = colors[scheme][histoList.index(histo)-1], markerStyle = 21)

                stdProfile.Draw("EPSAME")

        elif scheme == "PFA2":
            c.cd(1)
            ROOT.gPad.SetPad(0, 1-split1, 1, 1.0)
            ROOT.gPad.SetGridx(); ROOT.gPad.SetGridy();
            ROOT.gPad.SetTopMargin(tm)
            ROOT.gPad.SetBottomMargin(0.0)
            ROOT.gPad.SetLeftMargin(lm)
            ROOT.gPad.SetRightMargin(rm)

            for histo in histoList:
                profile = histo.ProfileX("%s_%d_%s_%d_res"%(histo.GetName(),histo.GetUniqueID(), scheme, histoList.index(histo)), 1, -1, "s"); profile.Sumw2()
                stdProfile = stdDevProfile(profile)

                stdProfile.GetYaxis().SetNdivisions(6,5,0)
                setAxisDims(stdProfile, xl*ratio1, yl*ratio1, zl*ratio1, xt*ratio1, yt*ratio1, zt*ratio1, xo/ratio1, yo/ratio1, zo/ratio1)
                setAxisRanges(stdProfile, yMin = 0.01, yMax = 0.65)
                setAxisLabels(stdProfile, lab = "", yLab = "#sigma#left(E_{T,TP} / E_{T,RH}#right)")

                if "NOPU" in histo.GetName(): set1Doptions(stdProfile, lineWidth = 3, markerSize = 3, markerColor = ROOT.kBlack, markerStyle = 26)
                else:                         set1Doptions(stdProfile, lineWidth = 3, markerSize = 3, markerColor = colors[scheme][histoList.index(histo)-1], markerStyle = 22)

                stdProfile.Draw("EPSAME")

    if noPeakFind: c.SaveAs("%s/n%s_%s_%s_EtResolution_PU%s.pdf"%(plotsDir,schemes[0].split("_")[0], schemes[1].split("_")[0], schemes[2].split("_")[0], tag))
    else:        c.SaveAs("%s/%s_%s_%s_EtResolution_PU%s.pdf"%(plotsDir,schemes[0].split("_")[0], schemes[1].split("_")[0], schemes[2].split("_")[0], tag))

def analysis(PFAXFileDirs, chains, outDir, plotsDir, noPeakFind):

    onEOS = "store" in PFAXFileDirs[PFAXFileDirs.keys()[0]][0]

    if not os.path.exists(outDir):   os.makedirs(outDir)
    if not os.path.exists(plotsDir): os.makedirs(plotsDir)

    # Whether on EOS or locally, get the list of files to run on 
    proc = 0; allItems = {}
    for scheme in PFAXFileDirs.keys(): allItems[scheme] = []
    if onEOS: 
        for scheme, paths in PFAXFileDirs.iteritems():
            for path in paths:
                proc = subprocess.Popen(["xrdfs", "root://cmseos.fnal.gov", "ls", path], stdout=subprocess.PIPE)
                allItemsTemp = proc.stdout.readlines();  allItems[scheme].append([item.rstrip() for item in allItemsTemp])
    else:
        allItems[scheme].append(os.listdir(pfaDir))

    # Add only honest root files to TChain
    for scheme, fileLists in allItems.iteritems():
        
        for fileList in fileLists:
            for file in fileList:
                if ".root" not in file: continue
    
                if onEOS: chains[scheme][fileLists.index(fileList)].AddFile("root://cmseos.fnal.gov/"+file)
                else:     chains[scheme][fileLists.index(fileList)].AddFile(file)

    histosLow  = {}
    histosHigh = {}
    for scheme in PFAXFileDirs.keys():
        histosLow[scheme]  = []
        histosHigh[scheme] = []
  
    for scheme, chainList in chains.iteritems():
        for chain in chainList:
            histoLow = 0; histoHigh = 0
            if noPeakFind and "PFA1p" in scheme:
                histoLow = makeNDhisto(chain, ["ieta", "TP_energy/RH_energy"], [57, -28.5, 28.5, 720, -0.014, 19.986], ["i#eta", "E_{T,TP} / E_{T,RH}"], "TP_energy>0.5&&RH_energy>0.0&&RH_energy<=10.0")
                histoHigh = makeNDhisto(chain, ["ieta", "TP_energy/RH_energy"], [57, -28.5, 28.5, 720, -0.014, 19.986], ["i#eta", "E_{T,TP} / E_{T,RH}"], "TP_energy>0.5&&RH_energy>10.0")

            else:
                histoLow = makeNDhisto(chain, ["ieta", "TP_energy/RH_energy"], [57, -28.5, 28.5, 720, -0.014, 19.986], ["i#eta", "E_{T,TP} / E_{T,RH}"], "soi_peak==1&&TP_energy>0.5&&RH_energy>0.0&&RH_energy<=10.0")
                histoHigh = makeNDhisto(chain, ["ieta", "TP_energy/RH_energy"], [57, -28.5, 28.5, 720, -0.014, 19.986], ["i#eta", "E_{T,TP} / E_{T,RH}"], "soi_peak==1&&TP_energy>0.5&&RH_energy>10.0")
            histosLow[scheme].append(histoLow)
            histosHigh[scheme].append(histoHigh)

    makeTPRHratioPlot(plotsDir, histosLow, noPeakFind, "_Low")
    makeTPRHresPlot(plotsDir,   histosLow, noPeakFind, "_Low")
  
    makeTPRHratioPlot(plotsDir, histosHigh, noPeakFind, "_High")
    makeTPRHresPlot(plotsDir,   histosHigh, noPeakFind, "_High")

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--scenarios"  , dest="scenarios"  , help="List of pileup scenarios", nargs="+", required=True)
    parser.add_argument("--schemes"    , dest="schemes"    , help="List of schemes"         , nargs="+", required=True)
    parser.add_argument("--noPeakFind" , dest="noPeakFind" , help="No peak find for PFA1p" , action="store_true", default=False)
    parser.add_argument("--tag"        , dest="tag"        , help="Unique tag for separating"  , type=str , default="")
    args = parser.parse_args()

    HOME = os.getenv("HOME"); USER = os.getenv("USER")
    INPUTLOC = "/eos/uscms/store/user/%s/HCAL_Trigger_Study/hcalNtuples"%(USER)
    OUTPUTLOC = "%s/nobackup/HCAL_Trigger_Study/input/Ratios"%(HOME)
    PLOTSLOC = "%s/nobackup/HCAL_Trigger_Study/plots/Ratios"%(HOME)

    # Let the output folder structure mirror the input folder structure
    filePaths = {}; chains = {}
    for scheme in args.schemes:
        filePaths[scheme] = []
        chains[scheme] = []

    for scheme in args.schemes:
        for scenario in args.scenarios:
            filePaths[scheme].append(INPUTLOC + "/" + scenario + "/" + scheme)
            chains[scheme].append(ROOT.TChain("compareReemulRecoSeverity9/matches", scheme + scenario))

    tag      = args.tag

    analysis(filePaths, chains, OUTPUTLOC + "/" + tag, PLOTSLOC + "/" + tag, args.noPeakFind)
