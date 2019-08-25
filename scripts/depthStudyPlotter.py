import os
import sys
import ROOT
import multiprocessing

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetLineWidth(4)
ROOT.gStyle.SetFrameLineWidth(4)
ROOT.gStyle.SetPaintTextFormat("3.2f")

def drawHistos(histoMap, tag, pfa):
    # Save the final histograms
    for name, histo in histoMap.iteritems():

        if "TH1" in histo.__class__.__name__: continue
        
        prettyHisto(histo)

        c1 = ROOT.TCanvas("c1", "c1", 2400, 1200); c1.cd();
        #c1.SetLogz()

        ROOT.gPad.SetTopMargin(0.025)
        ROOT.gPad.SetLeftMargin(0.05)
        ROOT.gPad.SetRightMargin(0.12)
        histo.SetContour(255)
        if "TH2" in histo.__class__.__name__:
            histo.Draw("COLZ TEXT89")
        elif "TH3" in histo.__class__.__name__:
            histo.Draw("BOX2Z")

        c1.SaveAs("plots/%s/depth/%s/depth_ieta_et_%s.png"%(tag,pfa,name))

def drawCompPU(puHistoDict, noPUHistoDict, tag, pfa):

    etBin = "0.5to10"
    puHistoVec = puHistoDict.values()
    noPUHistoVec = noPUHistoDict.values()

    for i in xrange(len(puHistoVec)):

        if not "TH1" in puHistoVec[i].__class__.__name__: continue
        if etBin not in puHistoVec[i].GetName(): continue

        special = puHistoVec[i].GetName().split("_")[-1]

        for j in xrange(len(noPUHistoVec)):

            if etBin not in noPUHistoVec[j].GetName(): continue
            if special not in noPUHistoVec[j].GetName(): continue
            else:

                c1 = ROOT.TCanvas("c1", "c1", 1200, 1200); c1.cd();
                ROOT.gPad.SetTopMargin(0.02)
                ROOT.gPad.SetLeftMargin(0.08)
                ROOT.gPad.SetRightMargin(0.01)
                ROOT.gPad.SetBottomMargin(0.12)

                puHistoVec[i].SetLineColor(ROOT.kRed); puHistoVec[i].SetLineWidth(9)
                noPUHistoVec[j].SetLineColor(ROOT.kBlack); noPUHistoVec[j].SetLineWidth(9)

                puHistoVec[i].SetMarkerSize(3); puHistoVec[i].SetMarkerStyle(20); puHistoVec[i].SetMarkerColor(ROOT.kRed)
                noPUHistoVec[j].SetMarkerSize(3); noPUHistoVec[j].SetMarkerStyle(20); noPUHistoVec[j].SetMarkerColor(ROOT.kBlack)

                someText = ROOT.TPaveText(0.68, 0.54, 0.97, 0.76, "trNDC")
                someText.AddText("|ieta| = %s"%(special[4:]))
                someText.SetFillColor(ROOT.kWhite)
                iamLegend = ROOT.TLegend(0.68, 0.74, 0.97, 0.96, "", "trNDC")
                iamLegend.AddEntry(noPUHistoVec[j], "0PU", "LP")
                iamLegend.AddEntry(puHistoVec[i], "50PU", "LP")
                iamLegend.SetTextSize(0.05)
                iamLegend.SetBorderSize(0)

                puHistoVec[i].SetMinimum(0)
                puHistoVec[i].SetMaximum(1)

                puHistoVec[i].GetYaxis().SetLabelSize(0.055); 
                puHistoVec[i].GetXaxis().SetLabelSize(0.055); puHistoVec[i].GetXaxis().SetTitleSize(0.065); puHistoVec[i].GetXaxis().SetTitleOffset(0.9)


                puHistoVec[i].Draw("HIST P");
                puHistoVec[i].Draw("][ HIST SAME");
                noPUHistoVec[j].Draw("HIST P SAME")
                noPUHistoVec[j].Draw("][ HIST SAME")
                iamLegend.Draw("SAME")
                someText.Draw("SAME")

                c1.SaveAs("plots/%s/depth/%s/depth_comp_0PUto50PU_%s.png"%(tag,pfa,special))

                break

