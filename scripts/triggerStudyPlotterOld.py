import sys
import os
import ROOT
import multiprocessing

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetLineWidth(4)
ROOT.gStyle.SetFrameLineWidth(4)

# Run 317279
ISO_317279 = "(bx==858 || bx==2643)"
POST_317279 = "(bx==1 || bx==189 || bx==244 || bx==455 || bx==510 || bx==565 || bx==1071 || bx==1126 || bx==1337 || bx==1392 || bx==1447 || bx==1965 || bx==2020 || bx==2231 || bx==2286 || bx==2341 || bx==2859 || bx==2914 || bx==3125 || bx==3180 || bx==3235)"
PRE_317279 = "(bx==12 || bx==236 || bx==291 || bx==502 || bx==557 || bx==612 || bx==1118 || bx==1173 || bx==1384 || bx==1439 || bx==1494 || bx==2012 || bx==2067 || bx==2278 || bx==2333 || bx==2388 || bx==2906 || bx==2961 || bx==3172 || bx==3227 || bx==3282)"
NONISO_317279 = "(!%s && !%s && !%s)"%(PRE_317279,POST_317279,ISO_317279)
INC_317279 = "(bx>0)"

def prettyHisto(histo):
    histo.GetYaxis().SetLabelSize(0.045); histo.GetYaxis().SetTitleSize(0.055); histo.GetYaxis().SetTitleOffset(0.8)
    histo.GetXaxis().SetLabelSize(0.045); histo.GetXaxis().SetTitleSize(0.055); histo.GetXaxis().SetTitleOffset(0.8)
    histo.GetZaxis().SetLabelSize(0.045); histo.GetZaxis().SetTitleSize(0.055)

    if type(histo) is ROOT.TH1D: histo.SetLineWidth(2)

def ratioTPVsRH_Eta_ET(evtsTree, tpAlgo, recHit, bx = "(bx > 0)"):

    h3 = ROOT.TH3F("h3_%d%d_ET"%(tpAlgo,recHit), "h3_%d%d_ET"%(tpAlgo,recHit), 57, -28.5, 28.5, 28, 0., 3.5, 200, -0.25, 99.75)

    evtsTree.Draw("TP_energy:TP_energy/RH_energyM%d:ieta>>h3_%d%d_ET"%(recHit,tpAlgo,recHit), "tp_soi!=255 && RH_energyM%d>0 && %s"%(recHit, bx))

    h3 = ROOT.gDirectory.Get("h3_%d%d_ET"%(tpAlgo,recHit))

    return h3

def ratioTPVsRH_Eta(outfile, histo, tag = "INC_BX", tpET = []):

    outfile.cd()
    tpAlgo = histo.GetName().split("_")[1][0]
    recHit = histo.GetName().split("_")[1][1]

    h2 = 0
    if len(tpET) == 0:
        h2 = histo.Project3D("yx")
    elif len(tpET) == 1:
        histo.GetZaxis().SetRangeUser(tpET[0],tpET[0])
        histo.GetZaxis().SetBit(ROOT.TAxis.kAxisRange)
        h2 = histo.Project3D("yx")
    elif len(tpET) == 2:
        histo.GetZaxis().SetRangeUser(tpET[0],tpET[1])
        histo.GetZaxis().SetBit(ROOT.TAxis.kAxisRange)
        h2 = histo.Project3D("yx")

    h2.SetTitle("")
    h2.GetXaxis().SetTitle("i#eta")
    h2.GetYaxis().SetTitle("E_{T,TP} / E_{T,RH}")

    if len(tpET) == 0:
        h2.Write("Ratio_PFA%s-RH%s_vs_Eta_%s"%(tpAlgo,recHit,tag))
    elif len(tpET) == 1:
        h2.Write("Ratio_PFA%s-RH%s_vs_Eta_tpET%0.2g_%s"%(tpAlgo,recHit,tpET[0],tag))
    elif len(tpET) == 2:
        h2.Write("Ratio_PFA%s-RH%s_vs_Eta_tpET%0.2g-%0.2g_%s"%(tpAlgo,recHit,tpET[0],tpET[1],tag))

