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
parser.add_argument("--tag"     , dest="tag"     , help="Unique tag for output"    , type=str, required=True)
parser.add_argument("--ratio", dest="ratio", help="Draw a ratio"   , default=False, action="store_true")
parser.add_argument("--pfaY", dest="pfaY", type=str, help="Path to inputs for PFAY", default="NULL")
parser.add_argument("--pfaX1", dest="pfaX1", help="Path to other PFAX dir", default="NULL", type=str) 
parser.add_argument("--pfaX2", dest="pfaX2", help="Path to other PFAX dir", default="NULL", type=str) 

arg = parser.parse_args()

def prettyHisto(histo,magicFactor=1.0,magicFactor2=1.0):
    histo.GetYaxis().SetLabelSize(magicFactor*0.055); histo.GetYaxis().SetTitleSize(magicFactor*0.06); histo.GetYaxis().SetTitleOffset(0.9/magicFactor)
    histo.GetXaxis().SetLabelSize(magicFactor*0.055); histo.GetXaxis().SetTitleSize(magicFactor*0.08); histo.GetXaxis().SetTitleOffset(0.5/magicFactor2)
    histo.GetZaxis().SetLabelSize(magicFactor*0.055); histo.GetZaxis().SetTitleSize(magicFactor*0.06)

    if type(histo) is ROOT.TH1D: histo.SetLineWidth(2)

def prettyProfile(histo, name, color, markerStyle, pfa):

    p = histo.ProfileX("p_%s_%s"%(pfa,name), 1, -1)
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

           spec = hkey.GetName().find("-")
           name = hkey.GetName()[spec+1:]
           histo = hkey.ReadObj()
           histo.SetDirectory(0)

           histo.Sumw2()
           
           if name in theMap[pfaKey].keys(): theMap[pfaKey][name].Add(histo)
           else: theMap[pfaKey][name] = histo