def combineHistos(histoMap, outRootDir):
    for histoFile in os.listdir(outRootDir):

        histoFile = ROOT.TFile.Open(outRootDir + "/" + histoFile, "READ")
        for hkey in histoFile.GetListOfKeys():
            if "TH" not in hkey.GetClassName(): continue

            name = hkey.GetName()
            histo = hkey.ReadObj()
            histo.SetDirectory(0)
            
            if name in histoMap.keys(): histoMap[name].Add(histo)
            else: histoMap[name] = histo

def ietaRingProjection(histo2D, ietaRing):

    projHisto = histo2D.ProjectionY(histo2D.GetName()+"_ieta%s"%ietaRing, histo2D.GetXaxis().FindBin(ietaRing), histo2D.GetXaxis().FindBin(ietaRing)+1)
    projHisto.Add(histo2D.ProjectionY(histo2D.GetName()+"_ieta-%s"%(ietaRing), histo2D.GetXaxis().FindBin(-1*ietaRing), histo2D.GetXaxis().FindBin(-1*ietaRing)+1))

    if projHisto.Integral() > 0:
        projHisto.Scale(1./projHisto.Integral())
    projHisto.SetTitle("")
    projHisto.GetXaxis().SetTitle("Depth")

    return projHisto

def prettyHisto(histo):
    histo.GetYaxis().SetLabelSize(0.045); histo.GetYaxis().SetTitleSize(0.055); histo.GetYaxis().SetTitleOffset(0.4)
    histo.GetXaxis().SetLabelSize(0.045); histo.GetXaxis().SetTitleSize(0.055); histo.GetXaxis().SetTitleOffset(0.8)
    histo.GetZaxis().SetLabelSize(0.045); histo.GetZaxis().SetTitleSize(0.055); histo.GetZaxis().SetTitleOffset(0.6)

    histo.GetYaxis().SetTickLength(0.0)
    histo.GetYaxis().SetNdivisions(7)
    if type(histo) is ROOT.TH1D: histo.SetLineWidth(2)

