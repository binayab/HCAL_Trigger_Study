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

def prettyHisto(histo,magicFactor=1.0,magicFactor2=1.0):
    histo.GetYaxis().SetLabelSize(magicFactor*0.055); histo.GetYaxis().SetTitleSize(magicFactor*0.06); histo.GetYaxis().SetTitleOffset(0.9/magicFactor)
    histo.GetXaxis().SetLabelSize(magicFactor*0.055); histo.GetXaxis().SetTitleSize(magicFactor*0.08); histo.GetXaxis().SetTitleOffset(0.5/magicFactor2)
    histo.GetZaxis().SetLabelSize(magicFactor*0.055); histo.GetZaxis().SetTitleSize(magicFactor*0.06)

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
            if "RHET" in name: zMax = 6e3
            else: zMax = 5e3
            
            l = ROOT.TLine(-28.5, 1, 28.5, 1)
            l.SetLineWidth(2)
            l.SetLineColor(ROOT.kBlack)
            l.SetLineStyle(2)

            c1 = ROOT.TCanvas("%s"%(name), "%s"%(name), XCANVAS, int(0.8*YCANVAS)); c1.cd(); c1.SetLogz()

            ROOT.gPad.SetTopMargin(0.02625)
            ROOT.gPad.SetBottomMargin(0.13375)
            ROOT.gPad.SetLeftMargin(0.11)
            ROOT.gPad.SetRightMargin(0.12)

            drewRatio = False
            if "PFAX1" in mapPFAhistos:
                pPFAX1 = prettyProfile(mapPFAhistos["PFAX1"][name],name,ROOT.kBlack,20,"PFAX1")
                prettyHisto(mapPFAhistos["PFAX1"][name],0.875,0.8)
                if not drewRatio:
                    mapPFAhistos["PFAX1"][name].SetContour(255)
                    mapPFAhistos["PFAX1"][name].GetYaxis().SetRangeUser(0.1,2.)
                    mapPFAhistos["PFAX1"][name].GetZaxis().SetRangeUser(1,zMax)
                    mapPFAhistos["PFAX1"][name].Draw("COLZ")
                    drewRatio = True
                pPFAX1.Draw("EP SAME")
            if "PFAX2" in mapPFAhistos:
                pPFAX2 = prettyProfile(mapPFAhistos["PFAX2"][name],name,ROOT.kRed,20,"PFAX2")
                prettyHisto(mapPFAhistos["PFAX2"][name],0.875,0.8)
                if not drewRatio:
                    mapPFAhistos["PFAX2"][name].SetContour(255)
                    mapPFAhistos["PFAX2"][name].GetYaxis().SetRangeUser(0.1,2.)
                    mapPFAhistos["PFAX2"][name].GetZaxis().SetRangeUser(1,zMax)
                    mapPFAhistos["PFAX2"][name].Draw("COLZ")
                    drewRatio = True
                pPFAX2.Draw("EP SAME")
            if "PFAY" in mapPFAhistos:
                prettyHisto(mapPFAhistos["PFAY"][name],0.875,0.8)
                pPFAY = prettyProfile(mapPFAhistos["PFAY"][name],name,ROOT.kBlack,4,"PFAY")
                pPFAY.Draw("EP SAME")

            l.Draw("SAME")

            c1.SaveAs("%s/%s.pdf"%(outpath,name))

        elif "TH1" in mapPFAhistos.values()[0][name].ClassName():

            c1 = ROOT.TCanvas("%s"%(name), "%s"%(name), 1600, 1600); c1.cd()
            c1.SetGridy(); c1.SetGridx()
            ROOT.gPad.SetTopMargin(0.02)
            ROOT.gPad.SetBottomMargin(0.12)
            ROOT.gPad.SetLeftMargin(0.11)
            ROOT.gPad.SetRightMargin(0.02)

            if "PFAX1" in mapPFAhistos:

                algoName = arg.pfaX1.split("/")[3]

                mapPFAhistos["PFAX1"][name].Rebin(2)
                mapPFAhistos["PFAX1"][name].Scale(1./mapPFAhistos["PFAX1"][name].Integral())

                mapPFAhistos["PFAX1"][name].GetXaxis().SetRangeUser(0.,4.)
                mapPFAhistos["PFAX1"][name].SetLineColor(ROOT.kBlack)
                mapPFAhistos["PFAX1"][name].SetLineWidth(4)
                prettyHisto(mapPFAhistos["PFAX1"][name],0.65,0.5)
                mapPFAhistos["PFAX1"][name].Draw("HIST")

                someTextPFAX1 = ROOT.TPaveText(0.70, 0.75, 0.9, 0.9, "trNDC")
                someTextPFAX1.SetFillColor(ROOT.kWhite);
                someTextPFAX1.SetTextAlign(11)
                someTextPFAX1.AddText(algoName)
                someTextPFAX1.AddText("#mu = %3.2f"%(mapPFAhistos["PFAX1"][name].GetMean()))
                someTextPFAX1.AddText("#sigma = %3.2f"%(mapPFAhistos["PFAX1"][name].GetStdDev()))
                someTextPFAX1.SetTextColor(ROOT.kBlack)
                someTextPFAX1.Draw("SAME")

            if "PFAY" in mapPFAhistos:
                algoName = arg.pfaY.split("/")[3]

                mapPFAhistos["PFAY"][name].Rebin(2)
                mapPFAhistos["PFAY"][name].Scale(1./mapPFAhistos["PFAY"][name].Integral())
                mapPFAhistos["PFAY"][name].GetXaxis().SetRangeUser(0.,4.)
                mapPFAhistos["PFAY"][name].SetLineColor(ROOT.kGray+2)
                mapPFAhistos["PFAY"][name].SetLineWidth(4)
                prettyHisto(mapPFAhistos["PFAY"][name],0.65,0.6)
                mapPFAhistos["PFAY"][name].Draw("HIST SAME")

                someTextPFAY = ROOT.TPaveText(0.7, 0.39, 0.9, 0.54, "trNDC")
                someTextPFAY.SetFillColor(ROOT.kWhite);
                someTextPFAY.SetTextAlign(11)
                someTextPFAY.AddText(algoName)
                someTextPFAY.AddText("#mu = %3.2f"%(mapPFAhistos["PFAY"][name].GetMean()))
                someTextPFAY.AddText("#sigma = %3.2f"%(mapPFAhistos["PFAY"][name].GetStdDev()))
                someTextPFAY.SetTextColor(ROOT.kGray+2)
                someTextPFAY.Draw("SAME")

            if "PFAX2" in mapPFAhistos:
                algoName = arg.pfaX2.split("/")[3]

                mapPFAhistos["PFAX2"][name].Rebin(2)
                mapPFAhistos["PFAX2"][name].Scale(1./mapPFAhistos["PFAX2"][name].Integral())
                mapPFAhistos["PFAX2"][name].GetXaxis().SetRangeUser(0.,4.)
                mapPFAhistos["PFAX2"][name].SetLineColor(ROOT.kRed)
                mapPFAhistos["PFAX2"][name].SetLineWidth(4)
                prettyHisto(mapPFAhistos["PFAX2"][name],0.65,0.5)
                mapPFAhistos["PFAX2"][name].Draw("HIST SAME")

                someTextPFAX2 = ROOT.TPaveText(0.7, 0.57, 0.9, 0.72, "trNDC")
                someTextPFAX2.SetFillColor(ROOT.kWhite);
                someTextPFAX2.SetTextAlign(11)
                someTextPFAX2.AddText(algoName)
                someTextPFAX2.AddText("#mu = %3.2f"%(mapPFAhistos["PFAX2"][name].GetMean()))
                someTextPFAX2.AddText("#sigma = %3.2f"%(mapPFAhistos["PFAX2"][name].GetStdDev()))
                someTextPFAX2.SetTextColor(ROOT.kRed)
                someTextPFAX2.Draw("SAME")

            c1.SaveAs("%s/%s.pdf"%(outpath,name))
