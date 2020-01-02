import sys, os, ROOT, argparse

ROOT.TH1.SetDefaultSumw2()
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetLineWidth(4)
ROOT.gStyle.SetPaintTextFormat("3.2f")
ROOT.gStyle.SetFrameLineWidth(4)
ROOT.gStyle.SetErrorX(0)

usage = "usage: %prog [options]"
parser = argparse.ArgumentParser(usage)
parser.add_argument("--tag"     , dest="tag"     , help="Unique tag for output"    , type=str, default="")
parser.add_argument("--pfaY", dest="pfaY", type=str, help="Path to inputs for PFAY", default="NULL")
parser.add_argument("--pfaX1", dest="pfaX1", help="Path to other PFAX dir", default="NULL", type=str) 
parser.add_argument("--pfaX2", dest="pfaX2", help="Path to other PFAX dir", default="NULL", type=str) 

arg = parser.parse_args()

optionsMap = {"h_jetptmax"        : {"X" : {"rebin" : 5, "min" : 0, "max" : 1000, "title" : "Max Jet p_{T} [GeV]"}},
              "h_jetpt"           : {"X" : {"rebin" : 5, "min" : 0, "max" : 1000, "title" : "Jet p_{T} [GeV]"}},
              "h_ht"              : {"X" : {"rebin" : 5, "min" : 0, "max" : 2500, "title" : "H_{T} [GeV]"}},
              "h_nb"              : {"X" : {"rebin" : 1,                          "title" : "N b-tagged Jets"}},
              "h_lvMET_cm_pt"     : {"X" : {"rebin" : 1, "min" : 0, "max" : 1000, "title" : "p_{T} [GeV]"}},
              "h_met"             : {"X" : {"rebin" : 4, "min" : 0, "max" : 600, "title" : "MET [GeV]"}},
              "h_electron_etaphi" : {"X" : {"rebin" : 360, "title" : "#eta"}, "Y" : {"rebin" : 80, "title" : "#phi"}},
              "h_muon_etaphi"     : {"X" : {"rebin" : 360, "title" : "#eta"}, "Y" : {"rebin" : 80, "title" : "#phi"}},
              "h_fwm2_top6"       : {"X" : {"rebin" : 30}},
              "h_fwm3_top6"       : {"X" : {"rebin" : 30}},
              "h_fwm4_top6"       : {"X" : {"rebin" : 30}},
              "h_fwm5_top6"       : {"X" : {"rebin" : 30}},
              "h_fwm6_top6"       : {"X" : {"rebin" : 30}},
              "h_fwm7_top6"       : {"X" : {"rebin" : 30}},
              "h_fwm8_top6"       : {"X" : {"rebin" : 30}},
              "h_fwm9_top6"       : {"X" : {"rebin" : 30}},
              "h_fwm10_top6"      : {"X" : {"rebin" : 30}},
              "h_jmt_ev0_top6"    : {"X" : {"rebin" : 30}},
              "h_jmt_ev1_top6"    : {"X" : {"rebin" : 30}},
              "h_jmt_ev2_top6"    : {"X" : {"rebin" : 30}},
              "h_lvMET_cm_m"      : {"X" : {"rebin" : 30, "title" : "Mass [GeV]"}},
              "h_lvMET_cm_phi"    : {"X" : {"rebin" : 30, "title" : "#phi"}},
              "h_lvMET_cm_eta"    : {"X" : {"rebin" : 30, "title" : "#eta"}},
              "h_lvMET_cm_pt"     : {"X" : {"rebin" : 30, "title" : "p_{T} [GeV]"}},
              "h_beta_z"          : {"X" : {"rebin" : 30}}
}

def doOptions(histo, histoName, theMap):

    if histoName not in theMap: return

    is1D = "TH1" in histo.ClassName()

    for axis, options in theMap[histoName].iteritems():

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

def prettyHisto(histo,magicFactor=1.0,magicFactor2=1.0):
    histo.GetYaxis().SetLabelSize(magicFactor*0.045); histo.GetYaxis().SetTitleSize(magicFactor*0.051); histo.GetYaxis().SetTitleOffset(1.05/magicFactor)
    histo.GetXaxis().SetLabelSize(magicFactor*0.045); histo.GetXaxis().SetTitleSize(magicFactor*0.051); histo.GetXaxis().SetTitleOffset(0.95/magicFactor2)
    histo.GetZaxis().SetLabelSize(magicFactor*0.045); histo.GetZaxis().SetTitleSize(magicFactor*0.051)

