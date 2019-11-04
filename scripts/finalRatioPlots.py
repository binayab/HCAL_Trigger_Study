import sys, os, ROOT, argparse

ROOT.TH1.SetDefaultSumw2()
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetPaintTextFormat("3.2f")
ROOT.gStyle.SetFrameLineWidth(2)
ROOT.gStyle.SetErrorX(0)

usage = "usage: %prog [options]"
parser = argparse.ArgumentParser(usage)
parser.add_argument("--tag"      , dest="tag"      , type=str, default=""    , help="Unique tag for output")
parser.add_argument("--pfaY"     , dest="pfaY"     , type=str, default="NULL", help="Path to inputs for PFAY")
parser.add_argument("--pfaX1"    , dest="pfaX1"    , type=str, default="NULL", help="Path to other PFAX dir") 
parser.add_argument("--pfaX2"    , dest="pfaX2"    , type=str, default="NULL", help="Path to other PFAX dir") 
parser.add_argument("--pfaYUp"   , dest="pfaYUp"   , type=str, default="NULL", help="Path to inputs for PFAY with up variation")
parser.add_argument("--pfaX1Up"  , dest="pfaX1Up"  , type=str, default="NULL", help="Path to other PFAX dir with up variation") 
parser.add_argument("--pfaX2Up"  , dest="pfaX2Up"  , type=str, default="NULL", help="Path to other PFAX dir with up variation") 
parser.add_argument("--pfaYDown" , dest="pfaYDown" , type=str, default="NULL", help="Path to inputs for PFAY with down variation")
parser.add_argument("--pfaX1Down", dest="pfaX1Down", type=str, default="NULL", help="Path to other PFAX dir with down variation") 
parser.add_argument("--pfaX2Down", dest="pfaX2Down", type=str, default="NULL", help="Path to other PFAX dir with down variation") 
arg = parser.parse_args()

OPTIONSMAP = {"TPRH_TPET_ieta1to16"  : {"X" : {"min" : 0.5, "max" : 20}, "Y" : {"min" : 0.2, "max" : 2}},
              "TPRH_RHET_ieta1to16"  : {"X" : {"min" : 0.5, "max" : 20}, "Y" : {"min" : 0.2, "max" : 2}},
              "TPRH_TPET_ieta17to28" : {"X" : {"min" : 0.5, "max" : 20}, "Y" : {"min" : 0.2, "max" : 2}},
              "TPRH_RHET_ieta17to28" : {"X" : {"min" : 0.5, "max" : 20}, "Y" : {"min" : 0.2, "max" : 2}},
              "TPRH_TPET_ieta1to28"  : {"X" : {"min" : 0.5, "max" : 20}, "Y" : {"min" : 0.2, "max" : 2}},
              "TPRH_RHET_ieta1to28"  : {"X" : {"min" : 0.5, "max" : 20}, "Y" : {"min" : 0.2, "max" : 2}}}

def makeBandGraph(histoUp, histoDown, color):
    
    npoints = histoUp.GetNbinsX()

    graphUp   = ROOT.TGraph(npoints)
    graphDown = ROOT.TGraph(npoints)
    graphBand = ROOT.TGraph(2*npoints)

    for iPoint in xrange(0, npoints):

        # Sweet hack for bin 29 or iPoint == 28, interpolate from surrounding bins
        if iPoint == 28: 
            graphUp.SetPoint(iPoint,   histoUp.GetBinCenter(iPoint+1), (histoUp.GetBinContent(iPoint)+histoUp.GetBinContent(iPoint+2))/2)
            graphDown.SetPoint(iPoint, histoUp.GetBinCenter(iPoint+1), (histoUp.GetBinContent(iPoint)+histoUp.GetBinContent(iPoint+2))/2)

            graphBand.SetPoint(iPoint,         histoUp.GetBinCenter(iPoint+1),       (histoUp.GetBinContent(iPoint)+histoUp.GetBinContent(iPoint+2))/2)
            graphBand.SetPoint(npoints+iPoint, histoUp.GetBinCenter(npoints-iPoint), (histoUp.GetBinContent(npoints-iPoint-1)+histoUp.GetBinContent(npoints-iPoint+1))/2)

        else:
            graphUp.SetPoint(iPoint,   histoUp.GetBinCenter(iPoint+1), histoUp.GetBinContent(iPoint+1))
            graphDown.SetPoint(iPoint, histoUp.GetBinCenter(iPoint+1), histoDown.GetBinContent(iPoint+1))

            graphBand.SetPoint(iPoint,         histoUp.GetBinCenter(iPoint+1),       histoUp.GetBinContent(iPoint+1))
            graphBand.SetPoint(npoints+iPoint, histoUp.GetBinCenter(npoints-iPoint), histoDown.GetBinContent(npoints-iPoint))

    graphUp.SetLineWidth(2);   graphUp.SetLineColorAlpha(color, 0.25)
    graphDown.SetLineWidth(2); graphDown.SetLineColorAlpha(color, 0.25)
    graphBand.SetFillColorAlpha(color, 0.15)

    return graphUp, graphDown, graphBand

