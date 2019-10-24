import sys, os, ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetLineWidth(4)
ROOT.gStyle.SetFrameLineWidth(4)
ROOT.TH1.SetDefaultSumw2()

def ratioTPVsRH_Eta_ET(evtsTree, basis = "TP", bx = "(1==1)"):

    etBins = 0; etBranch = ""; tpMinSelection = "TP_energy>0.5"
    if basis == "TP":
        etBranch = "TP_energy"
        etBins = 257 
    else:
        etBranch = "RH_energy"
        etBins = 257 

    h3 = ROOT.TH3F("h3_%sET"%(basis), "h3_%sET"%(basis), 57, -28.5, 28.5, 720, 0., 20.0, etBins, -0.25, 128.25)

    evtsTree.Draw("%s:TP_energy/RH_energy:ieta>>h3_%sET"%(etBranch,basis), "tp_soi!=255 && %s && RH_energy>0. && %s"%(tpMinSelection,bx))

    h3 = ROOT.gDirectory.Get("h3_%sET"%(basis))

    return h3

def ratioTPVsRH_Eta(outfile, histo, basis, etRange = []):

    outfile.cd()

    htemp = histo.Clone()

    h2 = 0
    if len(etRange) == 0: htemp.GetZaxis().SetRange(1, htemp.GetZaxis().GetNbins())
    elif len(etRange) == 1: htemp.GetZaxis().SetRange(htemp.GetZaxis().FindBin(etRange[0]),htemp.GetZaxis().FindBin(etRange[0]))
    elif len(etRange) == 2: htemp.GetZaxis().SetRange(htemp.GetZaxis().FindBin(etRange[0])+1,htemp.GetZaxis().FindBin(etRange[1]))
    htemp.GetZaxis().SetBit(ROOT.TAxis.kAxisRange)
    h2 = htemp.Project3D("yx")

    h2.SetTitle("")
    h2.GetXaxis().SetTitle("i#eta")
    h2.GetYaxis().SetTitle("E_{T,TP} / E_{T,RH}")

    if len(etRange) == 0:
        h2.Write("TPRH_vs_Eta")
    elif len(etRange) == 1:
        h2.Write("TPRH_vs_Eta_%sET%0.1f"%(basis,etRange[0]))
    elif len(etRange) == 2:
        h2.Write("TPRH_vs_Eta_%sET%0.1fto%0.1f"%(basis,etRange[0],etRange[1]))

def ratioTPVsRH(outfile, histo, basis, etRange = [], ietaRange = []):

    outfile.cd()

    htemp = histo.Clone()

    h2 = 0; etStr = ""
    if len(etRange) == 0:
        htemp.GetZaxis().SetRange(1, htemp.GetZaxis().GetNbins())
    elif len(etRange) == 1:
        htemp.GetZaxis().SetRange(htemp.GetZaxis().FindBin(etRange[0]),htemp.GetZaxis().FindBin(etRange[0]))
        etStr = "%sET%0.1f"%(basis,etRange[0])
    elif len(etRange) == 2:
        htemp.GetZaxis().SetRange(htemp.GetZaxis().FindBin(etRange[0])+1,htemp.GetZaxis().FindBin(etRange[1]))
        etStr = "%sET%0.1fto%0.1f"%(basis,etRange[0],etRange[1])
    htemp.GetZaxis().SetBit(ROOT.TAxis.kAxisRange)
    h2 = htemp.Project3D("yx")

    h = 0; ietaStr = ""
    if len(ietaRange) == 0:
        h = h2.ProjectionY("%s_proj"%(h2.GetTitle()), 1, h2.GetxAxis().GetNbins())
    elif len(ietaRange) == 1:
        hpos = h2.ProjectionY("%s_proj_pos_%d"%(h2.GetTitle(),ietaRange[0]), h2.GetXaxis().FindBin(ietaRange[0]),h2.GetXaxis().FindBin(ietaRange[0]))
        hneg = h2.ProjectionY("%s_proj_neg_%d"%(h2.GetTitle(),ietaRange[0]), h2.GetXaxis().FindBin(-ietaRange[0]),h2.GetXaxis().FindBin(-ietaRange[0]))
        h = hpos; h.Add(hneg)
        ietaStr = "ieta%d"%(ietaRange[0])
    elif len(ietaRange) == 2:
        hpos = h2.ProjectionY("%s_proj_pos_%dto%d"%(h2.GetTitle(),ietaRange[0],ietaRange[1]), h2.GetXaxis().FindBin(ietaRange[0]),h2.GetXaxis().FindBin(ietaRange[1]))
        hneg = h2.ProjectionY("%s_proj_neg_%dto%d"%(h2.GetTitle(),ietaRange[0],ietaRange[1]), h2.GetXaxis().FindBin(-ietaRange[1]),h2.GetXaxis().FindBin(-ietaRange[0]))
        h = hpos; h.Add(hneg)
        ietaStr = "ieta%dto%d"%(ietaRange[0],ietaRange[1])

    h.SetTitle("")
    h.GetXaxis().SetTitle("E_{T,TP} / E_{T,RH}")
    h.GetYaxis().SetTitle("A.U.")

    h.Write("TPRH_%s_%s"%(etStr,ietaStr))

