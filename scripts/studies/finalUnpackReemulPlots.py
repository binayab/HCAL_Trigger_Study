import sys, os, ROOT, argparse

ROOT.TH1.SetDefaultSumw2()
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetPaintTextFormat("3.2f")
ROOT.gStyle.SetFrameLineWidth(2)
ROOT.gStyle.SetErrorX(0)

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

def prettyHisto(histo, xLabelSize, yLabelSize, zLabelSize, xTitleSize, yTitleSize, zTitleSize, xOffset, yOffset, zOffset,color=ROOT.kBlack):

    histo.GetYaxis().SetLabelSize(yLabelSize); histo.GetYaxis().SetTitleSize(yTitleSize); histo.GetYaxis().SetTitleOffset(yOffset)
    histo.GetXaxis().SetLabelSize(xLabelSize); histo.GetXaxis().SetTitleSize(xTitleSize); histo.GetXaxis().SetTitleOffset(xOffset)

    if "TH2" in histo.ClassName():
        histo.GetZaxis().SetLabelSize(zLabelSize); histo.GetZaxis().SetTitleSize(zTitleSize)

def prettyProfile(histo, name, color, markerStyle, pfa):

    p = histo.ProfileX("p_%s_%s"%(pfa,name), 1, -1, "")
    p.SetMarkerStyle(markerStyle)
    p.SetMarkerSize(2)
    p.SetLineWidth(2)
    p.SetMarkerColor(color)
    p.SetLineColor(color)
    p.Sumw2()

    return p

def fillMap(pfaKey, inRootDir):

    if inRootDir == "NULL": return

    MAPPFAHISTOS[pfaKey] = {}

    for histoFile in os.listdir(inRootDir):

       if ".root" not in histoFile: continue
       histoFile = ROOT.TFile.Open(inRootDir + "/" + histoFile, "READ")
       for hkey in histoFile.GetListOfKeys():
           if "TH" not in hkey.GetClassName(): continue

           name = hkey.GetName()
           histo = hkey.ReadObj()
           histo.SetDirectory(0)

           histo.Sumw2()
           
           if name in MAPPFAHISTOS[pfaKey].keys(): MAPPFAHISTOS[pfaKey][name].Add(histo)
           else: MAPPFAHISTOS[pfaKey][name] = histo

def draw2DHistoAndProfile(canvas, keyName, histoName, zMax, color, markerStyle):

    canvas.cd()

    # Get nominal TP/RH profile
    theHisto = MAPPFAHISTOS[keyName][histoName]

    prof = prettyProfile(theHisto, histoName, color, markerStyle, keyName)
    prettyHisto(theHisto, 0.059, 0.059, 0.059, 0.072, 0.072, 0.072, 0.85, 0.72, 1.0)

    # Set some visual options for the actual 2D TP/RH
    #doOptions(theHisto, histoName)
    theHisto.SetContour(255)
    theHisto.GetYaxis().SetRangeUser(0.1,2.)
    theHisto.GetZaxis().SetRangeUser(1,zMax)
    theHisto.Draw("COLZ")

    prof.Draw("EP SAME")

def draw2DHisto(canvas, keyName, histoName, zMax):

    canvas.cd()

    # Get nominal TP/RH profile
    theHisto = MAPPFAHISTOS[keyName][histoName]
    prettyHisto(theHisto, 0.045, 0.045, 0.045, 0.055, 0.055, 0.055, 1.0, 1.2, 1.0)

    doOptions(theHisto, histoName)
    theHisto.SetContour(255)
    theHisto.GetZaxis().SetRangeUser(1,zMax)
    theHisto.Draw("COLZ")

    l = ROOT.TLine(0, 0, 20, 20) 
    l.SetLineWidth(2)
    l.SetLineColor(ROOT.kBlack)
    l.SetLineStyle(2)
    l.Draw("SAME")

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--tag"      , dest="tag"      , type=str, default=""    , help="Unique tag for output")
    parser.add_argument("--inputDir" , dest="inputDir" , type=str, default="NULL", help="Path to inputs")
    args = parser.parse_args()
    
    OPTIONSMAP = {"UnpackReemul_vs_ET_ieta1"  : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta2"  : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta3"  : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta4"  : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta5"  : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta6"  : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta7"  : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta8"  : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta9"  : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta10" : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta11" : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta12" : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta13" : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta14" : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta15" : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta16" : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta17" : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta18" : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta19" : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta20" : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta21" : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta22" : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta23" : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta24" : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta25" : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta26" : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta27" : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}},
                  "UnpackReemul_vs_ET_ieta28" : {"X" : {"min" : 0, "max" : 20}, "Y" : {"min" : 0, "max" : 20}}}

    MAPPFAHISTOS = {}

    # Figure out the stub to use for the output directory
    # If input has not been specified then quit!
    if   args.inputDir != "NULL": stub = args.inputDir.split("Ratios/")[-1]
    else: quit()

    tag = args.tag

    # Save the input directories provided and fill the map of histos
    fillMap("input" , args.inputDir)

    # Set up the output directory and make it if it does not exist
    outpath = "./plots/UnpackReemul/%s/%s"%(stub,tag)
    if not os.path.exists(outpath): os.makedirs(outpath)

    # Save the final histograms
    for key,histo in MAPPFAHISTOS["input"].iteritems():

        zMax = 8e6

        if "vs_Eta" in key: 

            c1 = ROOT.TCanvas("%s"%(key), "%s"%(key), 2400, 1440); c1.cd(); c1.SetLogz()

            ROOT.gPad.SetTopMargin(0.02625)
            ROOT.gPad.SetBottomMargin(0.13375)
            ROOT.gPad.SetLeftMargin(0.11)
            ROOT.gPad.SetRightMargin(0.12)

            draw2DHistoAndProfile(c1, "input", key, zMax, ROOT.kBlack, 20)
    
            l = ROOT.TLine(-28, 1, 28, 1) 
            l.SetLineWidth(2)
            l.SetLineColor(ROOT.kBlack)
            l.SetLineStyle(2)
            l.Draw("SAME")

            c1.SaveAs("%s/%s.pdf"%(outpath,key))

        elif "vs_ET" in key:

            c1 = ROOT.TCanvas("%s"%(key), "%s"%(key), 2700, 2400); c1.cd(); c1.SetLogz()

            ROOT.gPad.SetTopMargin(0.025)
            ROOT.gPad.SetBottomMargin(0.12)
            ROOT.gPad.SetLeftMargin(0.14)
            ROOT.gPad.SetRightMargin(0.12)

            draw2DHisto(c1, "input", key, zMax)

            c1.SaveAs("%s/%s.pdf"%(outpath,key))
