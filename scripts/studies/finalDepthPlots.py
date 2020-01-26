import sys, os, ROOT, argparse

ROOT.TH1.SetDefaultSumw2()
ROOT.TH2.SetDefaultSumw2()
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetPaintTextFormat("3.2f")
ROOT.gStyle.SetFrameLineWidth(4)
ROOT.gStyle.SetErrorX(0)

# The doOptions method takes a histo and its histoName and looks in the global OPIONSMAP
# to see if there are any special options to be done for the histo (axis titles, etc)
def doOptions(histo, histoName):

    if histoName not in MAPPFAHISTOS: return

    is1D = "TH1" in histo.ClassName()

    for axis, options in MAPPFAHISTOS[histoName].iteritems():

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

# Set the title and axis label sizes to some reasonable values
def prettyHisto(histo):
    histo.GetYaxis().SetLabelSize(0.045); histo.GetYaxis().SetTitleSize(0.051); histo.GetYaxis().SetTitleOffset(1.05)
    histo.GetXaxis().SetLabelSize(0.045); histo.GetXaxis().SetTitleSize(0.051); histo.GetXaxis().SetTitleOffset(0.95)
    histo.GetZaxis().SetLabelSize(0.045); histo.GetZaxis().SetTitleSize(0.051)

# Get the ProfileX of an input 2D histo and set some visual attributes
def prettyProfile(histo, name, color, markerStyle, pfa):

    p = histo.ProfileX("p_%s_%s"%(pfa,name), 1, -1, "")
    p.Scale(1.0/p.Integral())
    p.SetMinimum(0); p.SetMaximum(0.95)
    p.GetYaxis().SetTitle("A.U.")

    p.SetMarkerStyle(markerStyle); p.SetMarkerSize(7)
    p.SetLineWidth(7); p.SetLineColor(color)
    p.SetMarkerColor(color)
    p.Sumw2()

    return p

# In list of ROOT files go through the histograms and add them to the dictionary
def fillMap(pfaKey, inRootDir):

    if inRootDir == "NULL": return

    MAPPFAHISTOS[pfaKey] = {}

    for histoFile in os.listdir(inRootDir):

       if ".root" not in histoFile: continue
       histoFile = ROOT.TFile.Open(inRootDir + histoFile, "READ")
       for hkey in histoFile.GetListOfKeys():
           if "TH" not in hkey.GetClassName(): continue

           name = hkey.GetName()
           histo = hkey.ReadObj()
           histo.SetDirectory(0)

           histo.Sumw2()
           
           if name in MAPPFAHISTOS[pfaKey].keys(): MAPPFAHISTOS[pfaKey][name].Add(histo)
           else: MAPPFAHISTOS[pfaKey][name] = histo

if __name__ == '__main__':

    usage = "usage: %prog [options]"
    parser = argparse.ArgumentParser(usage)
    parser.add_argument("--tag"  , dest="tag"  , help="Unique tag for output"  , type=str, default="")
    parser.add_argument("--pfaY" , dest="pfaY" , help="Path to inputs for PFAY", type=str, default="NULL")
    parser.add_argument("--pfaX1", dest="pfaX1", help="Path to other PFAX dir" , type=str, default="NULL") 
    parser.add_argument("--pfaX2", dest="pfaX2", help="Path to other PFAX dir" , type=str, default="NULL") 
    
    arg = parser.parse_args()

    XCANVAS = 2400; YCANVAS = 2400

    if   args.pfaX1 != "NULL": stub = args.pfaX1.split("Depths/")[-1]
    elif args.pfaX2 != "NULL": stub = args.pfaX2.split("Depths/")[-1]
    else: quit()

    tag = args.tag

    outpath = "./plots/Depths/%s/%s"%(stub,tag)
    if not os.path.exists(outpath): os.makedirs(outpath)

    HOME = os.getenv("HOME")
    OUTBASE  = "%s/nobackup/HCAL_Trigger_Study/plots/Depths"%(HOME)
    INPUTLOC = "%s/nobackup/HCAL_Trigger_Study/input/Depths"%(HOME)

    OPTIONSMAP = {}
    MAPPFAHISTOS = {}

    fillMap("PFAY",  INPUTLOC + "/" + args.pfaY)
    fillMap("PFAX1", INPUTLOC + "/" + args.pfaX1)
    fillMap("PFAX2", INPUTLOC + "/" + args.pfaX2)

    # Save the final histograms
    mapNameToHisto = MAPPFAHISTOS.values()[0]
    for name in mapNameToHisto.values()[0].keys():

        if "TH2" in mapNameToHisto.values()[0][name].ClassName():

            c1 = ROOT.TCanvas("%s"%(name), "%s"%(name), XCANVAS, YCANVAS); c1.cd(); c1.SetLogz()

            ROOT.gPad.SetLeftMargin(0.12)
            ROOT.gPad.SetRightMargin(0.02)

            someText = ROOT.TPaveText(0.65, 0.62, 0.90, 0.85, "trNDC")
            someText.SetFillColor(ROOT.kWhite);
            someText.SetTextAlign(11)

            if "PFAX1" in mapPFAhistos:
                scenario = args.pfaX1.split("/")[4]
                algoName = args.pfaX1.split("/")[3]
                textBlob = algoName + " - " + scenario

                pPFAX1 = prettyProfile(mapPFAhistos["PFAX1"][name],name,ROOT.kBlack,20,"PFAX1")
                prettyHisto(pPFAX1)

                someText.AddText(textBlob)
                someText.GetListOfLines().Last().SetTextColor(ROOT.kBlack)

                pPFAX1.Draw("HIST P SAME")
                pPFAX1.Draw("HIST SAME")

            if "PFAX2" in mapPFAhistos:
                scenario = args.pfaX2.split("/")[4]
                algoName = args.pfaX2.split("/")[3]
                textBlob = algoName + " - " + scenario

                pPFAX2 = prettyProfile(mapPFAhistos["PFAX2"][name],name,ROOT.kRed,20,"PFAX2")
                prettyHisto(pPFAX2)

                someText.AddText(textBlob)
                someText.GetListOfLines().Last().SetTextColor(ROOT.kRed)

                pPFAX2.Draw("HIST P SAME")
                pPFAX2.Draw("HIST SAME")

            if "PFAY" in mapPFAhistos:
                scenario = args.pfaY.split("/")[4]
                algoName = args.pfaY.split("/")[3]
                textBlob = algoName + " - " + scenario

                pPFAY = prettyProfile(mapPFAhistos["PFAY"][name],name,ROOT.kGray+1,20,"PFAY")
                prettyHisto(pPFAY)

                someText.AddText(textBlob)
                someText.GetListOfLines().Last().SetTextColor(ROOT.kGray+1)

                pPFAY.Draw("HIST P SAME")
                pPFAY.Draw("HIST SAME")

            someText.Draw("SAME")
            c1.SaveAs("%s/%s.pdf"%(outpath,name))
