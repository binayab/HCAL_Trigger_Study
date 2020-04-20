# The finalClosurePlots script extracts the raw 2D histograms made by the closureStudyPlotter script
# and puts them into final presentable form. An example call would be:
# python studies/finalClosurePlots.py --tag someTag --pfaY subpath/to/nominal --pfaX1 subpath/to/new

import sys, os, ROOT, argparse

ROOT.TH1.SetDefaultSumw2()
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetPaintTextFormat("3.2f")
ROOT.gStyle.SetFrameLineWidth(2)
ROOT.gStyle.SetErrorX(0)

def prettyHisto(histo, xLabelSize, yLabelSize, zLabelSize, xTitleSize, yTitleSize, zTitleSize, xOffset, yOffset, zOffset,color=ROOT.kBlack, special=True):

    histo.GetYaxis().SetLabelSize(yLabelSize); histo.GetYaxis().SetTitleSize(yTitleSize); histo.GetYaxis().SetTitleOffset(yOffset)
    histo.GetXaxis().SetLabelSize(xLabelSize); histo.GetXaxis().SetTitleSize(xTitleSize); histo.GetXaxis().SetTitleOffset(xOffset)

    if special:
        if "TH2" in histo.ClassName():
            histo.GetZaxis().SetLabelSize(zLabelSize); histo.GetZaxis().SetTitleSize(zTitleSize)

        if "TH1" in histo.ClassName():
            histo.Rebin(1)
            if histo.Integral() != 0: histo.Scale(1./histo.Integral())
            histo.SetLineWidth(4)
            histo.SetLineColor(color)

        if "THStack" in histo.ClassName() or "TH1" in histo.ClassName():
            histo.GetXaxis().SetRangeUser(0.23,2.98)

def prettyProfile(histo, name, color, markerStyle, pfa):

    firstyBin = 1; option = ""
    if "ETCorr" in name:
        firstyBin = 2
        option = "s"

    p = histo.ProfileX("p_%s_%s"%(pfa,name), firstyBin, -1, option)
    p.SetMarkerStyle(markerStyle)
    p.SetMarkerSize(3)
    p.SetLineWidth(3)
    p.SetMarkerColor(color)
    p.SetLineColor(color)
    p.Sumw2()

    return p

def fillMap(pfaKey, inRootDir):

    if "NULL" in inRootDir: return

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