def fillHistos(puFileOut, noPuFileOut, puTree, noPuTree, etBin):

    if etBin[1] == "Inf": etReq = "(etsum > %s)"%(etBin[0])
    else:  etReq = "(etsum > %s && etsum <= %s)"%(etBin[0], etBin[1])

    noPUName = "noPUHistoET_%sto%s"%(etBin[0],etBin[1])
    puName = "puHistoET_%sto%s"%(etBin[0],etBin[1])
    ratioName = "ratioHistoET_%sto%s"%(etBin[0],etBin[1])
    ratioProfName = "ratioHistoProfET_%sto%s"%(etBin[0],etBin[1])
    diffName = "diffHistoET_%sto%s"%(etBin[0],etBin[1])
    diffProfName = "diffHistoProfET_%sto%s"%(etBin[0],etBin[1])

    noPUHistoET = ROOT.TH2F(noPUName, noPUName, 57, -28.5, 28.5, 7, 0.5, 7.5)
    noPuTree.Draw("depth:ieta>>"+noPUName, "et*(et > 0 && %s)"%(etReq)) 
    noPUHistoET = ROOT.gDirectory.Get(noPUName)
    noPUHistoET.SetDirectory(0)

    noPUHistoET.SetTitle("")
    noPUHistoET.GetXaxis().SetTitle("i#eta")
    noPUHistoET.GetYaxis().SetTitle("Depth")

    countNoPuHistoET = ROOT.TH2F(noPUName+"count", noPUName+"count", 57, -28.5, 28.5, 7, 0.5, 7.5) 
    noPuTree.Draw("depth:ieta>>"+noPUName+"count", "(et > 0 && %s)"%(etReq))
    countNoPuHistoET = ROOT.gDirectory.Get(noPUName+"count")
    countNoPuHistoET.SetDirectory(0)

    puHistoET = ROOT.TH2F(puName, puName, 57, -28.5, 28.5, 7, 0.5, 7.5) 
    puTree.Draw("depth:ieta>>"+puName, "et*(et > 0 && %s)"%(etReq))
    puHistoET = ROOT.gDirectory.Get(puName)
    puHistoET.SetDirectory(0)

    puHistoET.SetTitle("")
    puHistoET.GetXaxis().SetTitle("i#eta")
    puHistoET.GetYaxis().SetTitle("Depth")

    countPuHistoET = ROOT.TH2F(puName+"count", puName+"count", 57, -28.5, 28.5, 7, 0.5, 7.5) 
    puTree.Draw("depth:ieta>>"+puName+"count", "(et > 0 && %s)"%(etReq))
    countPuHistoET = ROOT.gDirectory.Get(puName+"count")
    countPuHistoET.SetDirectory(0)

    ratioHisto = ROOT.TH2F(ratioName, ratioName, 57, -28.5, 28.5, 7, 0.5, 7.5)
    ratioHisto.SetTitle("")

    ratioHisto.GetXaxis().SetTitle("i#eta")
    ratioHisto.GetYaxis().SetTitle("Depth")
    ratioHisto.GetZaxis().SetTitle("E_{T,50PU} / E_{T,0PU}")
    ratioHisto.GetZaxis().RotateTitle()

    ratioHisto.Divide(puHistoET,noPUHistoET)

    diffHisto = puHistoET.Clone()
    diffHisto.SetName(diffName)
    diffHisto.SetTitle("")
    diffHisto.GetXaxis().SetTitle("i#eta")
    diffHisto.GetYaxis().SetTitle("Depth")
    diffHisto.GetZaxis().SetTitle("E_{T,50PU} - E_{T,0PU}  [GeV]")
    diffHisto.GetZaxis().RotateTitle()

    diffHisto.Add(noPUHistoET,-1.)

    ieta17NoPU = ietaRingProjection(noPUHistoET, 17); ieta17PU = ietaRingProjection(puHistoET, 17)
    ieta18NoPU = ietaRingProjection(noPUHistoET, 18); ieta18PU = ietaRingProjection(puHistoET, 18)
    ieta19NoPU = ietaRingProjection(noPUHistoET, 19); ieta19PU = ietaRingProjection(puHistoET, 19)
    ieta20NoPU = ietaRingProjection(noPUHistoET, 20); ieta20PU = ietaRingProjection(puHistoET, 20)
    ieta21NoPU = ietaRingProjection(noPUHistoET, 21); ieta21PU = ietaRingProjection(puHistoET, 21)
    ieta22NoPU = ietaRingProjection(noPUHistoET, 22); ieta22PU = ietaRingProjection(puHistoET, 22)
    ieta23NoPU = ietaRingProjection(noPUHistoET, 23); ieta23PU = ietaRingProjection(puHistoET, 23)
    ieta24NoPU = ietaRingProjection(noPUHistoET, 24); ieta24PU = ietaRingProjection(puHistoET, 24)
    ieta25NoPU = ietaRingProjection(noPUHistoET, 25); ieta25PU = ietaRingProjection(puHistoET, 25)
    ieta26NoPU = ietaRingProjection(noPUHistoET, 26); ieta26PU = ietaRingProjection(puHistoET, 26)
    ieta27NoPU = ietaRingProjection(noPUHistoET, 27); ieta27PU = ietaRingProjection(puHistoET, 27)
    ieta28NoPU = ietaRingProjection(noPUHistoET, 28); ieta28PU = ietaRingProjection(puHistoET, 28)

    noPuFileOut.cd()
    noPUHistoET.Write()
    ieta17NoPU.Write()
    ieta18NoPU.Write()
    ieta19NoPU.Write()
    ieta20NoPU.Write()
    ieta21NoPU.Write()
    ieta22NoPU.Write()
    ieta23NoPU.Write()
    ieta24NoPU.Write()
    ieta25NoPU.Write()
    ieta26NoPU.Write()
    ieta27NoPU.Write()
    ieta28NoPU.Write()

    puFileOut.cd()
    puHistoET.Write()
    diffHisto.Write()
    ratioHisto.Write()
    ieta17PU.Write()
    ieta18PU.Write()
    ieta19PU.Write()
    ieta20PU.Write()
    ieta21PU.Write()
    ieta22PU.Write()
    ieta23PU.Write()
    ieta24PU.Write()
    ieta25PU.Write()
    ieta26PU.Write()
    ieta27PU.Write()
    ieta28PU.Write()

