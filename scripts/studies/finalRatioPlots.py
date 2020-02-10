# Pull raw histograms from root files and make final output

# An example call would be:
# python studies/finalRatioPlots.py --pfaY subpath/to/nominal --pfaX1 subpath/to/new

# Here the subpath is assumed to start in nobackup/HCAL_Trigger_Study/input/Ratios/

import sys, os, ROOT, argparse

ROOT.TH1.SetDefaultSumw2()
ROOT.TH2.SetDefaultSumw2()
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetPaintTextFormat("3.2f")
ROOT.gStyle.SetFrameLineWidth(2)
ROOT.gStyle.SetEndErrorSize(0)

# The makeBandGraph method takes three TH1s where histoUp and histoDown
# would make an envelope around histoNominal. An optional color for the 
# band is passable
def makeBandGraph(histoUp, histoDown, histoNominal, color):
    
    npoints = histoUp.GetNbinsX()

    graphUp   = ROOT.TGraph(npoints)
    graphDown = ROOT.TGraph(npoints)
    graphBand = ROOT.TGraph(2*npoints)

    for iPoint in xrange(0, npoints):

        # Sweet hack for bin 29 or iPoint == 28, interpolate from surrounding bins
        if iPoint == 28: 
            graphUp.SetPoint(iPoint,   histoUp.GetBinCenter(iPoint+1), (histoNominal.GetBinContent(iPoint)+histoNominal.GetBinContent(iPoint+2))/2)
            graphDown.SetPoint(iPoint, histoDown.GetBinCenter(iPoint+1), (histoNominal.GetBinContent(iPoint)+histoNominal.GetBinContent(iPoint+2))/2)

            graphBand.SetPoint(iPoint,         histoUp.GetBinCenter(iPoint+1),       (histoNominal.GetBinContent(iPoint)+histoNominal.GetBinContent(iPoint+2))/2)
            graphBand.SetPoint(npoints+iPoint, histoUp.GetBinCenter(npoints-iPoint), (histoNominal.GetBinContent(npoints-iPoint-1)+histoNominal.GetBinContent(npoints-iPoint+1))/2)

        else:
            graphUp.SetPoint(iPoint,   histoUp.GetBinCenter(iPoint+1), histoUp.GetBinContent(iPoint+1))
            graphDown.SetPoint(iPoint, histoUp.GetBinCenter(iPoint+1), histoDown.GetBinContent(iPoint+1))

            graphBand.SetPoint(iPoint,         histoUp.GetBinCenter(iPoint+1),       histoUp.GetBinContent(iPoint+1))
            graphBand.SetPoint(npoints+iPoint, histoUp.GetBinCenter(npoints-iPoint), histoDown.GetBinContent(npoints-iPoint))

    graphUp.SetLineWidth(2);   graphUp.SetLineColorAlpha(color, 0.25)
    graphDown.SetLineWidth(2); graphDown.SetLineColorAlpha(color, 0.25)
    graphBand.SetFillColorAlpha(color, 0.30)

    return graphUp, graphDown, graphBand

# The doOptions method takes a histo and its histoName and looks in the global OPIONSMAP
# to see if there are any special options to be done for the histo (axis titles, etc)
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

# The prettyHisto method takes an input histogram and axis label sizes (x,y,z); title label sizes (x,y,z); title offsets (x,y,z) and a color
def prettyHisto(histo, xLabelSize, yLabelSize, zLabelSize, xTitleSize, yTitleSize, zTitleSize, xOffset, yOffset, zOffset, color=ROOT.kBlack, lineStyle=1, special=True):

    histo.GetYaxis().SetLabelSize(yLabelSize); histo.GetYaxis().SetTitleSize(yTitleSize); histo.GetYaxis().SetTitleOffset(yOffset)
    histo.GetXaxis().SetLabelSize(xLabelSize); histo.GetXaxis().SetTitleSize(xTitleSize); histo.GetXaxis().SetTitleOffset(xOffset)

    if special:
        if "TH2" in histo.ClassName():
            histo.GetZaxis().SetLabelSize(zLabelSize); histo.GetZaxis().SetTitleSize(zTitleSize)

        if "TH1" in histo.ClassName():
            histo.Rebin(1)
            if histo.Integral() != 0: histo.Scale(1./histo.Integral())
            histo.SetLineWidth(5)
            histo.SetLineStyle(lineStyle)
            histo.SetLineColor(color)

        if "THStack" in histo.ClassName() or "TH1" in histo.ClassName():
            histo.GetXaxis().SetRangeUser(0.23,2.98)