def ratioTPVsRH_ET_Eta(evtsTree, tpAlgo, recHit, bx = "(bx > 0)"):

    h3 = ROOT.TH3F("h3_%d%d_eta"%(tpAlgo,recHit), "h3_%d%d_eta"%(tpAlgo,recHit), 50, 0.25, 25.25, 25, 0., 2.0, 62, -31.5, 30.5)

    evtsTree.Draw("abs(ieta):TP_energy/RH_energyM%d:TP_energy>>h3_%d%d_eta"%(recHit,tpAlgo,recHit), "tp_soi!=255 && RH_energyM%d>0 && TP_energy>0.5 && %s"%(recHit, bx))
       
    h3 = ROOT.gDirectory.Get("h3_%d%d_eta"%(tpAlgo,recHit))

    return h3

def ratioTPVsRH_ET(outfile, histo, tpAlgo, recHit, ieta = []):

    outfile.cd()

    h2 = 0
    if len(ieta) == 0:
        h2 = histo.Project3D("yx")
    elif len(ieta) == 1:
        histo.GetZaxis().SetRangeUser(ieta[0],ieta[0])
        histo.GetZaxis().SetBit(ROOT.TAxis.kAxisRange)
        h2 = histo.Project3D("yx")
    elif len(ieta) == 2:
        histo.GetZaxis().SetRangeUser(ieta[0],ieta[1])
        histo.GetZaxis().SetBit(ROOT.TAxis.kAxisRange)
        h2 = histo.Project3D("yx")

    h2.SetTitle("")
    h2.GetXaxis().SetTitle("E_{T,TP}")
    h2.GetYaxis().SetTitle("E_{T,TP} / E_{T,RH}")

    if len(ieta) == 0:
        h2.Write("Ratio_PFA%s-RH%s_vs_ET"%(tpAlgo,recHit))
    elif len(ieta) == 1:
        h2.Write("Ratio_PFA%s-RH%s_vs_ET_ieta%d"%(tpAlgo,recHit,ieta[0]))
    elif len(ieta) == 2:
        h2.Write("Ratio_PFA%s-RH%s_vs_ET_ieta%d-%d"%(tpAlgo,recHit,ieta[0],ieta[1]))

def analysis(aFilePair):

        print "Reading in files: " + str(aFilePair)
        stub = aFilePair[0].split("/")[-1].split(".root")[0]
        outFile = ROOT.TFile.Open("%s/%s_plots.root"%(outRootDir,stub), "RECREATE")

        fPFA2 = ROOT.TFile.Open(aFilePair[0], "READ")
        tPFA2 = fPFA2.Get("compareReemulRecoSeverity9/matches")

        fPFA3 = ROOT.TFile.Open(aFilePair[1], "READ")
        tPFA3 = fPFA3.Get("compareReemulRecoSeverity9/matches")

        # Make some plots
        ETvRatiovEta_20_ISO = ratioTPVsRH_Eta_ET(tPFA2,2,0,ISO_317279); ETvRatiovEta_20_ISO.SetDirectory(0)
        ETvRatiovEta_22_ISO = ratioTPVsRH_Eta_ET(tPFA2,2,2,ISO_317279); ETvRatiovEta_22_ISO.SetDirectory(0)
        ETvRatiovEta_32_ISO = ratioTPVsRH_Eta_ET(tPFA3,3,2,ISO_317279); ETvRatiovEta_32_ISO.SetDirectory(0)

        ETvRatiovEta_20_PRE = ratioTPVsRH_Eta_ET(tPFA2,2,0,PRE_317279); ETvRatiovEta_20_PRE.SetDirectory(0)
        ETvRatiovEta_22_PRE = ratioTPVsRH_Eta_ET(tPFA2,2,2,PRE_317279); ETvRatiovEta_22_PRE.SetDirectory(0)
        ETvRatiovEta_32_PRE = ratioTPVsRH_Eta_ET(tPFA3,3,2,PRE_317279); ETvRatiovEta_32_PRE.SetDirectory(0)

        ETvRatiovEta_20_POST = ratioTPVsRH_Eta_ET(tPFA2,2,0,POST_317279); ETvRatiovEta_20_POST.SetDirectory(0)
        ETvRatiovEta_22_POST = ratioTPVsRH_Eta_ET(tPFA2,2,2,POST_317279); ETvRatiovEta_22_POST.SetDirectory(0)
        ETvRatiovEta_32_POST = ratioTPVsRH_Eta_ET(tPFA3,3,2,POST_317279); ETvRatiovEta_32_POST.SetDirectory(0)

        ETvRatiovEta_20_NONISO = ratioTPVsRH_Eta_ET(tPFA2,2,0,NONISO_317279); ETvRatiovEta_20_NONISO.SetDirectory(0)
        ETvRatiovEta_22_NONISO = ratioTPVsRH_Eta_ET(tPFA2,2,2,NONISO_317279); ETvRatiovEta_22_NONISO.SetDirectory(0)
        ETvRatiovEta_32_NONISO = ratioTPVsRH_Eta_ET(tPFA3,3,2,NONISO_317279); ETvRatiovEta_32_NONISO.SetDirectory(0)

        fPFA2.Close(); fPFA3.Close()

        ratioTPVsRH_Eta(outFile,ETvRatiovEta_20_ISO,"ISO",[1,10])
        ratioTPVsRH_Eta(outFile,ETvRatiovEta_22_ISO,"ISO",[1,10])
        ratioTPVsRH_Eta(outFile,ETvRatiovEta_32_ISO,"ISO",[1,10])

        ratioTPVsRH_Eta(outFile,ETvRatiovEta_20_PRE,"PRE",[1,10])
        ratioTPVsRH_Eta(outFile,ETvRatiovEta_22_PRE,"PRE",[1,10])
        ratioTPVsRH_Eta(outFile,ETvRatiovEta_32_PRE,"PRE",[1,10])

        ratioTPVsRH_Eta(outFile,ETvRatiovEta_20_POST,"POST",[1,10])
        ratioTPVsRH_Eta(outFile,ETvRatiovEta_22_POST,"POST",[1,10])
        ratioTPVsRH_Eta(outFile,ETvRatiovEta_32_POST,"POST",[1,10])

        ratioTPVsRH_Eta(outFile,ETvRatiovEta_20_NONISO,"NONISO",[1,10])
        ratioTPVsRH_Eta(outFile,ETvRatiovEta_22_NONISO,"NONISO",[1,10])
        ratioTPVsRH_Eta(outFile,ETvRatiovEta_32_NONISO,"NONISO",[1,10])

        outFile.Close()

        print "Done reading in files: " + str(aFilePair)

   