def doOptions(histo, histoName):

    if histoName not in OPTIONSMAP: return

    is1D = "TH1" in histo.ClassName()

    for axis, options in OPTIONSMAP[histoName].iteritems():

        if axis == "X":
            if "rebin" in options:
                if is1D: histo.Rebin(options["rebin"])
                else: histo.RebinX(options["rebin"])
            if "min" in options and "max" in options: histo.GetXaxis().SetRangeUser(options["min"],options["max"])
            if "title" in options: histo.GetXaxis().SetTitle(options["title"])
        if axis == "Y":
            if "rebin" in options:
                if is1D: histo.Rebin(options["rebin"])
                else: histo.RebinY(options["rebin"])
            if "min" in options and "max" in options: histo.GetYaxis().SetRangeUser(options["min"],options["max"])
            if "title" in options: histo.GetYaxis().SetTitle(options["title"])
        if axis == "Z":
            if "min" in options and "max" in options: histo.GetZaxis().SetRangeUser(options["min"],options["max"])

def prettyHisto(histo,magicFactor=1.0,magicFactor2=1.0,color=ROOT.kBlack):

    histo.GetYaxis().SetLabelSize(magicFactor*0.055); histo.GetYaxis().SetTitleSize(magicFactor*0.08); histo.GetYaxis().SetTitleOffset(0.65/magicFactor)
    histo.GetXaxis().SetLabelSize(magicFactor*0.055); histo.GetXaxis().SetTitleSize(magicFactor*0.08); histo.GetXaxis().SetTitleOffset(0.53/magicFactor2)

    if "TH2" in histo.ClassName():
        histo.GetZaxis().SetLabelSize(magicFactor*0.055); histo.GetZaxis().SetTitleSize(magicFactor*0.06)

    if "TH1" in histo.ClassName():
        histo.Rebin(1)
        if histo.Integral() != 0: histo.Scale(1./histo.Integral())
        histo.SetLineWidth(4)
        histo.SetLineColor(color)

    if "THStack" in histo.ClassName() or "TH1" in histo.ClassName():
        histo.GetXaxis().SetRangeUser(0.23,2.98)

def prettyText(text, color, algoName, mean, stddev):

    text.SetFillColor(ROOT.kWhite);
    text.SetTextAlign(11)
    text.AddText(algoName)
    text.AddText("#mu = %3.2f"%(mean))
    text.AddText("#sigma = %3.2f"%(stddev))
    text.SetTextColor(color)

def prettyProfile(histo, name, color, markerStyle, pfa):

    p = histo.ProfileX("p_%s_%s"%(pfa,name), 1, -1, "")
    p.SetMarkerStyle(markerStyle)
    p.SetMarkerSize(2)
    p.SetLineWidth(2)
    p.SetMarkerColor(color)
    p.SetLineColor(color)
    p.Sumw2()

    return p

def fillMap(pfaKey, inRootDir, theMap):

    if inRootDir == "NULL": return

    theMap[pfaKey] = {}

    for histoFile in os.listdir(inRootDir):

       if ".root" not in histoFile: continue
       histoFile = ROOT.TFile.Open(inRootDir + histoFile, "READ")
       for hkey in histoFile.GetListOfKeys():
           if "TH" not in hkey.GetClassName(): continue

           name = hkey.GetName()
           histo = hkey.ReadObj()
           histo.SetDirectory(0)

           histo.Sumw2()
           
           if name in theMap[pfaKey].keys(): theMap[pfaKey][name].Add(histo)
           else: theMap[pfaKey][name] = histo

