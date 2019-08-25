import sys, os, ROOT, copy, multiprocessing
from functools import partial

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetLineWidth(2)
ROOT.gStyle.SetFrameLineWidth(4)
ROOT.gStyle.SetPaintTextFormat("3.2f")
ROOT.gStyle.SetErrorX(0)
ROOT.TH1.SetDefaultSumw2()

def etaSliceMeanET(evtsFrame, outFile, etRange, tag = ""):

    h1 = evtsFrame.Histo3D(("h1_%s_mean"%(tag), "h1_%s_mean"%(tag), 57, -28.5, 28.5, 4, -0.5, 3.5, 128, -0.25, 64.25), "ieta", "ts1", "ts1_e")

    h2 = evtsFrame.Histo3D(("h2_%s_mean"%(tag), "h2_%s_mean"%(tag), 57, -28.5, 28.5, 4, -0.5, 3.5, 128, -0.25, 64.25), "ieta", "ts2", "ts2_e")
    h3 = evtsFrame.Histo3D(("h3_%s_mean"%(tag), "h3_%s_mean"%(tag), 57, -28.5, 28.5, 4, -0.5, 3.5, 128, -0.25, 64.25), "ieta", "ts3", "ts3_e")
    h4 = evtsFrame.Histo3D(("h4_%s_mean"%(tag), "h4_%s_mean"%(tag), 57, -28.5, 28.5, 4, -0.5, 3.5, 128, -0.25, 64.25), "ieta", "ts4", "ts4_e")

    #h1 = evtsFrame.Histo3D(("h1_%s_mean"%(tag), "h1_%s_mean"%(tag), 57, -28.5, 28.5, 4, -0.5, 3.5, 30, -0.25, 5.25), "ieta", "ts1", "ts1_e")

    #h2 = evtsFrame.Histo3D(("h2_%s_mean"%(tag), "h2_%s_mean"%(tag), 57, -28.5, 28.5, 4, -0.5, 3.5, 30, -0.25, 5.25), "ieta", "ts2", "ts2_e")
    #h3 = evtsFrame.Histo3D(("h3_%s_mean"%(tag), "h3_%s_mean"%(tag), 57, -28.5, 28.5, 4, -0.5, 3.5, 30, -0.25, 5.25), "ieta", "ts3", "ts3_e")
    #h4 = evtsFrame.Histo3D(("h4_%s_mean"%(tag), "h4_%s_mean"%(tag), 57, -28.5, 28.5, 4, -0.5, 3.5, 30, -0.25, 5.25), "ieta", "ts4", "ts4_e")
    
    h11 = copy.deepcopy(h1.GetValue()); h11.SetDirectory(0)
    h21 = copy.deepcopy(h2.GetValue()); h21.SetDirectory(0)
    h31 = copy.deepcopy(h3.GetValue()); h31.SetDirectory(0)
    h41 = copy.deepcopy(h4.GetValue()); h41.SetDirectory(0)

    h11.Add(h21); h11.Add(h31); h11.Add(h41)

    h11.GetXaxis().SetTitle("|i#eta|")
    h11.GetZaxis().SetTitle("TS E_{T} [GeV]")
    h11.GetYaxis().SetTitle("TS")
    h11.SetTitle("")
    h11.SetName("Mean_et%sto%s_%s_3D"%(str(etRange[0]),str(etRange[1]),tag))

    outFile.cd()
    h11.Write("Mean_et%sto%s_%s_3D"%(str(etRange[0]),str(etRange[1]),tag))

def etaSliceDistET(evtsFrame, outFile, etRange, tag = ""):

    h1 = evtsFrame.Histo2D(("h1_%s_et"%(tag), "h1_%s_et"%(tag), 57, -28.5, 28.5, 256, -0.25, 127.75), "ieta", "et")
    
    h11 = copy.deepcopy(h1.GetValue()); h11.SetDirectory(0)

    h11.GetXaxis().SetTitle("|i#eta|")
    h11.GetYaxis().SetTitle("TP E_{T} [GeV]")
    h11.SetTitle("")
    h11.SetName("ET_et%sto%s_%s_3D"%(str(etRange[0]),str(etRange[1]),tag))

    outFile.cd()
    h11.Write("ET_et%sto%s_%s_3D"%(str(etRange[0]),str(etRange[1]),tag))