def ratioTPVsRH_ET(outfile, histo, basis, ietaRange = []):

    outfile.cd()

    htemp = histo.Clone()

    h2 = 0; ietaStr = ""
    if len(ietaRange) == 0:
        htemp.GetXaxis().SetRange(1, htemp.GetXaxis().GetNbins())
        htemp.GetXaxis().SetBit(ROOT.TAxis.kAxisRange)
    elif len(etRange) == 1:
        htemp.GetXaxis().SetRange(htemp.GetXaxis().FindBin(ietaRange[0]),htemp.GetXaxis().FindBin(ietaRange[0]))
        htemp.GetXaxis().SetBit(ROOT.TAxis.kAxisRange)
        ietaStr = "_%sieta%0.1f"%(basis,ietaRange[0])
    elif len(etRange) == 2:
        htemp.GetXaxis().SetRange(htemp.GetXaxis().FindBin(ietaRange[0]),htemp.GetXaxis().FindBin(ietaRange[1]))
        htemp.GetXaxis().SetBit(ROOT.TAxis.kAxisRange)
        ietaStr = "_%sieta%0.1fto%0.1f"%(basis,ietaRange[0],ietaRange[1])

    h2 = htemp.Project3D("yz")

    h2.SetTitle("")
    h2.GetYaxis().SetTitle("E_{T,TP} / E_{T,RH}")
    h2.GetXaxis().SetTitle("E_{T,%s} [GeV]"%(basis))

    h2.Write("TPRH_%sET%s"%(basis,ietaStr))

