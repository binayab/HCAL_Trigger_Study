import sys, os, ROOT, argparse

ROOT.TH1.SetDefaultSumw2()
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetPaintTextFormat("3.2f")
ROOT.gStyle.SetFrameLineWidth(2)
ROOT.gStyle.SetErrorX(0)

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

def draw2DHistoAndProfile(canvas, keyName, histoName, zMax, color, markerStyle, drewRatio, drawErrorBand):

    canvas.cd()

    # Get nominal TP/RH profile
    theHisto = MAPPFAHISTOS[keyName][histoName]

    #sliceFit = ROOT.TF1("f_%s_%s"%(keyName,histoName), "gaus")
    #theHisto.FitSlicesY(sliceFit, 0, -1, 0, "QN")

    #resIeta = ROOT.gDirectory.Get(theHisto.GetName()+"_2"); resIeta.SetDirectory(0); resIeta.SetName("%s_%s"%(keyName,histoName))

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

    return drewRatio, 0 

def draw1DHisto(c1, theStack, keyName, histoName, algoName, color, x1, y1, x2, y2):

    theHisto = MAPPFAHISTOS[keyName][histoName]

    prettyHisto(theHisto, 0.042, 0.042, 0.042, 0.052, 0.052, 0.052, 1.06, 1.2, 1.0, color)
    theStack.Add(theHisto)
    theStack.GetXaxis().SetTitle(theHisto.GetXaxis().GetTitle())
    theStack.GetYaxis().SetTitle(theHisto.GetYaxis().GetTitle())

    someTextPFAX = ROOT.TPaveText(x1, y1, x2, y2, "trNDC")
    prettyText(someTextPFAX, color, algoName, theHisto.GetMean(), theHisto.GetStdDev())

    return someTextPFAX, theHisto.GetStdDev()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--tag"      , dest="tag"      , type=str, default=""    , help="Unique tag for output")
    parser.add_argument("--pfaY"     , dest="pfaY"     , type=str, default="NULL", help="Path to inputs for PFAY")
    parser.add_argument("--pfaX1"    , dest="pfaX1"    , type=str, default="NULL", help="Path to other PFAX dir") 
    parser.add_argument("--pfaX2"    , dest="pfaX2"    , type=str, default="NULL", help="Path to other PFAX dir") 
    parser.add_argument("--pfaX1Err" , dest="pfaX1Err" , default=False, action="store_true", help="Draw error bands for PFAX") 
    parser.add_argument("--pfaX2Err" , dest="pfaX2Err" , default=False, action="store_true", help="Draw error bands for PFAX") 
    args = parser.parse_args()
    
    OPTIONSMAP = {"TPRH_TPET_ieta1to16"  : {"X" : {"min" : 0.5, "max" : 20}, "Y" : {"min" : 0.2, "max" : 2}},
                  "TPRH_RHET_ieta1to16"  : {"X" : {"min" : 0.5, "max" : 20}, "Y" : {"min" : 0.2, "max" : 2}},
                  "TPRH_TPET_ieta17to28" : {"X" : {"min" : 0.5, "max" : 20}, "Y" : {"min" : 0.2, "max" : 2}},
                  "TPRH_RHET_ieta17to28" : {"X" : {"min" : 0.5, "max" : 20}, "Y" : {"min" : 0.2, "max" : 2}},
                  "TPRH_TPET_ieta1to28"  : {"X" : {"min" : 0.5, "max" : 20}, "Y" : {"min" : 0.2, "max" : 2}},
                  "TPRH_RHET_ieta1to28"  : {"X" : {"min" : 0.5, "max" : 20}, "Y" : {"min" : 0.2, "max" : 2}}}

    MAPPFAHISTOS = {}

    # Figure out the stub to use for the output directory
    # If neither pfaX1 or pfaX2 have been specified then quit!
    if   args.pfaX1 != "NULL": stub = args.pfaX1.split("Ratios/")[-1]
    elif args.pfaX2 != "NULL": stub = args.pfaX2.split("Ratios/")[-1]
    else: quit()

    tag = args.tag

    # Save the input directories provided and fill the map of histos
    fillMap("PFAY" , args.pfaY)
    fillMap("PFAX1", args.pfaX1)
    fillMap("PFAX2", args.pfaX2)

    if args.pfaX1Err:
        fillMap("PFAX1Up"  , args.pfaX1 + "/Up"  )
        fillMap("PFAX1Down", args.pfaX1 + "/Down")
    if args.pfaX2Err:                       
        fillMap("PFAX2Up"  , args.pfaX2 + "/Up"  )
        fillMap("PFAX2Down", args.pfaX2 + "/Down")
       
    # Set up the output directory and make it if it does not exist
    outpath = "./plots/Ratios/%s/%s"%(stub,tag)
    if not os.path.exists(outpath): os.makedirs(outpath)

    pfaX1resHistLow = ROOT.TH1F("pfaX1ResLow", ";|i#eta|;#sigma(online / offline)", 28, 0.5, 28.5)
    pfaX2resHistLow = ROOT.TH1F("pfaX2ResLow", ";|i#eta|;#sigma(online / offline)", 28, 0.5, 28.5)
    pfaYresHistLow  = ROOT.TH1F("pfaYResLow",  ";|i#eta|;#sigma(online / offline)", 28, 0.5, 28.5)

    pfaX1resHistHigh = ROOT.TH1F("pfaX1ResHigh", ";|i#eta|;#sigma(online / offline)", 28, 0.5, 28.5)
    pfaX2resHistHigh = ROOT.TH1F("pfaX2ResHigh", ";|i#eta|;#sigma(online / offline)", 28, 0.5, 28.5)
    pfaYresHistHigh  = ROOT.TH1F("pfaYResHigh",  ";|i#eta|;#sigma(online / offline)", 28, 0.5, 28.5)

    # Save the final histograms
    for name in MAPPFAHISTOS.values()[0].keys():

        className = MAPPFAHISTOS.values()[0][name].ClassName()

        if "TH2" in className:
            zMax = 0
            if "RHET" in name: zMax = 8e4
            else:              zMax = 5e3
            
            c1 = ROOT.TCanvas("%s"%(name), "%s"%(name), 2400, 1440); c1.cd(); c1.SetLogz()

            ROOT.gPad.SetTopMargin(0.02625)
            ROOT.gPad.SetBottomMargin(0.13375)
            ROOT.gPad.SetLeftMargin(0.11)
            ROOT.gPad.SetRightMargin(0.12)

            drewRatio = False#; pfaX1res = 0; pfaX2res = 0; pfaYres = 0
            if "PFAX1" in MAPPFAHISTOS: drewRatio, pfaX1res = draw2DHistoAndProfile(c1, "PFAX1", name, zMax, ROOT.kBlack, 20, drewRatio, args.pfaX1Err)
            if "PFAX2" in MAPPFAHISTOS: drewRatio, pfaX2res = draw2DHistoAndProfile(c1, "PFAX2", name, zMax, ROOT.kRed  , 20, drewRatio, args.pfaX2Err)
            if "PFAY"  in MAPPFAHISTOS: drewRatio, pfaYres  = draw2DHistoAndProfile(c1, "PFAY" , name, zMax, ROOT.kBlack, 4,  drewRatio, False)
    
            l = 0
            if name in OPTIONSMAP: l = ROOT.TLine(OPTIONSMAP[name]["X"]["min"]-MAPPFAHISTOS.values()[0][name].GetXaxis().GetBinWidth(1)/1.75, 1, OPTIONSMAP[name]["X"]["max"]+MAPPFAHISTOS.values()[0][name].GetXaxis().GetBinWidth(1)/1.75, 1)
            else: l = ROOT.TLine(-28, 1, 28, 1) 
            l.SetLineWidth(2)
            l.SetLineColor(ROOT.kBlack)
            l.SetLineStyle(2)
            l.Draw("SAME")

            c1.SaveAs("%s/%s.pdf"%(outpath,name))

            # Now do resolution plots
            #c2 = ROOT.TCanvas("%s_res"%(name), "%s_res"%(name), 2400, 1440); c2.cd()

            #ROOT.gPad.SetTopMargin(0.02625)
            #ROOT.gPad.SetBottomMargin(0.13375)
            #ROOT.gPad.SetLeftMargin(0.13)
            #ROOT.gPad.SetRightMargin(0.05)

            #if pfaX1res:
            #    prettyHisto(pfaX1res, 0.059, 0.059, 0.059, 0.072, 0.072, 0.072, 0.85, 0.85, 1.0,special=False)
            #    pfaX1res.SetLineWidth(0);  pfaX1res.SetLineColor(ROOT.kBlack)
            #    pfaX1res.SetMarkerSize(3); pfaX1res.SetMarkerColor(ROOT.kBlack); pfaX1res.SetMarkerStyle(20)
            #if pfaX2res:
            #    prettyHisto(pfaX2res, 0.059, 0.059, 0.059, 0.072, 0.072, 0.072, 0.85, 0.85, 1.0,special=False)
            #    pfaX2res.SetLineWidth(0);  pfaX2res.SetLineColor(ROOT.kRed)
            #    pfaX2res.SetMarkerSize(3); pfaX2res.SetMarkerColor(ROOT.kRed); pfaX2res.SetMarkerStyle(20)
            #if pfaYres:
            #    prettyHisto(pfaYres, 0.059, 0.059, 0.059, 0.072, 0.072, 0.072, 0.85, 0.85, 1.0,special=False)
            #    pfaX2res.SetLineWidth(0); pfaYres.SetLineColor(ROOT.kBlack)
            #    pfaYres.SetMarkerSize(3); pfaYres.SetMarkerColor(ROOT.kBlack); pfaYres.SetMarkerStyle(4)
            #    pfaYres.SetTitle(""); pfaYres.GetYaxis().SetTitle("#sigma(online / offline)")

            #pfaYres.Draw(); pfaX1res.Draw("SAME"); pfaX2res.Draw("SAME")

            #c2.SaveAs("%s/%s_res.pdf"%(outpath, name))

        # 1D histos assumed to be a distribution of TP/RH for a given ieta
        elif "TH1" in className:

            c1 = ROOT.TCanvas("%s"%(name), "%s"%(name), 1600, 1600); c1.cd(); c1.SetGridy(); c1.SetGridx()

            ROOT.gPad.SetTopMargin(0.02)
            ROOT.gPad.SetBottomMargin(0.12)
            ROOT.gPad.SetLeftMargin(0.14)
            ROOT.gPad.SetRightMargin(0.02)

            t_pfaX1 = 0; t_pfaX2 = 0; t_pfaY = 0
            theStack = ROOT.THStack("theStack_%s"%(name), ""); theStack.Draw()
            ieta = int(name.split("ieta")[-1])
            rhBasis = name.split("_")[1][0:2] == "RH"
            etBinLow = "1000" not in str(name.split("_")[1])
            print name
            
            pfaX1res = 0; pfaX2res = 0; pfaYres = 0
            if "PFAX1" in MAPPFAHISTOS:
                t_pfaX1, pfaX1res = draw1DHisto(c1, theStack, "PFAX1", name, args.pfaX1.split("/")[3], ROOT.kBlack , 0.75, 0.75, 0.95, 0.90)
                if rhBasis:
                    if etBinLow: pfaX1resHistLow.SetBinContent(pfaX1resHistLow.GetXaxis().FindBin(ieta), pfaX1res)
                    else: pfaX1resHistHigh.SetBinContent(pfaX1resHistHigh.GetXaxis().FindBin(ieta), pfaX1res)
            if "PFAX2" in MAPPFAHISTOS:
                t_pfaX2, pfaX2res = draw1DHisto(c1, theStack, "PFAX2", name, args.pfaX2.split("/")[3], ROOT.kRed, 0.75, 0.39, 0.95, 0.54)
                if rhBasis:
                    if etBinLow: pfaX2resHistLow.SetBinContent(pfaX2resHistLow.GetXaxis().FindBin(ieta), pfaX2res)
                    else: pfaX2resHistHigh.SetBinContent(pfaX2resHistHigh.GetXaxis().FindBin(ieta), pfaX2res)
            if "PFAY"  in MAPPFAHISTOS:
                t_pfaY, pfaYres  = draw1DHisto(c1, theStack, "PFAY" , name, args.pfaY.split("/")[3] , ROOT.kGray+2   , 0.75, 0.57, 0.95, 0.72)
                if rhBasis:
                    if etBinLow: pfaYresHistLow.SetBinContent(pfaYresHistLow.GetXaxis().FindBin(ieta), pfaYres)
                    else: pfaYresHistHigh.SetBinContent(pfaYresHistHigh.GetXaxis().FindBin(ieta), pfaYres)
            prettyHisto(theStack, 0.042, 0.042, 0.042, 0.052, 0.052, 0.052, 1.06, 1.4, 1.0)
            theStack.Draw("HISTO NOSTACK")

            if t_pfaX1 != 0: t_pfaX1.Draw("SAME")
            if t_pfaX2 != 0: t_pfaX2.Draw("SAME")
            if t_pfaY  != 0: t_pfaY.Draw("SAME")

            c1.SaveAs("%s/%s.pdf"%(outpath,name))

    # Now do resolution plots
    c3 = ROOT.TCanvas("pfa_res_low", "pfa_res_low", 2400, 1440); c3.cd()
    lowStack = ROOT.THStack("lowStack", ";%s;%s"%(pfaX1resHistLow.GetXaxis().GetTitle(),pfaX1resHistLow.GetYaxis().GetTitle())); lowStack.Draw()

    ROOT.gPad.SetTopMargin(0.02625)
    ROOT.gPad.SetBottomMargin(0.13375)
    ROOT.gPad.SetLeftMargin(0.13)
    ROOT.gPad.SetRightMargin(0.05)

    iamTextX1low = ROOT.TPaveText(0.3, 0.2, 0.5, 0.25, "trNDC"); iamTextX1low.SetFillColor(ROOT.kWhite); iamTextX1low.SetTextAlign(11)

    prettyHisto(pfaX1resHistLow, 0.059, 0.059, 0.059, 0.072, 0.072, 0.072, 0.85, 0.85, 1.0,special=False)
    pfaX1resHistLow.SetLineWidth(3);  pfaX1resHistLow.SetLineColor(ROOT.kBlack)
    pfaX1resHistLow.SetMarkerSize(4); pfaX1resHistLow.SetMarkerColor(ROOT.kBlack); pfaX1resHistLow.SetMarkerStyle(20)
    lowStack.Add(pfaX1resHistLow)
    iamTextX1low.AddText(args.pfaX1.split("/")[3])
    iamTextX1low.SetTextColor(ROOT.kBlack)

    iamTextX2low = ROOT.TPaveText(0.3, 0.28, 0.5, 0.33, "trNDC"); iamTextX2low.SetFillColor(ROOT.kWhite); iamTextX2low.SetTextAlign(11)
    prettyHisto(pfaX2resHistLow, 0.059, 0.059, 0.059, 0.072, 0.072, 0.072, 0.85, 0.85, 1.0,special=False)
    pfaX2resHistLow.SetLineWidth(3);  pfaX2resHistLow.SetLineColor(ROOT.kRed)
    pfaX2resHistLow.SetMarkerSize(4); pfaX2resHistLow.SetMarkerColor(ROOT.kRed); pfaX2resHistLow.SetMarkerStyle(20)
    lowStack.Add(pfaX2resHistLow)
    iamTextX2low.AddText(args.pfaX2.split("/")[3])
    iamTextX2low.SetTextColor(ROOT.kRed)

    iamTextYlow = ROOT.TPaveText(0.3, 0.36, 0.5, 0.41, "trNDC"); iamTextYlow.SetFillColor(ROOT.kWhite); iamTextYlow.SetTextAlign(11)
    prettyHisto(pfaYresHistLow, 0.059, 0.059, 0.059, 0.072, 0.072, 0.072, 0.85, 0.85, 1.0,special=False)
    pfaYresHistLow.SetLineWidth(3); pfaYresHistLow.SetLineColor(ROOT.kBlack)
    pfaYresHistLow.SetMarkerSize(4); pfaYresHistLow.SetMarkerColor(ROOT.kGray+2); pfaYresHistLow.SetMarkerStyle(20)
    lowStack.Add(pfaYresHistLow)
    iamTextYlow.AddText(args.pfaY.split("/")[3])
    iamTextYlow.SetTextColor(ROOT.kGray+2)

    prettyHisto(lowStack, 0.059, 0.059, 0.059, 0.072, 0.072, 0.072, 0.85, 0.85, 1.0,special=False)
    lowStack.Draw("P NOSTACK")
    
    iamTextX1low.Draw("SAME"); iamTextX2low.Draw("SAME"); iamTextYlow.Draw("SAME")

    c3.SaveAs("%s/pfa_res_low.pdf"%(outpath))

    # Now do resolution plots
    c4 = ROOT.TCanvas("pfa_res_high", "pfa_res_high", 2400, 1440); c4.cd()

    highStack = ROOT.THStack("highStack", ";%s;%s"%(pfaX1resHistLow.GetXaxis().GetTitle(),pfaX1resHistLow.GetYaxis().GetTitle())); highStack.Draw()

    ROOT.gPad.SetTopMargin(0.02625)
    ROOT.gPad.SetBottomMargin(0.13375)
    ROOT.gPad.SetLeftMargin(0.13)
    ROOT.gPad.SetRightMargin(0.05)

    iamTextX1high = ROOT.TPaveText(0.3, 0.2, 0.5, 0.25, "trNDC"); iamTextX1high.SetFillColor(ROOT.kWhite); iamTextX1high.SetTextAlign(11)

    prettyHisto(pfaX1resHistHigh, 0.059, 0.059, 0.059, 0.072, 0.072, 0.072, 0.85, 0.9, 1.0,special=False)
    pfaX1resHistHigh.SetLineWidth(3);  pfaX1resHistHigh.SetLineColor(ROOT.kBlack)
    pfaX1resHistHigh.SetMarkerSize(4); pfaX1resHistHigh.SetMarkerColor(ROOT.kBlack); pfaX1resHistHigh.SetMarkerStyle(20)
    highStack.Add(pfaX1resHistHigh)
    iamTextX1high.AddText(args.pfaX1.split("/")[3])
    iamTextX1high.SetTextColor(ROOT.kBlack)

    iamTextX2high = ROOT.TPaveText(0.3, 0.28, 0.5, 0.33, "trNDC"); iamTextX2high.SetFillColor(ROOT.kWhite); iamTextX2high.SetTextAlign(11)
    prettyHisto(pfaX2resHistHigh, 0.059, 0.059, 0.059, 0.072, 0.072, 0.072, 0.85, 0.9, 1.0,special=False)
    pfaX2resHistHigh.SetLineWidth(3);  pfaX2resHistHigh.SetLineColor(ROOT.kRed)
    pfaX2resHistHigh.SetMarkerSize(4); pfaX2resHistHigh.SetMarkerColor(ROOT.kRed); pfaX2resHistHigh.SetMarkerStyle(20)
    highStack.Add(pfaX2resHistHigh)
    iamTextX2high.AddText(args.pfaX2.split("/")[3])
    iamTextX2high.SetTextColor(ROOT.kRed)

    iamTextYhigh = ROOT.TPaveText(0.3, 0.36, 0.5, 0.41, "trNDC"); iamTextYhigh.SetFillColor(ROOT.kWhite); iamTextYhigh.SetTextAlign(11)
    prettyHisto(pfaYresHistHigh, 0.059, 0.059, 0.059, 0.072, 0.072, 0.072, 0.85, 0.9, 1.0,special=False)
    pfaYresHistHigh.SetLineWidth(3); pfaYresHistHigh.SetLineColor(ROOT.kGray+2)
    pfaYresHistHigh.SetMarkerSize(4); pfaYresHistHigh.SetMarkerColor(ROOT.kGray+2); pfaYresHistHigh.SetMarkerStyle(20)
    highStack.Add(pfaYresHistHigh)
    iamTextYhigh.AddText(args.pfaY.split("/")[3])
    iamTextYhigh.SetTextColor(ROOT.kGray+2)

    prettyHisto(highStack, 0.059, 0.059, 0.059, 0.072, 0.072, 0.072, 0.85, 0.85, 1.0,special=False)
    highStack.Draw("P NOSTACK")
    iamTextX1high.Draw("SAME"); iamTextX2high.Draw("SAME"); iamTextYhigh.Draw("SAME")

    c4.SaveAs("%s/pfa_res_high.pdf"%(outpath))