def eosify(directory):

    if "eos" in directory and "cmseos" not in directory:
        directory.replace("/eos/uscms/", "root://eoscms.fnal.gov//") 

def prettyHisto(histo, tag=None, theFactor = 0.6):
    
    histo.GetYaxis().SetLabelSize(theFactor*0.065); histo.GetYaxis().SetTitleSize(theFactor*0.065); histo.GetYaxis().SetTitle("TS E_{T} [GeV]"); histo.GetYaxis().SetTitleOffset(0.7/theFactor)
    histo.GetXaxis().SetTitleSize(theFactor*0.065); histo.GetXaxis().SetTitleOffset(0.9)
    histo.GetXaxis().SetLabelSize(theFactor*0.085)

    histo.SetLineWidth(5)
    histo.SetMarkerSize(3)
    histo.SetMarkerStyle(20)
    histo.SetTitle("")

    histo.GetXaxis().SetBinLabel(1, "SOI-2")
    histo.GetXaxis().SetBinLabel(2, "SOI-1")
    histo.GetXaxis().SetBinLabel(3, "SOI")
    histo.GetXaxis().SetBinLabel(4, "SOI+1")

    #histo.GetXaxis().SetBinLabel(1, "SOI")
    #histo.GetXaxis().SetBinLabel(2, "SOI+1")
    #histo.GetXaxis().SetBinLabel(3, "SOI+2")
    #histo.GetXaxis().SetBinLabel(4, "SOI+3")

    histo.GetXaxis().SetTitleSize(theFactor*0.065)
    histo.GetXaxis().SetTitleSize(theFactor*0.065)
    histo.GetXaxis().SetTitleSize(theFactor*0.065)
    histo.GetXaxis().SetTitleSize(theFactor*0.065)

    if tag == "ISO":
        histo.SetLineColor(ROOT.TColor.GetColor("#F803D8"))
        histo.SetMarkerColor(ROOT.TColor.GetColor("#F803D8"))
    elif tag == "NONISO":
        histo.SetLineColor(ROOT.TColor.GetColor("#404FB6"))
        histo.SetMarkerColor(ROOT.TColor.GetColor("#404FB6"))
    elif tag == "NOPU":
        histo.SetLineColor(ROOT.kBlack)
        histo.SetMarkerColor(ROOT.kBlack)
    elif tag == "PRE":
        histo.SetLineColor(ROOT.TColor.GetColor("#00cd00"))
        histo.SetMarkerColor(ROOT.TColor.GetColor("#00cd00"))
    elif tag == "POST":
        histo.SetLineColor(ROOT.TColor.GetColor("#ff3200"))
        histo.SetMarkerColor(ROOT.TColor.GetColor("#ff3200"))
    elif tag == "OOT":
        histo.SetLineColor(ROOT.TColor.GetColor("#7a0019"))
        histo.SetMarkerColor(ROOT.TColor.GetColor("#7a0019"))
    elif tag == "50PU":
        histo.SetLineColor(ROOT.kGray+1)
        histo.SetMarkerColor(ROOT.kGray+1)

def combineHistos(histoMap, outRootDir):

    for histoFile in os.listdir(outRootDir):

        histoFile = ROOT.TFile.Open(outRootDir + "/" + histoFile, "READ")
        for hkey in histoFile.GetListOfKeys():
            if "TH" not in hkey.GetClassName() and \
               "TProf" not in hkey.GetClassName(): continue

            name = hkey.GetName()
            histo = hkey.ReadObj()
            histo.SetDirectory(0)
            
            if name in histoMap.keys(): histoMap[name].Add(histo)
            else: histoMap[name] = histo

