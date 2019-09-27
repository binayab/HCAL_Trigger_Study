import sys, os, ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetLineWidth(2)
ROOT.gStyle.SetFrameLineWidth(2)
ROOT.TH1.SetDefaultSumw2()
ROOT.gStyle.SetErrorX(0)

def drawETratio(evtsTree):

    h2 = ROOT.TH2F("h2", "h2", 100, -0.25, 49.75, 720, 0., 20.0)

    evtsTree.Draw("tPFA1.TP_energy/TP_energy:tPFA1.TP_energy>>h2", "tp_soi!=255 && TP_energy>0.5 && tPFA1.TP_energy>0.5")

    h2 = ROOT.gDirectory.Get("h2")

    return h2


def printETratio(histo):

    l = ROOT.TLine(-0.5, 1, 50.5, 1)
    l.SetLineWidth(2)
    l.SetLineColor(ROOT.kBlack)
    l.SetLineStyle(2)

    c1 = ROOT.TCanvas("canvas", "canvas", 2400, int(0.8*1800.0)); c1.cd(); c1.SetLogz()

    ROOT.gPad.SetTopMargin(0.02625)
    ROOT.gPad.SetBottomMargin(0.13375)
    ROOT.gPad.SetLeftMargin(0.11)
    ROOT.gPad.SetRightMargin(0.12)

    magicFactor = 0.8; magicFactor2 = 0.6

    p = histo.ProfileX("p", 1, -1, "")
    p.SetMarkerStyle(8)
    p.SetMarkerSize(2)
    p.SetLineWidth(2)
    p.SetMarkerColor(ROOT.kBlack)
    p.SetLineColor(ROOT.kBlack)
    p.Sumw2()

    histo.SetTitle("")
    histo.GetXaxis().SetTitle("PFA1 TP E_{T}")
    histo.GetYaxis().SetTitle("E_{T,PFA1} / E_{T,PFA2}")

    histo.GetYaxis().SetLabelSize(magicFactor*0.055); histo.GetYaxis().SetTitleSize(magicFactor*0.06); histo.GetYaxis().SetTitleOffset(0.9/magicFactor)
    histo.GetXaxis().SetLabelSize(magicFactor*0.055); histo.GetXaxis().SetTitleSize(magicFactor*0.08); histo.GetXaxis().SetTitleOffset(0.6/magicFactor2)
    histo.GetZaxis().SetLabelSize(magicFactor*0.055); histo.GetZaxis().SetTitleSize(magicFactor*0.06)
    histo.SetContour(255)
    histo.GetYaxis().SetRangeUser(0.6,1.8)

    histo.Draw("COLZ")
    l.Draw("SAME")
    p.Draw("SAME")

    c1.SaveAs("etRatioPlot.pdf")

if __name__ == '__main__':

    PFA1File = str(sys.argv[1])
    PFA2File = str(sys.argv[2])
    
    fPFA1 = ROOT.TFile.Open(PFA1File, "READ")
    tPFA1 = fPFA1.Get("compareReemulRecoSeverity9/matches")
    
    fPFA2 = ROOT.TFile.Open(PFA2File, "READ")
    tPFA2 = fPFA2.Get("compareReemulRecoSeverity9/matches")

    tPFA2.AddFriend(tPFA1, "tPFA1")
    
    aHisto = drawETratio(tPFA2)
    printETratio(aHisto)

    fPFA1.Close()
    fPFA2.Close()