if __name__ == '__main__':

    # Figure out the stub to use for the output directory
    # If neither pfaX1 or pfaX2 have been specified then quit!
    if arg.pfaX1   != "NULL": stub = arg.pfaX1.split("Ratios/")[-1]
    elif arg.pfaX2 != "NULL": stub = arg.pfaX2.split("Ratios/")[-1]
    else: quit()

    tag = arg.tag

    # Save the input directories provided and fill the map of histos
    inRootDirs = {};  mapPFAhistos = {}
    inRootDirs["PFAY"]      = arg.pfaY;       fillMap("PFAY"     , inRootDirs["PFAY"]     , mapPFAhistos)
    inRootDirs["PFAX1"]     = arg.pfaX1;      fillMap("PFAX1"    , inRootDirs["PFAX1"]    , mapPFAhistos)
    inRootDirs["PFAX2"]     = arg.pfaX2;      fillMap("PFAX2"    , inRootDirs["PFAX2"]    , mapPFAhistos)
    inRootDirs["PFAYUp"]    = arg.pfaYUp;     fillMap("PFAYUp"   , inRootDirs["PFAYUp"]   , mapPFAhistos)
    inRootDirs["PFAX1Up"]   = arg.pfaX1Up;    fillMap("PFAX1Up"  , inRootDirs["PFAX1Up"]  , mapPFAhistos)
    inRootDirs["PFAX2Up"]   = arg.pfaX2Up;    fillMap("PFAX2Up"  , inRootDirs["PFAX2Up"]  , mapPFAhistos)
    inRootDirs["PFAYDown"]  = arg.pfaYDown;   fillMap("PFAYDown" , inRootDirs["PFAYDown"] , mapPFAhistos)
    inRootDirs["PFAX1Down"] = arg.pfaX1Down;  fillMap("PFAX1Down", inRootDirs["PFAX1Down"], mapPFAhistos)
    inRootDirs["PFAX2Down"] = arg.pfaX2Down;  fillMap("PFAX2Down", inRootDirs["PFAX2Down"], mapPFAhistos)
       
    # Set up the output directory and make it if it does not exist
    outpath = "./plots/Ratios/%s/%s"%(stub,tag)
    if not os.path.exists(outpath): os.makedirs(outpath)

    # Save the final histograms
    for name in mapPFAhistos.values()[0].keys():

        if "TH2" in mapPFAhistos.values()[0][name].ClassName():
            zMax = 0
            if "RHET" in name: zMax = 8e3
            else:              zMax = 5e3
            
            c1 = ROOT.TCanvas("%s"%(name), "%s"%(name), 2400, 1440); c1.cd(); c1.SetLogz()

            ROOT.gPad.SetTopMargin(0.02625)
            ROOT.gPad.SetBottomMargin(0.13375)
            ROOT.gPad.SetLeftMargin(0.11)
            ROOT.gPad.SetRightMargin(0.12)

            if "PFAX1" in mapPFAhistos:

                # If both and up and down variation of the TP/RH provided, make an uncertainty band 
                pPFAX1Up = 0; pPFAX1Down = 0; gPFAX1Up = 0; gPFAX1Down = 0; gPFAX1Band = 0
                if "PFAX1Up" in mapPFAhistos and "PFAX1Down" in mapPFAhistos:
                    pPFAX1Up   = prettyProfile(mapPFAhistos["PFAX1Up"][name]  , name, ROOT.kBlack, 20, "PFAX1Up")
                    pPFAX1Down = prettyProfile(mapPFAhistos["PFAX1Down"][name], name, ROOT.kBlack, 20, "PFAX1Down")

                    gPFAX1Up, gPFAX1Down, gPFAX1Band = makeBandGraph(pPFAX1Up, pPFAX1Down, ROOT.kBlack)
                   
                # Get nominal TP/RH profile
                pPFAX1 = prettyProfile(mapPFAhistos["PFAX1"][name], name, ROOT.kBlack, 20, "PFAX1")
                prettyHisto(mapPFAhistos["PFAX1"][name], 0.875, 0.6)

                # Set some visual options for the actual 2D TP/RH
                doOptions(mapPFAhistos["PFAX1"][name],name)
                mapPFAhistos["PFAX1"][name].SetContour(255)
                mapPFAhistos["PFAX1"][name].GetYaxis().SetRangeUser(0.1,2.)
                mapPFAhistos["PFAX1"][name].GetZaxis().SetRangeUser(1,zMax)
                mapPFAhistos["PFAX1"][name].Draw("COLZ")

                pPFAX1.Draw("EP SAME")

                if gPFAX1Up and gPFAX1Down and gPFAX1Band:
                    gPFAX1Band.Draw("F SAME")
                    gPFAX1Up.Draw("L SAME")
                    gPFAX1Down.Draw("L SAME")

            if "PFAX2" in mapPFAhistos:

                # If both and up and down variation of the TP/RH provided, make an uncertainty band 
                pPFAX2Up = 0; pPFAX2Down = 0; gPFAX2Up = 0; gPFAX2Down = 0; gPFAX2Band = 0
                if "PFAX2Up" in mapPFAhistos and "PFAX2Down" in mapPFAhistos:
                    pPFAX2Up   = prettyProfile(mapPFAhistos["PFAX2Up"][name]  , name, ROOT.kRed, 20, "PFAX2Up")
                    pPFAX2Down = prettyProfile(mapPFAhistos["PFAX2Down"][name], name, ROOT.kRed, 20, "PFAX2Down")

                    gPFAX2Up, gPFAX2Down, gPFAX2Band = makeBandGraph(pPFAX2Up, pPFAX2Down, ROOT.kRed)

                # Get nominal TP/RH profile
                pPFAX2 = prettyProfile(mapPFAhistos["PFAX2"][name], name, ROOT.kRed, 20, "PFAX2")
                prettyHisto(mapPFAhistos["PFAX2"][name], 0.875, 0.6)

                # Set some visual options for the actual 2D TP/RH
                doOptions(mapPFAhistos["PFAX2"][name],name)
                mapPFAhistos["PFAX2"][name].SetContour(255)
                mapPFAhistos["PFAX2"][name].GetYaxis().SetRangeUser(0.1,2.)
                mapPFAhistos["PFAX2"][name].GetZaxis().SetRangeUser(1,zMax)
                mapPFAhistos["PFAX2"][name].Draw("COLZ")

                pPFAX2.Draw("EP SAME")

                if gPFAX2Up and gPFAX2Down and gPFAX2Band:
                    gPFAX2Band.Draw("F SAME")
                    gPFAX2Up.Draw("L SAME")
                    gPFAX2Down.Draw("L SAME")

            if "PFAY" in mapPFAhistos:

                # If both and up and down variation of the TP/RH provided, make an uncertainty band 
                pPFAYUp = 0; pPFAYDown = 0; gPFAYUp = 0; gPFAYDown = 0; gPFAYBand = 0
                if "PFAYUp" in mapPFAhistos and "PFAYDown" in mapPFAhistos:
                    pPFAYUp   = prettyProfile(mapPFAhistos["PFAYUp"][name]  , name, ROOT.kBlack, 20, "PFAYUp")
                    pPFAYDown = prettyProfile(mapPFAhistos["PFAYDown"][name], name, ROOT.kBlack, 20, "PFAYDown")

                    gPFAYUp, gPFAYDown, gPFAYBand = makeBandGraph(pPFAYUp, pPFAYDown, ROOT.kBlack)

                # Get nominal TP/RH profile
                pPFAY = prettyProfile(mapPFAhistos["PFAY"][name], name, ROOT.kBlack, 4, "PFAY")
                prettyHisto(mapPFAhistos["PFAY"][name], 0.875, 0.6)

                doOptions(mapPFAhistos["PFAY"][name],name)

                pPFAY.Draw("EP SAME")

                if gPFAYUp and gPFAYDown and gPFAYBand:
                    gPFAYBand.Draw("F SAME")
                    gPFAYUp.Draw("L SAME")
                    gPFAYDown.Draw("L SAME")

            l = 0
            if name in OPTIONSMAP: l = ROOT.TLine(OPTIONSMAP[name]["X"]["min"]-mapPFAhistos.values()[0][name].GetXaxis().GetBinWidth(1)/1.75, 1, OPTIONSMAP[name]["X"]["max"]+mapPFAhistos.values()[0][name].GetXaxis().GetBinWidth(1)/1.75, 1)
            else: l = ROOT.TLine(-28, 1, 28, 1) 
            l.SetLineWidth(2)
            l.SetLineColor(ROOT.kBlack)
            l.SetLineStyle(2)
            l.Draw("SAME")

            c1.SaveAs("%s/%s.pdf"%(outpath,name))

        # 1D histos assumed to be a distribution of TP/RH for a given ieta
        elif "TH1" in mapPFAhistos.values()[0][name].ClassName():

            c1 = ROOT.TCanvas("%s"%(name), "%s"%(name), 1600, 1600); c1.cd(); c1.SetGridy(); c1.SetGridx()

            ROOT.gPad.SetTopMargin(0.02)
            ROOT.gPad.SetBottomMargin(0.12)
            ROOT.gPad.SetLeftMargin(0.11)
            ROOT.gPad.SetRightMargin(0.02)

            t_pfaX1 = 0; t_pfaX2 = 0; t_pfaY = 0
            theStack = ROOT.THStack("theStack_%s"%(name), ""); theStack.Draw()
            if "PFAX1" in mapPFAhistos:

                prettyHisto(mapPFAhistos["PFAX1"][name], 0.65, 0.5, ROOT.kBlack)
                theStack.Add(mapPFAhistos["PFAX1"][name])
                theStack.GetXaxis().SetTitle(mapPFAhistos["PFAX1"][name].GetXaxis().GetTitle())
                theStack.GetYaxis().SetTitle(mapPFAhistos["PFAX1"][name].GetYaxis().GetTitle())

                algoName = arg.pfaX1.split("/")[3]
                someTextPFAX1 = ROOT.TPaveText(0.75, 0.75, 0.95, 0.9, "trNDC")
                prettyText(someTextPFAX1, ROOT.kBlack, algoName, mapPFAhistos["PFAX1"][name].GetMean(), mapPFAhistos["PFAX1"][name].GetStdDev())
                t_pfaX1 = someTextPFAX1

            if "PFAY" in mapPFAhistos:

                prettyHisto(mapPFAhistos["PFAY"][name], 0.65, 0.5, ROOT.kGray+2)
                theStack.Add(mapPFAhistos["PFAY"][name])
                theStack.GetXaxis().SetTitle(mapPFAhistos["PFAY"][name].GetXaxis().GetTitle())
                theStack.GetYaxis().SetTitle(mapPFAhistos["PFAY"][name].GetYaxis().GetTitle())

                algoName = arg.pfaY.split("/")[3]
                someTextPFAY = ROOT.TPaveText(0.75, 0.39, 0.95, 0.54, "trNDC")
                prettyText(someTextPFAY, ROOT.kGray+2, algoName, mapPFAhistos["PFAY"][name].GetMean(), mapPFAhistos["PFAY"][name].GetStdDev())
                t_pfaY = someTextPFAY

            if "PFAX2" in mapPFAhistos:

                prettyHisto(mapPFAhistos["PFAX2"][name], 0.65, 0.5, ROOT.kRed)
                theStack.Add(mapPFAhistos["PFAX2"][name])
                theStack.GetXaxis().SetTitle(mapPFAhistos["PFAX2"][name].GetXaxis().GetTitle())
                theStack.GetYaxis().SetTitle(mapPFAhistos["PFAX2"][name].GetYaxis().GetTitle())

                algoName = arg.pfaX2.split("/")[3]
                someTextPFAX2 = ROOT.TPaveText(0.75, 0.57, 0.95, 0.72, "trNDC")
                prettyText(someTextPFAX2, ROOT.kRed, algoName, mapPFAhistos["PFAX2"][name].GetMean(), mapPFAhistos["PFAX2"][name].GetStdDev())
                t_pfaX2 = someTextPFAX2

            prettyHisto(theStack, 0.65, 0.5)
            theStack.Draw("HISTO NOSTACK")

            if t_pfaX1 != 0: t_pfaX1.Draw("SAME")
            if t_pfaX2 != 0: t_pfaX2.Draw("SAME")
            if t_pfaY  != 0: t_pfaY.Draw("SAME")

            c1.SaveAs("%s/%s.pdf"%(outpath,name))
