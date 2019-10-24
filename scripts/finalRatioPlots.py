import sys, os, ROOT, argparse

ROOT.TH1.SetDefaultSumw2()
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetLineWidth(2)
ROOT.gStyle.SetPaintTextFormat("3.2f")
ROOT.gStyle.SetFrameLineWidth(2)
ROOT.gStyle.SetErrorX(0)

usage = "usage: %prog [options]"
parser = argparse.ArgumentParser(usage)
parser.add_argument("--tag"     , dest="tag"     , help="Unique tag for output"    , type=str, default="")
parser.add_argument("--pfaY", dest="pfaY", type=str, help="Path to inputs for PFAY", default="NULL")
parser.add_argument("--pfaX1", dest="pfaX1", help="Path to other PFAX dir", default="NULL", type=str) 
parser.add_argument("--pfaX2", dest="pfaX2", help="Path to other PFAX dir", default="NULL", type=str) 

arg = parser.parse_args()

OPTIONSMAP = {"TPRH_TPET" : {"X" : {"min" : 0.5, "max" : 20}, "Y" : {"min" : 0.2, "max" : 2}},
              "TPRH_RHET" : {"X" : {"min" : 0.5, "max" : 20}, "Y" : {"min" : 0.2, "max" : 2}}}

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
        histo.Scale(1./histo.Integral())
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

    XCANVAS = 2400; YCANVAS = 1800

    if arg.pfaX1 != "NULL": stub = arg.pfaX1.split("Ratios/")[-1]
    elif arg.pfaX2 != "NULL": stub = arg.pfaX2.split("Ratios/")[-1]
    else: quit()

    tag = arg.tag

    inRootDirs = {}
    inRootDirs["PFAY"] = arg.pfaY
    inRootDirs["PFAX1"] = arg.pfaX1
    inRootDirs["PFAX2"] = arg.pfaX2
       
    outpath = "./plots/Ratios/%s/%s"%(stub,tag)
    if not os.path.exists(outpath): os.makedirs(outpath)

    mapPFAhistos = {}

    fillMap("PFAY",  inRootDirs["PFAY"],  mapPFAhistos)
    fillMap("PFAX1", inRootDirs["PFAX1"], mapPFAhistos)
    fillMap("PFAX2", inRootDirs["PFAX2"], mapPFAhistos)

    # Save the final histograms
    for name in mapPFAhistos.values()[0].keys():

        if "TH2" in mapPFAhistos.values()[0][name].ClassName():
            zMax = 0
            if "RHET" in name: zMax = 8e3
            else: zMax = 5e3
            
            c1 = ROOT.TCanvas("%s"%(name), "%s"%(name), XCANVAS, int(0.8*YCANVAS)); c1.cd(); c1.SetLogz()

            ROOT.gPad.SetTopMargin(0.02625)
            ROOT.gPad.SetBottomMargin(0.13375)
            ROOT.gPad.SetLeftMargin(0.11)
            ROOT.gPad.SetRightMargin(0.12)

            drewRatio = False
            xMax = 0; xMin = 0
            if "PFAX1" in mapPFAhistos:
                pPFAX1 = prettyProfile(mapPFAhistos["PFAX1"][name],name,ROOT.kBlack,20,"PFAX1")
                prettyHisto(mapPFAhistos["PFAX1"][name],0.875,0.6)
                if not drewRatio:
                    doOptions(mapPFAhistos["PFAX1"][name],name)
                    mapPFAhistos["PFAX1"][name].SetContour(255)
                    mapPFAhistos["PFAX1"][name].GetYaxis().SetRangeUser(0.1,2.)
                    mapPFAhistos["PFAX1"][name].GetZaxis().SetRangeUser(1,zMax)
                    mapPFAhistos["PFAX1"][name].Draw("COLZ")
                    drewRatio = True
                pPFAX1.Draw("EP SAME")
            if "PFAX2" in mapPFAhistos:
                pPFAX2 = prettyProfile(mapPFAhistos["PFAX2"][name],name,ROOT.kRed,20,"PFAX2")
                prettyHisto(mapPFAhistos["PFAX2"][name],0.875,0.6)
                if not drewRatio:
                    doOptions(mapPFAhistos["PFAX2"][name],name)
                    mapPFAhistos["PFAX2"][name].SetContour(255)
                    mapPFAhistos["PFAX2"][name].GetYaxis().SetRangeUser(0.1,2.)
                    mapPFAhistos["PFAX2"][name].GetZaxis().SetRangeUser(1,zMax)
                    mapPFAhistos["PFAX2"][name].Draw("COLZ")
                    drewRatio = True
                pPFAX2.Draw("EP SAME")
            if "PFAY" in mapPFAhistos:
                doOptions(mapPFAhistos["PFAY"][name],name)
                prettyHisto(mapPFAhistos["PFAY"][name],0.875,0.6)
                pPFAY = prettyProfile(mapPFAhistos["PFAY"][name],name,ROOT.kBlack,4,"PFAY")
                pPFAY.Draw("EP SAME")

            l = 0
            if name in OPTIONSMAP: l = ROOT.TLine(OPTIONSMAP[name]["X"]["min"]-mapPFAhistos.values()[0][name].GetXaxis().GetBinWidth(1)/1.75, 1, OPTIONSMAP[name]["X"]["max"]+mapPFAhistos.values()[0][name].GetXaxis().GetBinWidth(1)/1.75, 1)
            else: l = ROOT.TLine(-28, 1, 28, 1) 
            l.SetLineWidth(2)
            l.SetLineColor(ROOT.kBlack)
            l.SetLineStyle(2)
            l.Draw("SAME")

            c1.SaveAs("%s/%s.pdf"%(outpath,name))

        elif "TH1" in mapPFAhistos.values()[0][name].ClassName():

            c1 = ROOT.TCanvas("%s"%(name), "%s"%(name), 1600, 1600); c1.cd()
            c1.SetGridy(); c1.SetGridx()
            ROOT.gPad.SetTopMargin(0.02)
            ROOT.gPad.SetBottomMargin(0.12)
            ROOT.gPad.SetLeftMargin(0.11)
            ROOT.gPad.SetRightMargin(0.02)

            t_pfaX1 = 0; t_pfaX2 = 0; t_pfaY = 0
            theStack = ROOT.THStack("theStack", ""); theStack.Draw()
            if "PFAX1" in mapPFAhistos:

                maximum = mapPFAhistos["PFAX1"][name].GetMaximum()

                prettyHisto(mapPFAhistos["PFAX1"][name],0.65,0.5,ROOT.kBlack)
                theStack.Add(mapPFAhistos["PFAX1"][name])
                theStack.GetXaxis().SetTitle(mapPFAhistos["PFAX1"][name].GetXaxis().GetTitle())
                theStack.GetYaxis().SetTitle(mapPFAhistos["PFAX1"][name].GetYaxis().GetTitle())

                algoName = arg.pfaX1.split("/")[3]
                someTextPFAX1 = ROOT.TPaveText(0.75, 0.75, 0.95, 0.9, "trNDC")
                prettyText(someTextPFAX1, ROOT.kBlack, algoName, mapPFAhistos["PFAX1"][name].GetMean(), mapPFAhistos["PFAX1"][name].GetStdDev())
                t_pfaX1 = someTextPFAX1

            if "PFAY" in mapPFAhistos:

                prettyHisto(mapPFAhistos["PFAY"][name],0.65,0.5,ROOT.kGray+2)
                theStack.Add(mapPFAhistos["PFAY"][name])
                theStack.GetXaxis().SetTitle(mapPFAhistos["PFAY"][name].GetXaxis().GetTitle())
                theStack.GetYaxis().SetTitle(mapPFAhistos["PFAY"][name].GetYaxis().GetTitle())

                algoName = arg.pfaY.split("/")[3]
                someTextPFAY = ROOT.TPaveText(0.75, 0.39, 0.95, 0.54, "trNDC")
                prettyText(someTextPFAY, ROOT.kGray+2, algoName, mapPFAhistos["PFAY"][name].GetMean(), mapPFAhistos["PFAY"][name].GetStdDev())
                t_pfaY = someTextPFAY

            if "PFAX2" in mapPFAhistos:

                prettyHisto(mapPFAhistos["PFAX2"][name],0.65,0.5,ROOT.kRed)
                theStack.Add(mapPFAhistos["PFAX2"][name])
                theStack.GetXaxis().SetTitle(mapPFAhistos["PFAX2"][name].GetXaxis().GetTitle())
                theStack.GetYaxis().SetTitle(mapPFAhistos["PFAX2"][name].GetYaxis().GetTitle())

                algoName = arg.pfaX2.split("/")[3]
                someTextPFAX2 = ROOT.TPaveText(0.75, 0.57, 0.95, 0.72, "trNDC")
                prettyText(someTextPFAX2, ROOT.kRed, algoName, mapPFAhistos["PFAX2"][name].GetMean(), mapPFAhistos["PFAX2"][name].GetStdDev())
                t_pfaX2 = someTextPFAX2

            prettyHisto(theStack, 0.65,0.5)
            theStack.Draw("HISTO NOSTACK")

            if t_pfaX1 != 0: t_pfaX1.Draw("SAME")
            if t_pfaX2 != 0: t_pfaX2.Draw("SAME")
            if t_pfaY != 0: t_pfaY.Draw("SAME")

            c1.SaveAs("%s/%s.pdf"%(outpath,name))