def analysis(aFilePair):

    if not aFilePair[0].endswith(".root") or not aFilePair[1].endswith(".root"): return
    if "SIM" in aFilePair[0] or "SIM" in aFilePair[1]: return

    puStub = aFilePair[1].split("/")[-1].split(".root")[0]
    outFilePU = ROOT.TFile.Open("%s/%s_plots.root"%(outRootDirPU,puStub), "RECREATE")

    noPuStub = aFilePair[0].split("/")[-1].split(".root")[0]
    outFileNoPU = ROOT.TFile.Open("%s/%s_plots.root"%(outRootDirNoPU,noPuStub), "RECREATE")

    inFilePU = ROOT.TFile.Open(aFilePair[1], "READ")
    evtsTreePU = inFilePU.Get("compareReemulRecoSeverity9/tpsplit")

    inFileNoPU = ROOT.TFile.Open(aFilePair[0], "READ")
    evtsTreeNoPU = inFileNoPU.Get("compareReemulRecoSeverity9/tpsplit")

    fillHistos(outFilePU, outFileNoPU, evtsTreePU, evtsTreeNoPU, ["0.5","10"])
    fillHistos(outFilePU, outFileNoPU, evtsTreePU, evtsTreeNoPU, ["10","30"])
    fillHistos(outFilePU, outFileNoPU, evtsTreePU, evtsTreeNoPU, ["30","Inf"])
    
    inFilePU.Close(); outFilePU.Close()
    inFileNoPU.Close(); outFileNoPU.Close()

if __name__ == '__main__':

    pfa = sys.argv[1]; noPUDir = sys.argv[2]; PUDir = sys.argv[3]

    onEOS = "eos" in noPUDir

    noPUDirEOS = noPUDir.replace("/eos/uscms/", "root://cmseos.fnal.gov//")
    PUDirEOS =   PUDir.replace("/eos/uscms/", "root://cmseos.fnal.gov//")

    outRootDirNoPU = "./plots/0PU/depth/PFA%s/root"%(pfa)
    if not os.path.exists(outRootDirNoPU): os.makedirs(outRootDirNoPU)

    outRootDirPU = "./plots/50PU/depth/PFA%s/root"%(pfa)
    if not os.path.exists(outRootDirPU): os.makedirs(outRootDirPU)

    print "Processing root files"
    if onEOS:
        puFilesList = [PUDirEOS + "/" + aFile for aFile in os.listdir(PUDir)]
        noPUFilesList = [noPUDirEOS + "/" + aFile for aFile in os.listdir(noPUDir)]
    else:
        puFilesList = [PUDir + "/" + aFile for aFile in os.listdir(PUDir)]
        noPUFilesList = [noPUDir + "/" + aFile for aFile in os.listdir(noPUDir)]

    filePairsList = []
    for i in xrange(len(puFilesList)):
        filePairsList.append([noPUFilesList[i], puFilesList[i]])

    pool = multiprocessing.Pool(processes=8)
    results = pool.map(analysis, filePairsList)

    puHistoMap = {}
    noPUHistoMap = {}

    combineHistos(puHistoMap, outRootDirPU)
    combineHistos(noPUHistoMap, outRootDirNoPU)

    drawHistos(puHistoMap, "50PU", "PFA%s"%(pfa))
    drawHistos(noPUHistoMap, "0PU", "PFA%s"%(pfa))

    drawCompPU(puHistoMap, noPUHistoMap, "50PU", "PFA%s"%(pfa))
