import sys, os, ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetLineWidth(4)
ROOT.gStyle.SetFrameLineWidth(4)
ROOT.TH1.SetDefaultSumw2()

def ratioTPVsRH_Eta_ET(evtsTree, basis = "TP", bx = "(1==1)"):

    etBranch = ""; tpMinSelection = "1==1"
    if basis == "TP": etBranch = "tPFA2.TP_energy"
    else:
        etBranch = "RH_energy"
        tpMinSelection = "TP_energy>0"

    h3 = ROOT.TH3F("h3_%sET"%(basis), "h3_%sET"%(basis), 57, -28.5, 28.5, 720, 0., 20.0, 1000, -0.25, 499.75)

    evtsTree.Draw("%s:TP_energy/RH_energy:ieta>>h3_%sET"%(etBranch,basis), "tp_soi!=255 && %s && RH_energy>0. && %s"%(tpMinSelection,bx))

    h3 = ROOT.gDirectory.Get("h3_%sET"%(basis))

    return h3

def ratioTPVsRH_Eta(outfile, histo, etRange = []):

    outfile.cd()

    # The basis depends on the title of the histo in the companion function ratioTPVsRH_Eta_ET
    basis = histo.GetTitle().split("_")[1][0:2]

    h2 = 0
    if len(etRange) == 0: histo.GetZaxis().SetRange(1, histo.GetZaxis().GetNbins())
    elif len(etRange) == 1: histo.GetZaxis().SetRange(histo.GetZaxis().FindBin(etRange[0]),histo.GetZaxis().FindBin(etRange[0]))
    elif len(etRange) == 2: histo.GetZaxis().SetRange(histo.GetZaxis().FindBin(etRange[0])+1,histo.GetZaxis().FindBin(etRange[1]))
    histo.GetZaxis().SetBit(ROOT.TAxis.kAxisRange)
    h2 = histo.Project3D("yx")

    h2.SetTitle("")
    h2.GetXaxis().SetTitle("i#eta")
    h2.GetYaxis().SetTitle("E_{T,TP} / E_{T,RH}")

    if len(etRange) == 0:
        h2.Write("TPRH_vs_Eta")
    elif len(etRange) == 1:
        h2.Write("TPRH_vs_Eta_%sET%0.1f"%(basis,etRange[0]))
    elif len(etRange) == 2:
        h2.Write("TPRH_vs_Eta_%sET%0.1fto%0.1f"%(basis,etRange[0],etRange[1]))

def ratioTPVsRH(outfile, histo, etRange = [], etaRange = []):

    outfile.cd()

    basis = histo.GetTitle().split("_")[1][0:2]

    h2 = 0; etStr = ""
    if len(etRange) == 0:
        histo.GetZaxis().SetRange(1, histo.GetZaxis().GetNbins())
    elif len(etRange) == 1:
        histo.GetZaxis().SetRange(histo.GetZaxis().FindBin(etRange[0]),histo.GetZaxis().FindBin(etRange[0]))
        etStr = "_%sET%0.1f"%(basis,etRange[0])
    elif len(etRange) == 2:
        histo.GetZaxis().SetRange(histo.GetZaxis().FindBin(etRange[0])+1,histo.GetZaxis().FindBin(etRange[1]))
        etStr = "_%sET%0.1fto%0.1f"%(basis,etRange[0],etRange[1])
    histo.GetZaxis().SetBit(ROOT.TAxis.kAxisRange)
    h2 = histo.Project3D("yx")

    h = 0; etaStr = ""
    if len(etaRange) == 0:
        h = h2.ProjectionY("%s_proj"%(h2.GetTitle()), 1, h2.GetxAxis().GetNbins())
    elif len(etaRange) == 1:
        h = h2.ProjectionY("%s_proj"%(h2.GetTitle()), h2.GetXaxis().FindBin(etaRange[0]),h2.GetXaxis().FindBin(etaRange[0]))
        etaStr = "_ieta%d"%(etaRange[0])
    elif len(etaRange) == 2:
        h = h2.ProjectionY("%s_proj"%(h2.GetTitle()), h2.GetXaxis().FindBin(etaRange[0]),h2.GetXaxis().FindBin(etaRange[1]))
        etaStr = "_ieta%dto%d"%(etaRange[0],etaRange[1])

    h.SetTitle("")
    h.GetXaxis().SetTitle("E_{T,TP} / E_{T,RH}")
    h.GetYaxis().SetTitle("A.U.")

    h.Write("TPRH%s%s"%(etStr,etaStr))

def analysis(PFAXFile, PFA2File):

        outPath = PFAXFile.replace(".root", "_ratios.root") 
        outFile = ROOT.TFile.Open(outPath, "RECREATE")

        fPFAX = ROOT.TFile.Open(PFAXFile, "READ")
        fPFA2 = ROOT.TFile.Open(PFA2File, "READ")

        tPFAX = fPFAX.Get("compareReemulRecoSeverity9/matches")
        tPFA2 = fPFA2.Get("compareReemulRecoSeverity9/matches")

        friendAdded = tPFAX.AddFriend(tPFA2, "tPFA2")
        if friendAdded == 0:\
            print "Trouble adding friend tree from PFA2 file!"
            print "Exiting..."
            quit()

        TPETvRatiovEta_42 = ratioTPVsRH_Eta_ET(tPFAX,"TP"); TPETvRatiovEta_42.SetDirectory(0)
        RHETvRatiovEta_42 = ratioTPVsRH_Eta_ET(tPFAX,"RH"); RHETvRatiovEta_42.SetDirectory(0)

        fPFAX.Close()
        fPFA2.Close()

        # When providing ET ranges it always for PFA2 when in TP basis
        for ieta in xrange(1,29):
            ratioTPVsRH(outFile,TPETvRatiovEta_42,[0.5,10],[ieta])
            ratioTPVsRH(outFile,TPETvRatiovEta_42,[10, 1000],[ieta])

            ratioTPVsRH(outFile,RHETvRatiovEta_42,[0.5,10],[ieta])
            ratioTPVsRH(outFile,RHETvRatiovEta_42,[10, 1000],[ieta])

        ratioTPVsRH_Eta(outFile,TPETvRatiovEta_42,[0.5,10])
        ratioTPVsRH_Eta(outFile,TPETvRatiovEta_42,[10, 1000])

        ratioTPVsRH_Eta(outFile,RHETvRatiovEta_42,[0.5,10])
        ratioTPVsRH_Eta(outFile,RHETvRatiovEta_42,[10, 1000])

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
        print "We need to add PFA2 as a friend but we cannot find \"%s\"!"
        print "Exiting..."
        quit()

    analysis(PFAXFile, PFA2File)
