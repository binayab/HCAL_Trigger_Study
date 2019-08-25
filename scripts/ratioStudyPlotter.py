import sys, os, ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetLineWidth(4)
ROOT.gStyle.SetFrameLineWidth(4)
ROOT.TH1.SetDefaultSumw2()

def ratioTPVsRH_Eta_ET(evtsTree, basis = "TP", bx = "(1==1)"):

    etBranch = ""; tpMinSelection = "1==1"
    if basis == "TP": etBranch = "TP_energy"
    else:
        etBranch = "RH_energy"
        tpMinSelection = "TP_energy>0.5"

    h3 = ROOT.TH3F("h3_%sET"%(basis), "h3_%sET"%(basis), 57, -28.5, 28.5, 300, 0., 20.0, 1000, -0.25, 499.75)

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
        h2.Write("Ratio_TP-RH_vs_Eta")
    elif len(etRange) == 1:
        h2.Write("Ratio_TP-RH_vs_Eta_%sET%0.1f"%(basis,etRange[0]))
    elif len(etRange) == 2:
        h2.Write("Ratio_TP-RH_vs_Eta_%sET%0.1f-%0.1f"%(basis,etRange[0],etRange[1]))

def analysis(PFAFile):

        stub = PFAFile.split("/")[-1].split(".root")[0]
        outFile = ROOT.TFile.Open("%s_ratios.root"%(stub), "RECREATE")

        fPFA = ROOT.TFile.Open(PFAFile, "READ")
        tPFA = fPFA.Get("compareReemulRecoSeverity9/matches")

        TPETvRatiovEta_42 = ratioTPVsRH_Eta_ET(tPFA,"TP"); TPETvRatiovEta_42.SetDirectory(0)
        RHETvRatiovEta_42 = ratioTPVsRH_Eta_ET(tPFA,"RH"); RHETvRatiovEta_42.SetDirectory(0)

        fPFA.Close()

        ratioTPVsRH_Eta(outFile,TPETvRatiovEta_42,[0.5,1000])
        ratioTPVsRH_Eta(outFile,TPETvRatiovEta_42,[0.5,10])
        ratioTPVsRH_Eta(outFile,TPETvRatiovEta_42,[10, 1000])

        ratioTPVsRH_Eta(outFile,RHETvRatiovEta_42,[0.5,1000])
        ratioTPVsRH_Eta(outFile,RHETvRatiovEta_42,[0.5,10])
        ratioTPVsRH_Eta(outFile,RHETvRatiovEta_42,[10, 1000])

        outFile.Close()
   
if __name__ == '__main__':

    PFAFile = str(sys.argv[1])
    analysis(PFAFile)