def drawETEtaSlice(etHistos, ieta, fold=False, tag = ""):
    
    theFactor = 0.6
    projHistos = {}
    
    for cat, histo in etHistos.iteritems():

        c2 = ROOT.TCanvas("c2_%s_%s_%s"%(ieta,tag,cat), "c2_%s_%s_%s"%(ieta,tag,cat), 1200, 1200); c2.cd()
        
        etaRing = 0
        if fold:
            etaRingPos = 0; etaRingNeg = 0
            histoPos = histo.Clone(); histoNeg = histo.Clone()

            etaRingPos = histoPos.ProjectionY("Pos_%d"%(ieta),histoPos.GetXaxis().FindBin(ieta),histoPos.GetXaxis().FindBin(ieta))
            etaRingNeg = histoNeg.ProjectionY("Neg_%d"%(ieta),histoNeg.GetXaxis().FindBin(-ieta),histoNeg.GetXaxis().FindBin(-ieta))

            etaRing = etaRingPos.Clone()
            etaRing.Add(etaRingNeg)
        else:
            etaRing = histo.ProjectionX(ieta,ieta)
           
        prettyHisto(etaRing, cat.split("_")[0])
        etaRing.GetXaxis().SetTitle("TP E_{T} [GeV]")
        etaRing.GetYaxis().SetTitle("A.U.")
        etaRing.GetXaxis().SetLabelSize(0.6*0.065)
        etaRing.GetXaxis().SetTitleOffset(1.1)

        projHistos[cat] = etaRing 

    for etRange in gEtRanges:

        etStr = "%sto%s"%(etRange[0],etRange[1])

        c1 = ROOT.TCanvas("c1_%s_%s_%s"%(ieta,tag,etStr), "c1_%s_%s_%s"%(ieta,tag,etStr), 1200, 1200); c1.cd()

        someText = ROOT.TPaveText(0.66, 0.57, 0.9, 0.65, "trNDC")
        someText.AddText("|ieta| = %d"%(ieta))
        someText.SetFillColor(ROOT.kWhite)

        ROOT.gPad.SetRightMargin(0.02)
        ROOT.gPad.SetLeftMargin(0.10)
        ROOT.gPad.SetTopMargin(0.025)
        ROOT.gPad.SetBottomMargin(0.11)

        iamLegend = ROOT.TLegend(0.66, 0.69, 0.95, 0.94, "", "trNDC")
        iamLegend.SetTextSize(theFactor*0.05)
        iamLegend.SetBorderSize(0)

        maximum = 0
        for cat, projHisto in projHistos.iteritems():
           if etStr in cat:
                tempMax = projHisto.GetBinContent(projHisto.GetMaximumBin())
                if tempMax > maximum: maximum = tempMax 

        for cat, projHisto in projHistos.iteritems():
            if etStr in cat:
                iamLegend.AddEntry(projHisto, cat.split("_")[0], "LP")
                #projHisto.SetMinimum(0)
                #projHisto.SetMaximum(1.)
                if etRange[0] == 0.5:
                    projHisto.GetXaxis().SetRangeUser(0,15)
                    projHisto.SetMaximum(10e4)
                elif etRange[0] == 10:
                    #projHisto.RebinX(4)
                    projHisto.GetXaxis().SetRangeUser(10,35)
                    projHisto.SetMaximum(10e1)
                elif etRange[0] == 30:
                    #projHisto.RebinX(8)
                    projHisto.GetXaxis().SetRangeUser(30,100)
                    projHisto.SetMaximum(10e0)

                projHisto.Draw("HIST SAME")

        iamLegend.Draw("SAME")
        someText.Draw("SAME")

        c1.SetLogy()
        c1.SaveAs("./plots/TS/%s/%s/ET_ieta%d.pdf"%(gTag,etStr,ieta))