def draw2DHistoAndProfile(canvas, keyName, histoName, zMax, color, markerStyle, line, drewRatio):

    canvas.cd()

    theHisto = MAPPFAHISTOS[keyName][histoName]

    pPFAX = prettyProfile(theHisto, histoName, color, markerStyle, keyName)

    if "ETCorr" in histoName: prettyHisto(theHisto, 0.050, 0.050, 0.050, 0.055, 0.055, 0.055, 1.0, 1.2, 1.0)
    else:                     prettyHisto(theHisto, 0.059, 0.059, 0.059, 0.072, 0.072, 0.072, 0.85, 0.72, 1.0)

    # Set some visual options for the actual 2D TP/RH
    if not drewRatio:
        theHisto.SetContour(255)

        if "ETCorr" in histoName:
            theHisto.GetXaxis().SetRangeUser(-0.25,20.25)
            theHisto.GetYaxis().SetRangeUser(-0.25,20.25)

            theHisto.GetXaxis().SetTitle("TP E_{T} [GeV] (t#bar{t}+0PU)")
            theHisto.GetYaxis().SetTitle("TP E_{T} [GeV] (t#bar{t}+OOTPU)")
        else: 
            theHisto.GetYaxis().SetRangeUser(0.1,2.)

        theHisto.GetZaxis().SetRangeUser(1,zMax)
        theHisto.Draw("COLZ")
        drewRatio = True
    
    # Sneak the line in so the profile is draw on top
    line.Draw("SAME")
    pPFAX.Draw("EP SAME")

    return drewRatio

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--tag"      , dest="tag"      , type=str, default=""    , help="Unique tag for output")
    parser.add_argument("--pfaY"     , dest="pfaY"     , type=str, default="NULL", help="Path to inputs for PFAY")
    parser.add_argument("--pfaX1"    , dest="pfaX1"    , type=str, default="NULL", help="Path to other PFAX dir") 
    parser.add_argument("--pfaX2"    , dest="pfaX2"    , type=str, default="NULL", help="Path to other PFAX dir") 
    args = parser.parse_args()
    
    MAPPFAHISTOS = {}

    # Figure out the stub to use for the output directory
    # If neither pfaX1 or pfaX2 have been specified then quit!
    # The subtlety here is that pfaX1 takes precedence for the output directory
    if   args.pfaX1 != "NULL": stub = args.pfaX1.split("Closure/")[-1]
    elif args.pfaX2 != "NULL": stub = args.pfaX2.split("Closure/")[-1]
    else: quit()

    tag = args.tag

    HOME = os.getenv("HOME")
    OUTBASE = "%s/nobackup/HCAL_Trigger_Study/plots/Closure"%(HOME)
    INPUTLOC = "%s/nobackup/HCAL_Trigger_Study/input/Closure"%(HOME)

    # Save the input directories provided and fill the map of histos
    fillMap("PFAY" , INPUTLOC + "/" + args.pfaY)
    fillMap("PFAX1", INPUTLOC + "/" + args.pfaX1)
    fillMap("PFAX2", INPUTLOC + "/" + args.pfaX2)

    # Set up the output directory and make it if it does not exist
    outpath = "%s/%s/%s"%(OUTBASE,stub,tag)
    if not os.path.exists(outpath): os.makedirs(outpath)

    # Save the final histograms
    for name in MAPPFAHISTOS.values()[0].keys():

        className = MAPPFAHISTOS.values()[0][name].ClassName()

        if "TH2" in className:
            zMax = 2e3 
            
            c1 = 0; line = 0
            if "ETCorr" in name:

                c1 = ROOT.TCanvas("%s"%(name), "%s"%(name), 1600, 1440); c1.cd(); c1.SetLogz()

                ROOT.gPad.SetTopMargin(0.026)
                ROOT.gPad.SetBottomMargin(0.13)
                ROOT.gPad.SetLeftMargin(0.13)
                ROOT.gPad.SetRightMargin(0.14)

                ROOT.gPad.SetGridx()
                ROOT.gPad.SetGridy()

                line = ROOT.TLine(-0.25, -0.25, 20.65, 20.65) 

            else:

                c1 = ROOT.TCanvas("%s"%(name), "%s"%(name), 2400, 1440); c1.cd(); c1.SetLogz()

                ROOT.gPad.SetTopMargin(0.02625)
                ROOT.gPad.SetBottomMargin(0.13375)
                ROOT.gPad.SetLeftMargin(0.11)
                ROOT.gPad.SetRightMargin(0.12)

                line = ROOT.TLine(-28, 1, 28, 1) 

            line.SetLineWidth(7)
            line.SetLineColor(ROOT.kBlack)
            line.SetLineStyle(7)

            drewRatio = False
            if "PFAX1" in MAPPFAHISTOS: drewRatio = draw2DHistoAndProfile(c1, "PFAX1", name, zMax, ROOT.kBlack  , 20, line, drewRatio)
            if "PFAX2" in MAPPFAHISTOS: drewRatio = draw2DHistoAndProfile(c1, "PFAX2", name, zMax, ROOT.kPink+10, 20, line, drewRatio)
            if "PFAY"  in MAPPFAHISTOS: drewRatio = draw2DHistoAndProfile(c1, "PFAY" , name, zMax, ROOT.kBlack  , 4,  line, drewRatio)

            ietaList = name.split("ieta")[-1].split("to")
            ietaStr = ""
            if len(ietaList) > 1: ietaStr = "%s to %s"%(ietaList[0],ietaList[1])
            else:                 ietaStr = "%s"%(ietaList[0])

            ietaText = ROOT.TPaveText(0.20, 0.86, 0.40, 0.95, "trNDC")
            ietaText.SetFillColor(ROOT.kWhite); ietaText.SetTextAlign(11); ietaText.SetTextFont(63); ietaText.SetTextSize(90)
            ietaText.AddText("|i#eta| = %s"%(ietaStr))

            ietaText.Draw("SAME")

            c1.SaveAs("%s/%s.pdf"%(outpath,name))