def analysis(PFAXFile, PFA2File):

    outPath = PFAXFile.replace(".root", "_ratios.root") 
    outFile = ROOT.TFile.Open(outPath, "RECREATE")

    fPFAX = ROOT.TFile.Open(PFAXFile, "READ")
    fPFA2 = ROOT.TFile.Open(PFA2File, "READ")

    tPFAX = fPFAX.Get("compareReemulRecoSeverity9/matches")
    tPFA2 = fPFA2.Get("compareReemulRecoSeverity9/matches")

    friendAdded = tPFAX.AddFriend(tPFA2, "tPFA2")
    if friendAdded == 0:
        print "Trouble adding friend tree from PFA2 file!"
        print "Exiting..."
        quit()

    TPETvRatiovEta_TP = ratioTPVsRH_Eta_ET(tPFAX,"TP"); TPETvRatiovEta_TP.SetDirectory(0)
    TPETvRatiovEta_RH = ratioTPVsRH_Eta_ET(tPFAX,"RH"); TPETvRatiovEta_RH.SetDirectory(0)

    fPFAX.Close()
    fPFA2.Close()

    # When providing ET ranges it always for PFA2 when in TP basis
    for ieta in xrange(1,29):
        ratioTPVsRH(outFile,TPETvRatiovEta_TP,"TP",[0.5,10],[ieta])
        ratioTPVsRH(outFile,TPETvRatiovEta_TP,"TP",[10, 1000],[ieta])

        ratioTPVsRH(outFile,TPETvRatiovEta_RH,"RH",[0.5,10],[ieta])
        ratioTPVsRH(outFile,TPETvRatiovEta_RH,"RH",[10, 1000],[ieta])

    ratioTPVsRH_Eta(outFile,TPETvRatiovEta_TP,"TP",[0.5,10])
    ratioTPVsRH_Eta(outFile,TPETvRatiovEta_TP,"TP",[10, 1000])

    ratioTPVsRH_Eta(outFile,TPETvRatiovEta_RH,"RH",[0.5,10])
    ratioTPVsRH_Eta(outFile,TPETvRatiovEta_RH,"RH",[10, 1000])

    ratioTPVsRH(outFile,TPETvRatiovEta_TP,"TP",[1.0],[-28,28])
    ratioTPVsRH(outFile,TPETvRatiovEta_TP,"TP",[2.0],[-28,28])
    ratioTPVsRH(outFile,TPETvRatiovEta_TP,"TP",[3.0],[-28,28])
    ratioTPVsRH(outFile,TPETvRatiovEta_TP,"TP",[4.0],[-28,28])
    ratioTPVsRH(outFile,TPETvRatiovEta_TP,"TP",[5.0],[-28,28])
    ratioTPVsRH(outFile,TPETvRatiovEta_TP,"TP",[6.0],[-28,28])

    ratioTPVsRH(outFile,TPETvRatiovEta_RH,"RH",[1.0],[-28,28])
    ratioTPVsRH(outFile,TPETvRatiovEta_RH,"RH",[2.0],[-28,28])
    ratioTPVsRH(outFile,TPETvRatiovEta_RH,"RH",[3.0],[-28,28])
    ratioTPVsRH(outFile,TPETvRatiovEta_RH,"RH",[4.0],[-28,28])
    ratioTPVsRH(outFile,TPETvRatiovEta_RH,"RH",[5.0],[-28,28])
    ratioTPVsRH(outFile,TPETvRatiovEta_RH,"RH",[6.0],[-28,28])

    ratioTPVsRH_ET(outFile,TPETvRatiovEta_TP,"TP")
    ratioTPVsRH_ET(outFile,TPETvRatiovEta_RH,"RH")

    ratioTPVsRH_ET(outFile,TPETvRatiovEta_TP,"TP",[1,16])
    ratioTPVsRH_ET(outFile,TPETvRatiovEta_RH,"RH",[1,16])

    ratioTPVsRH_ET(outFile,TPETvRatiovEta_TP,"TP",[17,28])
    ratioTPVsRH_ET(outFile,TPETvRatiovEta_RH,"RH",[17,28])

    outFile.Close()
   
if __name__ == '__main__':

    PFAXFile = str(sys.argv[1])

    subdirs = PFAXFile.split("/")

    # Unfortunately hard code this
    # But get the companion ntuples for PFA2 to use as a friend
    for iSubdir in xrange(len(subdirs)):
        if "PFA" in subdirs[iSubdir]: subdirs[iSubdir] = "PFA2" 

    PFA2File = '/'.join(subdirs[0:-1]) + "/hcalNtuple_PFA2.root"

    if not os.path.exists(PFA2File):
        print "We need to add PFA2 as a friend but we cannot find \"%s\"!"%(PFA2File)
        print "Exiting..."
        quit()

    analysis(PFAXFile, PFA2File)