def drawPulseShapeEtaSlice(meanHistos, ieta, fold=False, tag = ""):
    
    theFactor = 0.6
    projHistos = {}
    
    for cat, histo in meanHistos.iteritems():

        c2 = ROOT.TCanvas("c2_%s_%s_%s"%(ieta,tag,cat), "c2_%s_%s_%s"%(ieta,tag,cat), 1200, 1200); c2.cd()
        
        etaRing = 0
        if fold:
            etaRingPos = 0; etaRingNeg = 0
            histoPos = histo.Clone(); histoNeg = histo.Clone()

            histoPos.GetXaxis().SetRangeUser(ieta,ieta)
            histoPos.GetXaxis().SetBit(ROOT.TAxis.kAxisRange)
            etaRingPos = histoPos.Project3D("zy")

            histoNeg.GetXaxis().SetRangeUser(-ieta,-ieta)
            histoNeg.GetXaxis().SetBit(ROOT.TAxis.kAxisRange)
            etaRingNeg = histoNeg.Project3D("zy")

            etaRing = etaRingPos.Clone()
            etaRing.Add(etaRingNeg)
        else:
            histo.GetXaxis().SetRangeUser(ieta,ieta)
            histo.GetXaxis().SetBit(ROOT.TAxis.kAxisRange)
            etaRing = histo.Project3D("zy")
           
        etaRing.SetTitle("%s, |ieta| = %s"%(cat, ieta))
        etaRing.GetYaxis().SetTitle("TS #LT E_{T} #GT [GeV]")
        etaRing.GetXaxis().SetTitle("")
        etaRing.GetXaxis().SetBinLabel(1, "SOI")
        etaRing.GetXaxis().SetBinLabel(2, "SOI+1")
        etaRing.GetXaxis().SetBinLabel(3, "SOI+2")
        etaRing.GetXaxis().SetBinLabel(4, "SOI+3")
        etaRing.GetXaxis().SetLabelSize(0.6*0.085)

        ROOT.gPad.SetRightMargin(0.2)
    
        p1 = etaRing.ProfileX("Mean_%s_prof"%(cat), 1, -1)
        prettyHisto(p1, cat.split("_")[0])
        p1.GetXaxis().SetTitle("")
        p1.GetYaxis().SetTitle("TS #LT E_{T} #GT [GeV]")
        etaRing.Draw("COLZ SAME")
        etaRing.SetContour(255)
        p1.Draw("SAME")

        c2.SaveAs("./plots/TS/%s/%s/%s/Debug_ieta%s.pdf"%(gTag,cat.split("_")[0],cat.split("_")[1].split("et")[-1],ieta))

        projHistos[cat] = p1

    for etRange in gEtRanges:

        etStr = "%sto%s"%(etRange[0],etRange[1])

        c1 = ROOT.TCanvas("c1_%s_%s_%s"%(ieta,tag,etStr), "c1_%s_%s_%s"%(ieta,tag,etStr), 1200, 1200); c1.cd()

        someText = ROOT.TPaveText(0.66, 0.57, 0.9, 0.65, "trNDC")
        someText.AddText("|ieta| = %d"%(ieta))
        someText.SetFillColor(ROOT.kWhite)

        ROOT.gPad.SetRightMargin(0.010)
        ROOT.gPad.SetLeftMargin(0.10)
        ROOT.gPad.SetTopMargin(0.025)
        ROOT.gPad.SetBottomMargin(0.045)

        iamLegend = ROOT.TLegend(0.66, 0.69, 0.95, 0.94, "", "trNDC")
        iamLegend.SetTextSize(theFactor*0.05)
        iamLegend.SetBorderSize(0)

        maximum = 0
        for cat, projHisto in projHistos.iteritems():
           if etStr in cat:
                tempMax = projHisto.GetBinContent(projHisto.GetMaximumBin())
                if tempMax > maximum: maximum = tempMax 

        for cat, projHisto in projHistos.iteritems():
            if etStr in cat:
                iamLegend.AddEntry(projHisto, cat.split("_")[0], "LP")
                projHisto.SetMinimum(0)
                projHisto.SetMaximum(maximum*2.)
                projHisto.Draw("HIST P SAME")
                projHisto.Draw("HIST SAME")

        iamLegend.Draw("SAME")
        someText.Draw("SAME")

        c1.SaveAs("./plots/TS/%s/%s/TS_pulseShape_ieta%d.pdf"%(gTag,etStr,ieta))

def drawCompPU(catHistosMap):

    # A list of dict with histo names as keys and histo objs and values
    catHistos  = catHistosMap.values()
    cats       = catHistosMap.keys()
    
    numHistos = len(catHistos[0].values())
    meanHistos = {}
    etHistos = {}
    for i in xrange(numHistos):

        special = catHistos[0].values()[i].GetName().split("_")[0]
        etRange = catHistos[0].values()[i].GetName().split("_")[1]
        for j in xrange(0,len(cats)):
            if special == "Mean":
                meanHistos[cats[j]+"_"+etRange] = next((hist for hist in catHistos[j].values() if special in hist.GetName() and etRange in hist.GetName()), None)
            if special == "ET":
                etHistos[cats[j]+"_"+etRange] = next((hist for hist in catHistos[j].values() if special in hist.GetName() and etRange in hist.GetName()), None)

    for ieta in xrange(17,29):
        drawPulseShapeEtaSlice(meanHistos, ieta, fold=True, tag=special)
        #drawETEtaSlice(etHistos, ieta, fold=True, tag=special)
    
def timeSlice_Eta(evtsFrame, etRange):

    filtered = evtsFrame.Filter("(et > %s && et <= %s)"%(etRange[0],etRange[1]))

    return filtered