def prettyProfile(histo, name, color, markerStyle, pfa):

    p = histo.ProfileX("p_%s_%s"%(pfa,name), 1, -1, "")
    p.Scale(1.0/p.Integral())
    p.SetMinimum(0); p.SetMaximum(0.95)
    p.GetYaxis().SetTitle("A.U.")
    p.SetMarkerStyle(markerStyle)
    p.SetMarkerSize(7)
    p.SetLineWidth(7)
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

    XCANVAS = 2400; YCANVAS = 2400

    if arg.pfaX1 != "NULL": stub = arg.pfaX1.split("Depths/")[-1]
    elif arg.pfaX2 != "NULL": stub = arg.pfaX2.split("Depths/")[-1]
    else: quit()

    tag = arg.tag

    inRootDirs = {}
    inRootDirs["PFAY"] = arg.pfaY
    inRootDirs["PFAX1"] = arg.pfaX1
    inRootDirs["PFAX2"] = arg.pfaX2
       
    outpath = "./plots/Depths/%s/%s"%(stub,tag)
    if not os.path.exists(outpath): os.makedirs(outpath)

    mapPFAhistos = {}

    fillMap("PFAY",  inRootDirs["PFAY"],  mapPFAhistos)
    fillMap("PFAX1", inRootDirs["PFAX1"], mapPFAhistos)
    fillMap("PFAX2", inRootDirs["PFAX2"], mapPFAhistos)

    # Save the final histograms
    for name in mapPFAhistos.values()[0].keys():

        if "TH2" in mapPFAhistos.values()[0][name].ClassName():

            zMax = 5e4
            
            c1 = ROOT.TCanvas("%s"%(name), "%s"%(name), XCANVAS, YCANVAS); c1.cd(); c1.SetLogz()

            ROOT.gPad.SetLeftMargin(0.12)
            ROOT.gPad.SetRightMargin(0.02)

            someText = ROOT.TPaveText(0.65, 0.62, 0.90, 0.85, "trNDC")
            someText.SetFillColor(ROOT.kWhite);
            someText.SetTextAlign(11)

            drewFirst = False
            if "PFAX1" in mapPFAhistos:
                scenario = arg.pfaX1.split("/")[4]
                algoName = arg.pfaX1.split("/")[3]
                textBlob = algoName + " - " + scenario

                pPFAX1 = prettyProfile(mapPFAhistos["PFAX1"][name],name,ROOT.kBlack,20,"PFAX1")
                prettyHisto(pPFAX1)#,0.875,0.8)
                #if not drewRatio:
                #    mapPFAhistos["PFAX1"][name].SetContour(255)
                #    mapPFAhistos["PFAX1"][name].GetYaxis().SetRangeUser(0,200)
                #    mapPFAhistos["PFAX1"][name].GetZaxis().SetRangeUser(1,zMax)
                #    mapPFAhistos["PFAX1"][name].Draw("COLZ")
                #    drewRatio = True

                someText.AddText(textBlob)
                someText.GetListOfLines().Last().SetTextColor(ROOT.kBlack)

                pPFAX1.Draw("HIST P SAME")
                pPFAX1.Draw("HIST SAME")

            if "PFAX2" in mapPFAhistos:
                scenario = arg.pfaX2.split("/")[4]
                algoName = arg.pfaX2.split("/")[3]
                textBlob = algoName + " - " + scenario

                pPFAX2 = prettyProfile(mapPFAhistos["PFAX2"][name],name,ROOT.kRed,20,"PFAX2")
                prettyHisto(pPFAX2)#,0.875,0.8)
                #if not drewRatio:
                #    mapPFAhistos["PFAX2"][name].SetContour(255)
                #    mapPFAhistos["PFAX2"][name].GetYaxis().SetRangeUser(0,200)
                #    mapPFAhistos["PFAX2"][name].GetZaxis().SetRangeUser(1,zMax)
                #    mapPFAhistos["PFAX2"][name].Draw("COLZ")
                #    drewRatio = True

                someText.AddText(textBlob)
                someText.GetListOfLines().Last().SetTextColor(ROOT.kRed)

                pPFAX2.Draw("HIST P SAME")
                pPFAX2.Draw("HIST SAME")

            if "PFAY" in mapPFAhistos:
                scenario = arg.pfaY.split("/")[4]
                algoName = arg.pfaY.split("/")[3]
                textBlob = algoName + " - " + scenario

                pPFAY = prettyProfile(mapPFAhistos["PFAY"][name],name,ROOT.kGray+1,20,"PFAY")
                prettyHisto(pPFAY)#,0.875,0.8)

                someText.AddText(textBlob)
                someText.GetListOfLines().Last().SetTextColor(ROOT.kGray+1)

                pPFAY.Draw("HIST P SAME")
                pPFAY.Draw("HIST SAME")

            someText.Draw("SAME")
            c1.SaveAs("%s/%s.pdf"%(outpath,name))
