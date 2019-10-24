import sys, os, ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetLineWidth(4)
ROOT.gStyle.SetFrameLineWidth(4)
ROOT.TH1.SetDefaultSumw2()

def fillIetaDictionary(tPFAX, tPFA2, outFile, ietaDictionaryLowET,ietaDictionaryHighET):

    numEntries = tPFA2.GetEntries()

    tPFAX.SetBranchStatus("*", 0)
    tPFAX.SetBranchStatus("ieta", 1)  
    tPFAX.SetBranchStatus("TP_energy", 1)
    tPFAX.SetBranchStatus("event", 1)

    tPFA2.SetBranchStatus("*", 0)
    tPFA2.SetBranchStatus("TP_energy", 1)
    tPFA2.SetBranchStatus("event", 1)

    for depth in xrange(1,8):
        tPFAX.SetBranchStatus("d%d"%(depth), 1)

    for iEntry in xrange(numEntries):

        if iEntry % 10000 == 0: print "Processed entry %d..."%(iEntry)

        tPFAX.GetEntry(iEntry)
        tPFA2.GetEntry(iEntry)

        if tPFAX.event != tPFA2.event:
            print "Wow, we're effed!"

        aieta = abs(tPFAX.ieta)
        corrTPET = tPFAX.TP_energy
        uncorrTPET = tPFA2.TP_energy 
        
        d1 = tPFAX.d1
        d2 = tPFAX.d2
        d3 = tPFAX.d3
        d4 = tPFAX.d4
        d5 = tPFAX.d5
        d6 = tPFAX.d6
        d7 = tPFAX.d7

        if aieta > 28: continue 
        if corrTPET == 0: continue

        if uncorrTPET > 0.5 and uncorrTPET <= 10:
            ietaDictionaryLowET[aieta].Fill(1, d1)
            ietaDictionaryLowET[aieta].Fill(2, d2)
            ietaDictionaryLowET[aieta].Fill(3, d3)
            ietaDictionaryLowET[aieta].Fill(4, d4)
            ietaDictionaryLowET[aieta].Fill(5, d5)
            ietaDictionaryLowET[aieta].Fill(6, d6)
            ietaDictionaryLowET[aieta].Fill(7, d7)
        elif uncorrTPET > 10:
            ietaDictionaryHighET[aieta].Fill(1, d1)
            ietaDictionaryHighET[aieta].Fill(2, d2)
            ietaDictionaryHighET[aieta].Fill(3, d3)
            ietaDictionaryHighET[aieta].Fill(4, d4)
            ietaDictionaryHighET[aieta].Fill(5, d5)
            ietaDictionaryHighET[aieta].Fill(6, d6)
            ietaDictionaryHighET[aieta].Fill(7, d7)

    outFile.cd()
    for ieta in xrange(1,29):
        lowHisto = ietaDictionaryLowET[ieta]
        highHisto = ietaDictionaryHighET[ieta]

        lowHisto.SetTitle("|i#eta| = %d"%(ieta));         highHisto.SetTitle("|i#eta| = %d"%(ieta))
        lowHisto.GetXaxis().SetTitle("Depth");            highHisto.GetXaxis().SetTitle("Depth")
        lowHisto.GetYaxis().SetTitle("ADC (Linearized)"); highHisto.GetYaxis().SetTitle("ADC (Linearized)")

        lowHisto.Write()
        highHisto.Write()

def analysis(PFAXFile, PFA2File):

    outPath = PFAXFile.replace(".root", "_depths.root") 
    outFile = ROOT.TFile.Open(outPath, "RECREATE")

    fPFAX = ROOT.TFile.Open(PFAXFile, "READ")
    fPFA2 = ROOT.TFile.Open(PFA2File, "READ")

    tPFAX = fPFAX.Get("compareReemulRecoSeverity9/matches")
    tPFA2 = fPFA2.Get("compareReemulRecoSeverity9/matches")

    fillIetaDictionary(tPFAX,tPFA2,outFile,ietaDictionaryLowET,ietaDictionaryHighET)

    fPFAX.Close()
    fPFA2.Close()

    outFile.Close()
   
if __name__ == '__main__':

    ietaDictionaryLowET = {}
    ietaDictionaryHighET = {}
    for ieta in xrange(1,29):
        ietaDictionaryLowET[ieta] = ROOT.TH2D("ieta%d_low"%(ieta), "ieta%d_low"%(ieta), 7, 0.5, 7.5, 2049, -0.5, 2048.5)
        ietaDictionaryHighET[ieta] = ROOT.TH2D("ieta%d_high"%(ieta), "ieta%d_high"%(ieta), 7, 0.5, 7.5, 2049, -0.5, 2048.5)

    PFAXFile = str(sys.argv[1])

    subdirs = PFAXFile.split("/")
    for iSubdir in xrange(len(subdirs)):
        if "PFA" in subdirs[iSubdir]: subdirs[iSubdir] = "PFA2" 

    # Unfortunately hard code this
    # But get the companion ntuples for PFA2 to use as a friend
    PFA2File = '/'.join(subdirs[0:-1]) + "/hcalNtuple_PFA2.root"

    if not os.path.exists(PFA2File):
        print "We need to add PFA2 as a friend but we cannot find \"%s\"!"%(PFA2File)
        print "Exiting..."
        quit()

    analysis(PFAXFile, PFA2File)