def analysis(aFile, outRootDir, category):

    lowET = [0.5,10]; midET = [10,30]; highET = [30,1000]

    if "SIM" in aFile: return

    stub = aFile.split("/")[-1].split(".root")[0]
    outFile = ROOT.TFile.Open("%s/%s_plots.root"%(outRootDir,stub), "RECREATE")

    mainFrame = ROOT.ROOT.Experimental.TDataFrame("compareReemulRecoSeverity9/tps", aFile)

    customFrame = mainFrame.Define("ts1_e", "ts_energy[0]").Define("ts1", "0") \
    .Define("ts2_e", "ts_energy[1]").Define("ts2", "1") \
    .Define("ts3_e", "ts_energy[2]").Define("ts3", "2") \
    .Define("ts4_e", "ts_energy[3]").Define("ts4", "3")

    tsMeanProf05 = timeSlice_Eta(customFrame, lowET)
    tsMeanProf10 = timeSlice_Eta(customFrame, midET)
    tsMeanProf30 = timeSlice_Eta(customFrame, highET)

    etaSliceMeanET(tsMeanProf05, outFile, lowET, category)
    etaSliceMeanET(tsMeanProf10, outFile, midET, category)
    etaSliceMeanET(tsMeanProf30, outFile, highET, category)

    #etaSliceDistET(tsMeanProf05, outFile, lowET, category)
    #etaSliceDistET(tsMeanProf10, outFile, midET, category)
    #etaSliceDistET(tsMeanProf30, outFile, highET, category)

    outFile.Close()

if __name__ == '__main__':

    gTag = sys.argv[1]
    gEtRanges = [[0.5,10], [10,30], [30,1000]]

    location = "./destroy/oldshift/"
    outStub = "./plots/TS/%s"%(gTag)

    catInputDir = {}; catOutputDir = {}; catInputFiles = {}; catHistos = {}

    for cat in xrange(2,len(sys.argv)): catInputDir[sys.argv[cat]] = location + sys.argv[cat] + "/"

    for cat, inputDir in catInputDir.iteritems():
        catOutDir = "%s/%s"%(outStub,cat)
        if not os.path.exists("%s/root"%(catOutDir)): os.makedirs("%s/root"%(catOutDir))
        if not os.path.exists("%s/%sto%s"%(catOutDir,gEtRanges[0][0],gEtRanges[0][1])): os.makedirs("%s/%sto%s"%(catOutDir,gEtRanges[0][0],gEtRanges[0][1]))
        if not os.path.exists("%s/%sto%s"%(catOutDir,gEtRanges[1][0],gEtRanges[1][1])): os.makedirs("%s/%sto%s"%(catOutDir,gEtRanges[1][0],gEtRanges[1][1]))
        if not os.path.exists("%s/%sto%s"%(catOutDir,gEtRanges[2][0],gEtRanges[2][1])): os.makedirs("%s/%sto%s"%(catOutDir,gEtRanges[2][0],gEtRanges[2][1]))

        if not os.path.exists("%s/%sto%s"%(outStub,gEtRanges[0][0],gEtRanges[0][1])): os.makedirs("%s/%sto%s"%(outStub,gEtRanges[0][0],gEtRanges[0][1]))
        if not os.path.exists("%s/%sto%s"%(outStub,gEtRanges[1][0],gEtRanges[1][1])): os.makedirs("%s/%sto%s"%(outStub,gEtRanges[1][0],gEtRanges[1][1]))
        if not os.path.exists("%s/%sto%s"%(outStub,gEtRanges[2][0],gEtRanges[2][1])): os.makedirs("%s/%sto%s"%(outStub,gEtRanges[2][0],gEtRanges[2][1]))

        catOutputDir[cat] = catOutDir+"/root" 
        catInputFiles[cat] = [inputDir + "/" + aFile for aFile in os.listdir(inputDir)]
        catHistos[cat] = {}

    print "Processing root files"
    for cat, inputFiles in catInputFiles.iteritems():
        for aFile in inputFiles:
            eosify(aFile)
        
        theFunc = partial(analysis, outRootDir=catOutputDir[cat], category=cat)
        pool = multiprocessing.Pool(processes=8)
        results = pool.map(theFunc, inputFiles) 

    for cat, histoMap in catHistos.iteritems():
        combineHistos(histoMap, catOutputDir[cat])

    drawCompPU(catHistos)