# The prettyText method takes in a TPaveText object and strings to add
# to the text with a specific color
def prettyText(text, color, algoName, mean, stddev):

    text.SetFillColor(ROOT.kWhite);
    text.SetTextAlign(11)
    text.AddText(algoName)
    text.AddText("#mu = %3.2f"%(mean))
    text.AddText("#sigma = %3.2f"%(stddev))
    text.SetTextColor(color)

# The prettyProfile method takes in a TH2 histogram with some customization 
# parameters and makes a profile along the x-axis
def prettyProfile(histo, name, color, markerStyle, pfa):

    p = histo.ProfileX("p_%s_%s"%(pfa,name), 1, -1, "")
    p.SetMarkerStyle(markerStyle)
    p.SetMarkerSize(3)
    p.SetLineWidth(2)
    p.SetMarkerColor(color)
    p.SetLineColor(color)
    p.Sumw2()

    return p

# The fillMap method has inputs pfaKey which will be a key in a dictionary and inRootDir which is a path to 
# histogram files
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
           ROOT.SetOwnership(histo, False)

           histo.Sumw2()
           
           if name in MAPPFAHISTOS[pfaKey].keys(): MAPPFAHISTOS[pfaKey][name].Add(histo)
           else: MAPPFAHISTOS[pfaKey][name] = histo

# The draw2DHistoAndProfile takes in a host canvas, a key to a dictionary, a histogram name
# and some histogram style options. Using the key and histogram name, the method pulls the 2D
# histo from the master dictionary MAPPFAHISTOS. From there a profile is made from the 2D.
# The 2D and profile make a little prettier and the error band around the profile is drawn if requested
def draw2DHistoAndProfile(canvas, keyName, histoName, zMax, color, markerStyle, drewRatio, drawErrorBand):

    canvas.cd()

    # Get nominal TP/RH profile
    theHisto = MAPPFAHISTOS[keyName][histoName]

    pPFAX = prettyProfile(theHisto, histoName, color, markerStyle, keyName)
    prettyHisto(theHisto, 0.059, 0.059, 0.059, 0.072, 0.072, 0.072, 0.85, 0.72, 1.0)

    # Set some visual options for the actual 2D TP/RH
    if not drewRatio:
        doOptions(theHisto, histoName)
        theHisto.SetContour(255)
        theHisto.GetYaxis().SetRangeUser(0.1,2.)
        theHisto.GetZaxis().SetRangeUser(1,zMax)
        theHisto.Draw("COLZ")
        drewRatio = True

    pPFAX.Draw("EP SAME")

    # If both and up and down variation of the TP/RH provided, make an uncertainty band 
    if drawErrorBand:
        keyNameUp = keyName + "Up"; keyNameDown = keyName + "Down"
        pPFAXUp = 0; pPFAXDown = 0; gPFAXUp = 0; gPFAXDown = 0; gPFAXBand = 0
        if keyNameUp in MAPPFAHISTOS and keyNameDown in MAPPFAHISTOS:
            pPFAXUp   = prettyProfile(MAPPFAHISTOS[keyNameUp][name]  , name, color, markerStyle, keyNameUp)
            pPFAXDown = prettyProfile(MAPPFAHISTOS[keyNameDown][name], name, color, markerStyle, keyNameDown)

            gPFAXUp, gPFAXDown, gPFAXBand = makeBandGraph(pPFAXUp, pPFAXDown, pPFAX, color)
           
        if gPFAXUp and gPFAXDown and gPFAXBand:
            ROOT.SetOwnership(gPFAXBand, False)
            gPFAXBand.Draw("F")

    return drewRatio