if __name__ == '__main__':

    run = str(sys.argv[1])
    PFA2Dir = "/eos/uscms/store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/%s/PFA2"%(run) 
    PFA3Dir = "/eos/uscms/store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/%s/PFA3"%(run) 

    PFA2DirEOS = "root://cmseos.fnal.gov//store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/%s/PFA2"%(run) 
    PFA3DirEOS = "root://cmseos.fnal.gov//store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/%s/PFA3"%(run) 

    outRootDir = "./plots/%s/root"%(run)
    if not os.path.exists(outRootDir): os.makedirs(outRootDir)

    # Pair up PFA2 and PFA3 files and add to list
    filePairList = []
    for aFile in os.listdir(PFA2Dir):

        aName = aFile.split(".root")[0]

        if os.path.isfile(PFA3Dir + "/" + aFile):
            filePairList.append([PFA2DirEOS + "/" + aFile, PFA3DirEOS + "/" + aFile])
    
    print "Processing root files"
    pool = multiprocessing.Pool(processes=20)
    results = pool.map(analysis, filePairList)

    print "Making final histograms"
    # hadd the histo files together
    histoMap = {}
    for histoFile in os.listdir(outRootDir):

        
        histoFile = ROOT.TFile.Open(outRootDir + "/" + histoFile, "READ")
        for hkey in histoFile.GetListOfKeys():
            if "TH" not in hkey.GetClassName(): continue

            name = hkey.GetName()
            histo = hkey.ReadObj()
            histo.SetDirectory(0)
            
            if name in histoMap.keys(): histoMap[name].Add(histo)
            else: histoMap[name] = histo

    # Save the final histograms
    for name, histo in histoMap.iteritems():
        
        # Make the histo pretty
        prettyHisto(histo)

        c1 = ROOT.TCanvas("%s"%(name), "%s"%(name), 2400, 1200); c1.cd(); c1.SetLogz()
        ROOT.gPad.SetTopMargin(0.025)

        histo.SetContour(255)
        histo.Draw("colz")

        p1 = histo.ProfileX("p1", 1, -1)
        p1.SetMarkerStyle(20)
        p1.SetMarkerSize(2)
        p1.SetLineWidth(0)
        p1.SetMarkerColor(ROOT.kBlack)
        p1.Draw("P SAME")

        c1.SaveAs("plots/%s/%s.png"%(run,name))