if __name__ == '__main__':

    XCANVAS = 2400; YCANVAS = 1800

    drawRatio = arg.ratio 
    tag = arg.tag

    inRootDirs = {}

    if arg.pfaX1 == "NULL": quit()
    if arg.pfaY == "NULL": drawRatio = False

    inRootDirs["PFAY"] = arg.pfaY
    inRootDirs["PFAX1"] = arg.pfaX1
    inRootDirs["PFAX2"] = arg.pfaX2
       
    outpath = "./plots/Ratios/%s"%(tag)
    if not os.path.exists(outpath): os.makedirs(outpath)

    mapPFAhistos = {}

    fillMap("PFAY",  inRootDirs["PFAY"],  mapPFAhistos)
    fillMap("PFAX1", inRootDirs["PFAX1"], mapPFAhistos)
    fillMap("PFAX2", inRootDirs["PFAX2"], mapPFAhistos)

    # Save the final histograms
    for name in mapPFAhistos.values()[0].keys():

        zMax = 0
        if "RHET" in name: zMax = 6e3
        else: zMax = 5e3
        
        l = ROOT.TLine(-28.5, 1, 28.5, 1)
        l.SetLineWidth(2)
        l.SetLineColor(ROOT.kBlack)
        l.SetLineStyle(2)

        if not drawRatio:
            c1 = ROOT.TCanvas("%s"%(name), "%s"%(name), XCANVAS, int(0.8*YCANVAS)); c1.cd(); c1.SetLogz()

            ROOT.gPad.SetTopMargin(0.02625)
            ROOT.gPad.SetBottomMargin(0.13375)
            ROOT.gPad.SetLeftMargin(0.11)
            ROOT.gPad.SetRightMargin(0.12)

            if "PFAX1" in mapPFAhistos:
                pPFAX1 = prettyProfile(mapPFAhistos["PFAX1"][name],name,ROOT.kBlack,20,"PFAX1")
                mapPFAhistos["PFAX1"][name].SetContour(255)
                mapPFAhistos["PFAX1"][name].GetYaxis().SetRangeUser(0.1,2)
                mapPFAhistos["PFAX1"][name].GetZaxis().SetRangeUser(1,zMax)
                mapPFAhistos["PFAX1"][name].Draw("COLZ")
                prettyHisto(mapPFAhistos["PFAX1"][name],0.875,0.8)
                pPFAX1.Draw("EP SAME")
            if "PFAY" in mapPFAhistos:
                prettyHisto(mapPFAhistos["PFAY"][name],0.875,0.8)
                pPFAY = prettyProfile(mapPFAhistos["PFAY"][name],name,ROOT.kBlack,4,"PFAY")
                pPFAY.Draw("EP SAME")
            if "PFAX2" in mapPFAhistos:
                prettyHisto(mapPFAhistos["PFAX2"][name],0.875,0.8)
                pPFAX2 = prettyProfile(mapPFAhistos["PFAX2"][name],name,ROOT.kBlack,20,"PFAX2")
                pPFAX2.Draw("EP SAME")

            l.Draw("SAME")

            c1.SaveAs("%s/%s.pdf"%(outpath,name))

        else:
            XMin = 0;    XMax = 1; RatioXMin = 0; RatioXMax = 1 
            YMin = 0.30; YMax = 1; RatioYMin = 0; RatioYMax = 0.30
            PadFactor = (YMax-YMin) / (RatioYMax-RatioYMin)

            #XTitleSize = 0.045;  XLabelSize = 0.036;  XTitleOffset = 4.0 
            #YTitleSize = 0.045;  YLabelSize = 0.036;  YTitleOffset = 0.9
                                
            c1 = ROOT.TCanvas("%s"%(name), "%s"%(name), XCANVAS, YCANVAS); 
            c1.Divide(1,2); c1.cd(1); ROOT.gPad.SetLogz(); ROOT.gPad.SetPad(XMin, YMin, XMax, YMax)

            ROOT.gPad.SetTopMargin(0.03)
            ROOT.gPad.SetLeftMargin(0.11)
            ROOT.gPad.SetBottomMargin(0.01)
            ROOT.gPad.SetRightMargin(0.12)

            mapPFAhistos["PFAX1"][name].SetContour(255)
            mapPFAhistos["PFAX1"][name].GetYaxis().SetRangeUser(0.1,2)
            mapPFAhistos["PFAX1"][name].GetZaxis().SetRangeUser(1,zMax)
            prettyHisto(mapPFAhistos["PFAX1"][name])
            mapPFAhistos["PFAX1"][name].Draw("colz")

            pPFAY = prettyProfile(mapPFAhistos["PFAY"][name],ROOT.kBlack,4,"PFAY")
            pPFAY.Draw("EP SAME")
            pPFAX1 = prettyProfile(mapPFAhistos["PFAX1"][name],ROOT.kBlack,20,"PFAX1")
            pPFAX1.Draw("EP SAME")

            l.Draw("SAME")

            c1.cd(2)

            ROOT.gPad.SetGridy()
            ROOT.gPad.SetTopMargin(0.05)
            ROOT.gPad.SetBottomMargin(0.26)
            ROOT.gPad.SetRightMargin(0.12)
            ROOT.gPad.SetLeftMargin(0.11)
            ROOT.gPad.SetPad(RatioXMin, RatioYMin, RatioXMax, RatioYMax)

            ratio = ROOT.TH1F("ratio_%s"%(name), "ratio_%s"%(name), pPFAX1.GetNbinsX(), pPFAX1.GetXaxis().GetXmin(), pPFAX1.GetXaxis().GetXmax()) 
            ratio.SetTitle("")
            for xbin in xrange(0,ratio.GetNbinsX()):
                if pPFAX1.GetBinContent(xbin+1) != 0:
                    content = (pPFAY.GetBinContent(xbin+1) - pPFAX1.GetBinContent(xbin+1))/pPFAY.GetBinContent(xbin+1)
                    ratio.SetBinContent(xbin+1, content)
            
            ratio.SetMinimum(-0.5)
            ratio.SetMaximum(0.5)
            ratio.GetYaxis().SetNdivisions(-304)
            ratio.GetYaxis().SetTitle("#frac{PFAX}{PFAY} - 1")
            ratio.GetXaxis().SetTitle("i#eta")
            ratio.SetMarkerStyle(20); ratio.SetMarkerSize(2); ratio.SetMarkerColor(ROOT.kBlue+2)
            ratio.SetLineWidth(2); ratio.SetLineColor(ROOT.kBlue+2)

            prettyHisto(ratio,PadFactor)

            ratio.Draw("EP")
            c1.SaveAs("%s/%s.pdf"%(outpath,name))