# The method for 1D histos is the draw1DHisto method. Here the 1D histogram
# is prettied up and added to a THStack. In addition, we use parameters of the 1D
# histogram to make a custom TPaveText and return it.
def draw1DHisto(theStack, keyName, histoName, algoName, color, lineStyle, x1, y1, x2, y2):

    theHisto = MAPPFAHISTOS[keyName][histoName]

    mean = theHisto.GetMean()
    stddev = theHisto.GetStdDev()

    prettyHisto(theHisto, 0.042, 0.042, 0.042, 0.052, 0.052, 0.052, 1.06, 1.2, 1.0, color, lineStyle)
    theStack.Add(theHisto)
    theStack.GetXaxis().SetTitle(theHisto.GetXaxis().GetTitle())
    theStack.GetYaxis().SetTitle(theHisto.GetYaxis().GetTitle())

    someTextPFAX = ROOT.TPaveText(x1, y1, x2, y2, "trNDC")
    prettyText(someTextPFAX, color, algoName, mean, stddev)

    return someTextPFAX, stddev, mean

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--tag"      , dest="tag"      , type=str, default=""    , help="Unique tag for output")
    parser.add_argument("--pfaY"     , dest="pfaY"     , type=str, default="NULL", help="Subpath to inputs for PFAY")
    parser.add_argument("--pfaX1"    , dest="pfaX1"    , type=str, default="NULL", help="Subpath to other PFAX dir") 
    parser.add_argument("--pfaX2"    , dest="pfaX2"    , type=str, default="NULL", help="Subpath to other PFAX dir") 
    parser.add_argument("--pfaX1Err" , dest="pfaX1Err" , default=False, action="store_true", help="Draw error bands for PFAX") 
    parser.add_argument("--pfaX2Err" , dest="pfaX2Err" , default=False, action="store_true", help="Draw error bands for PFAX") 
    args = parser.parse_args()

    tag = args.tag
    
    OPTIONSMAP = {}
    MAPPFAHISTOS = {}

    # Figure out the stub to use for the output directory
    # If neither pfaX1 or pfaX2 have been specified then quit!
    if   args.pfaX1 != "NULL": stub = args.pfaX1.split("Ratios/")[-1]
    elif args.pfaX2 != "NULL": stub = args.pfaX2.split("Ratios/")[-1]
    else: quit()

    HOME = os.getenv("HOME")
    OUTBASE = "%s/nobackup/HCAL_Trigger_Study/plots/Ratios"%(HOME)
    INPUTLOC = "%s/nobackup/HCAL_Trigger_Study/input/Ratios"%(HOME)

    # Save the input directories provided and fill the map of histos
    fillMap("PFAY" , INPUTLOC + "/" + args.pfaY)
    fillMap("PFAX1", INPUTLOC + "/" + args.pfaX1)
    fillMap("PFAX2", INPUTLOC + "/" + args.pfaX2)

    if args.pfaX1Err:
        fillMap("PFAX1Up"  , INPUTLOC + "/" + args.pfaX1 + "_UP"  )
        fillMap("PFAX1Down", INPUTLOC + "/" + args.pfaX1 + "_DOWN")
    if args.pfaX2Err:              
        fillMap("PFAX2Up"  , INPUTLOC + "/" + args.pfaX2 + "_UP"  )
        fillMap("PFAX2Down", INPUTLOC + "/" + args.pfaX2 + "_DOWN")
       
    # Set up the output directory and make it if it does not exist
    outpath = "%s/%s/%s"%(OUTBASE,stub,tag)
    if not os.path.exists(outpath): os.makedirs(outpath)

    pfaX1resHistLow = ROOT.TH1F("pfaX1ResLow", ";|i#eta|;#sigma/#mu (online / offline)", 28, 0.5, 28.5)
    pfaX2resHistLow = ROOT.TH1F("pfaX2ResLow", ";|i#eta|;#sigma/#mu (online / offline)", 28, 0.5, 28.5)
    pfaYresHistLow  = ROOT.TH1F("pfaYResLow",  ";|i#eta|;#sigma/#mu (online / offline)", 28, 0.5, 28.5)

    pfaX1resHistHigh = ROOT.TH1F("pfaX1ResHigh", ";|i#eta|;#sigma/#mu (online / offline)", 28, 0.5, 28.5)
    pfaX2resHistHigh = ROOT.TH1F("pfaX2ResHigh", ";|i#eta|;#sigma/#mu (online / offline)", 28, 0.5, 28.5)
    pfaYresHistHigh  = ROOT.TH1F("pfaYResHigh",  ";|i#eta|;#sigma/#mu (online / offline)", 28, 0.5, 28.5)

    pfaResHistDummy  = ROOT.TH1F("pfaResHistDummy", ";|i#eta|;#sigma(online / offline)", 28, 0.5, 28.5)
    prettyHisto(pfaResHistDummy, 0.059, 0.059, 0.059, 0.072, 0.072, 0.072, 0.85, 0.85, 1.0,special=False)
    pfaResHistDummy.GetYaxis().SetRangeUser(0.0, 0.7)

    # Save the final histograms
    mapNameToHisto = MAPPFAHISTOS.values()[0]
    for name in mapNameToHisto.keys():

        className = mapNameToHisto[name].ClassName()

        if "TH2" in className:

            ROOT.gStyle.SetErrorX(0.0)

            zMax = 8e4
            
            c1 = ROOT.TCanvas("%s"%(name), "%s"%(name), 2400, 1440); c1.cd(); c1.SetLogz()

            ROOT.gPad.SetTopMargin(0.02625)
            ROOT.gPad.SetBottomMargin(0.13375)
            ROOT.gPad.SetLeftMargin(0.11)
            ROOT.gPad.SetRightMargin(0.12)

            drewRatio = False
            if "PFAX1" in MAPPFAHISTOS: drewRatio = draw2DHistoAndProfile(c1, "PFAX1", name, zMax, ROOT.kBlack, 20, drewRatio, args.pfaX1Err)
            if "PFAX2" in MAPPFAHISTOS: drewRatio = draw2DHistoAndProfile(c1, "PFAX2", name, zMax, ROOT.kRed  , 20, drewRatio, args.pfaX2Err)
            if "PFAY"  in MAPPFAHISTOS: drewRatio = draw2DHistoAndProfile(c1, "PFAY" , name, zMax, ROOT.kBlack, 4,  drewRatio, False)
    
            l = ROOT.TLine(mapNameToHisto[name].GetXaxis().GetBinLowEdge(1), 1, mapNameToHisto[name].GetXaxis().GetBinUpEdge(mapNameToHisto[name].GetNbinsX()), 1) 
            l.SetLineWidth(2)
            l.SetLineColor(ROOT.kBlack)
            l.SetLineStyle(2)
            l.Draw("SAME")

            c1.SaveAs("%s/%s.pdf"%(outpath,name))

        # 1D histos assumed to be a distribution of TP/RH for a given ieta
        elif "TH1" in className:

            c1 = ROOT.TCanvas("%s"%(name), "%s"%(name), 1600, 1600); c1.cd(); c1.SetGridy(); c1.SetGridx()

            ROOT.gPad.SetTopMargin(0.02)
            ROOT.gPad.SetBottomMargin(0.12)
            ROOT.gPad.SetLeftMargin(0.14)
            ROOT.gPad.SetRightMargin(0.02)

            t_pfaX1 = 0; t_pfaX2 = 0; t_pfaY = 0
            theStack = ROOT.THStack("theStack_%s"%(name), ""); theStack.Draw()

            ietaList = name.split("ieta")[-1].split("to"); ieta = int(ietaList[0])
            skipRes = False; ietaStr = ""
            if len(ietaList) > 1:
                skipRes = True
                ietaStr = "%s to %s"%(ietaList[0],ietaList[1])
            else:
                ietaStr = "%s"%(ietaList[0])

            schemeStubX1 = "PFA" + args.pfaX1.split("PFA")[-1].split("_")[0]
            schemeStubX2 = "PFA" + args.pfaX2.split("PFA")[-1].split("_")[0]
            schemeStubY  = "PFA" + args.pfaY.split("PFA")[-1].split("_")[0]

            etBinLow  = "RHET0.0to10.0"  in str(name.split("_")[1])
            etBinHigh = "RHET10.0to1000" in str(name.split("_")[1])
            
            pfaX1res = 0; pfaX2res = 0; pfaYres = 0
            if "PFAX1" in MAPPFAHISTOS:
                t_pfaX1, pfaX1res, pfaX1mean = draw1DHisto(theStack, "PFAX1", name, schemeStubX1, ROOT.kBlack, 1, 0.75, 0.52, 0.92, 0.67)
                if not skipRes:
                    if   etBinLow:  pfaX1resHistLow.SetBinContent(pfaX1resHistLow.GetXaxis().FindBin(ieta), pfaX1res)
                    elif etBinHigh: pfaX1resHistHigh.SetBinContent(pfaX1resHistHigh.GetXaxis().FindBin(ieta), pfaX1res)
            if "PFAX2" in MAPPFAHISTOS:
                t_pfaX2, pfaX2res, pfaX2mean = draw1DHisto(theStack, "PFAX2", name, schemeStubX2, ROOT.kRed, 1, 0.75, 0.34, 0.92, 0.49)
                if not skipRes:
                    if   etBinLow:  pfaX2resHistLow.SetBinContent(pfaX2resHistLow.GetXaxis().FindBin(ieta), pfaX2res)
                    elif etBinHigh: pfaX2resHistHigh.SetBinContent(pfaX2resHistHigh.GetXaxis().FindBin(ieta), pfaX2res)
            if "PFAY"  in MAPPFAHISTOS:
                t_pfaY, pfaYres, pfaYmean  = draw1DHisto(theStack, "PFAY" , name, schemeStubY, ROOT.kGray+2, 1, 0.75, 0.70, 0.92, 0.85)
                if not skipRes:
                    if    etBinLow: pfaYresHistLow.SetBinContent(pfaYresHistLow.GetXaxis().FindBin(ieta), pfaYres)
                    elif etBinHigh: pfaYresHistHigh.SetBinContent(pfaYresHistHigh.GetXaxis().FindBin(ieta), pfaYres)

            ietaText = ROOT.TPaveText(0.72, 0.86, 0.92, 0.95, "trNDC")
            ietaText.SetFillColor(ROOT.kWhite); ietaText.SetTextAlign(11); ietaText.SetTextFont(63); ietaText.SetTextSize(80)
            ietaText.AddText("|i#eta| = %s"%(ietaStr))

            prettyHisto(theStack, 0.042, 0.042, 0.042, 0.052, 0.052, 0.052, 1.06, 1.4, 1.0)
            theStack.Draw("HIST NOSTACK")

            ietaText.Draw("SAME")
            if t_pfaX1 != 0: t_pfaX1.Draw("SAME")
            if t_pfaX2 != 0: t_pfaX2.Draw("SAME")
            if t_pfaY  != 0: t_pfaY.Draw("SAME")

            c1.SaveAs("%s/%s.pdf"%(outpath,name))

    # Now do resolution plots
    ROOT.gStyle.SetErrorX(0.5)

    canvases = []
    canvases.append(ROOT.TCanvas("pfa_res_low", "pfa_res_low", 2400, 1440))
    canvases.append(ROOT.TCanvas("pfa_res_high", "pfa_res_high", 2400, 1440))

    # Low ET bin is i == 0 and high ET bin is i == 1
    for i in xrange(len(canvases)):
        
        pfaYtext = ""; pfaX1text = ""; pfaX2text = ""
        pfaYgraph = 0; pfaX1graph = 0; pfaX2graph = 0

        # Case for low ET bin
        if i == 0: pfaYgraph = ROOT.TGraphErrors(pfaYresHistLow);  pfaX1graph = ROOT.TGraphErrors(pfaX1resHistLow);  pfaX2graph = ROOT.TGraphErrors(pfaX2resHistLow)
        if i == 1: pfaYgraph = ROOT.TGraphErrors(pfaYresHistHigh); pfaX1graph = ROOT.TGraphErrors(pfaX1resHistHigh); pfaX2graph = ROOT.TGraphErrors(pfaX2resHistHigh)

        canvases[i].cd(); canvases[i].SetGridy(); canvases[i].SetGridx()
        ROOT.gPad.SetTopMargin(0.03)
        ROOT.gPad.SetBottomMargin(0.14)
        ROOT.gPad.SetLeftMargin(0.13)
        ROOT.gPad.SetRightMargin(0.03)
       
        pfaResHistDummy.Draw("")

        iamTextX1 = ROOT.TPaveText(0.7, 0.69, 0.8, 0.75, "trNDC"); iamTextX1.SetFillColor(ROOT.kWhite); iamTextX1.SetTextAlign(12); iamTextX1.SetTextFont(63); iamTextX1.SetTextSize(90)
        if "PFAX1" in MAPPFAHISTOS:
            pfaX1graph.SetLineWidth(3);  pfaX1graph.SetLineColor(ROOT.kBlack)
            pfaX1graph.SetMarkerSize(4); pfaX1graph.SetMarkerColor(ROOT.kBlack); pfaX1graph.SetMarkerStyle(20)
            iamTextX1.AddText("PFA" + args.pfaX1.split("PFA")[-1].split("_")[0])
            iamTextX1.SetTextColor(ROOT.kBlack)

            pfaX1graph.Draw("EP SAME")
            iamTextX1.Draw("SAME")

        iamTextX2 = ROOT.TPaveText(0.7, 0.78, 0.8, 0.84, "trNDC"); iamTextX2.SetFillColor(ROOT.kWhite); iamTextX2.SetTextAlign(12); iamTextX2.SetTextFont(63); iamTextX2.SetTextSize(90)
        if "PFAX2" in MAPPFAHISTOS:
            pfaX2graph.SetLineWidth(3);  pfaX2graph.SetLineColor(ROOT.kRed)
            pfaX2graph.SetMarkerSize(4); pfaX2graph.SetMarkerColor(ROOT.kRed); pfaX2graph.SetMarkerStyle(20)
            iamTextX2.AddText("PFA" + args.pfaX2.split("PFA")[-1].split("_")[0])
            iamTextX2.SetTextColor(ROOT.kRed)

            pfaX2graph.Draw("EP SAME")
            iamTextX2.Draw("SAME")

        iamTextY = ROOT.TPaveText(0.7, 0.87, 0.8, 0.93, "trNDC"); iamTextY.SetFillColor(ROOT.kWhite); iamTextY.SetTextAlign(12); iamTextY.SetTextFont(63); iamTextY.SetTextSize(90)
        if "PFAY"  in MAPPFAHISTOS:
            pfaYgraph.SetLineWidth(3);  pfaYgraph.SetLineColor(ROOT.kGray+2)
            pfaYgraph.SetMarkerSize(4); pfaYgraph.SetMarkerColor(ROOT.kGray+2); pfaYgraph.SetMarkerStyle(20)
            iamTextY.AddText("PFA" + args.pfaY.split("PFA")[-1].split("_")[0])
            iamTextY.SetTextColor(ROOT.kGray+2)

            pfaYgraph.Draw("EP SAME")
            iamTextY.Draw("SAME")

        if i == 0: canvases[i].SaveAs("%s/pfa_res_low.pdf"%(outpath))
        if i == 1: canvases[i].SaveAs("%s/pfa_res_high.pdf"%(outpath))
