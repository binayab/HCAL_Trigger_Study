import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetLineWidth(4)
ROOT.gStyle.SetPaintTextFormat("3.2f")
ROOT.gStyle.SetFrameLineWidth(0)

pulses = {"TS0" : {"hist" : ROOT.TH1D("TS0", "TS0", 8, -0.5, 7.5), "bins" : [50, 17, 5, 0, 0, 0, 0, 0], "color" : ROOT.TColor.GetColor("#984ea3")},
          "TS1" : {"hist" : ROOT.TH1D("TS1", "TS1", 8, -0.5, 7.5), "bins" : [0, 40, 13, 5, 0, 0, 0, 0], "color" : ROOT.TColor.GetColor("#377eb8")},
          "TS2" : {"hist" : ROOT.TH1D("TS2", "TS2", 8, -0.5, 7.5), "bins" : [0, 0, 45, 15, 5, 1, 0, 0], "color" : ROOT.TColor.GetColor("#4daf4a")},
          "TS3" : {"hist" : ROOT.TH1D("TS3", "TS3", 8, -0.5, 7.5), "bins" : [0, 0, 0, 150, 50, 8, 0, 0], "color" : ROOT.TColor.GetColor("#e41a1c")},
          "TS4" : {"hist" : ROOT.TH1D("TS4", "TS4", 8, -0.5, 7.5), "bins" : [0, 0, 0, 0, 24, 7, 2, 0], "color" : ROOT.TColor.GetColor("#ff7f00")},
          "TS5" : {"hist" : ROOT.TH1D("TS5", "TS5", 8, -0.5, 7.5), "bins" : [0, 0, 0, 0, 0, 23, 7, 1], "color" : ROOT.TColor.GetColor("#999999")},
          "TS6" : {"hist" : ROOT.TH1D("TS6", "TS6", 8, -0.5, 7.5), "bins" : [0, 0, 0, 0, 0, 0, 30, 10], "color" : ROOT.TColor.GetColor("#a65628")},
          "TS7" : {"hist" : ROOT.TH1D("TS7", "TS7", 8, -0.5, 7.5), "bins" : [0, 0, 0, 0, 0, 0, 0, 0], "color" : ROOT.TColor.GetColor("#f781bf")}
}

binLabels = ["-3BX", "-2BX", "-1BX", "0", "+1BX", "+2BX", "+3BX", "+4BX"]

def setHistoOptions(histo):
    histo.SetMinimum(0)
    histo.GetYaxis().SetTickLength(0)
    histo.GetXaxis().SetTickLength(0)
    histo.GetYaxis().SetLabelSize(0)
    histo.GetXaxis().SetLabelSize(0.08)
    histo.GetYaxis().SetTitle("A.U.")
    histo.GetYaxis().SetTitleSize(0.06)
    histo.GetXaxis().SetTitleSize(0.07)
    histo.GetXaxis().SetTitleOffset(0.75)
    histo.GetYaxis().SetTitleOffset(0.3)
    histo.SetTitle("")

fullPulse = ROOT.TH1F("FullPulse", "FullPulse", 8, -0.5, 7.5)
for ts in xrange(0,8):
    fullPulse.GetXaxis().SetBinLabel(ts+1,binLabels[ts])

for pulse, pulseDict in pulses.iteritems():
    for ts in xrange(len(pulseDict["bins"])):
        pulseDict["hist"].SetBinContent(ts+1, pulseDict["bins"][ts])
        pulseDict["hist"].GetXaxis().SetBinLabel(ts+1, binLabels[ts])

    setHistoOptions(pulseDict["hist"])
    pulseDict["hist"].SetFillColorAlpha(pulseDict["color"],1.0)
    pulseDict["hist"].SetLineWidth(0)

for pulse, pulseDict in pulses.iteritems():
    fullPulse.Add(pulseDict["hist"])

for ts in xrange(fullPulse.GetNbinsX()+1):
    print "ts %d, %d"%(ts,fullPulse.GetBinContent(ts))

canvas = ROOT.TCanvas("canvas", "canvas", 2400, 1800); canvas.cd()

ROOT.gPad.SetTopMargin(0.02)
ROOT.gPad.SetBottomMargin(0.08)
ROOT.gPad.SetLeftMargin(0.06)
ROOT.gPad.SetRightMargin(0.02)

fullPulse.SetLineWidth(4)
fullPulse.SetLineStyle(7)
fullPulse.SetLineColor(ROOT.kBlack)

setHistoOptions(fullPulse)

fullPulse.Draw("HIST")

pulses["TS7"]["hist"].Draw("HIST SAME")
pulses["TS6"]["hist"].Draw("HIST SAME")
pulses["TS5"]["hist"].Draw("HIST SAME")
pulses["TS4"]["hist"].Draw("HIST SAME")
pulses["TS3"]["hist"].Draw("HIST SAME")
pulses["TS2"]["hist"].Draw("HIST SAME")
pulses["TS1"]["hist"].Draw("HIST SAME")
pulses["TS0"]["hist"].Draw("HIST SAME")

canvas.SaveAs("ootPUpulse_total.pdf")

canvas2 = ROOT.TCanvas("canvas2", "canvas2", 2400, 1800); canvas2.cd()

ROOT.gPad.SetTopMargin(0.02)
ROOT.gPad.SetBottomMargin(0.08)
ROOT.gPad.SetLeftMargin(0.06)
ROOT.gPad.SetRightMargin(0.02)

pulses["TS3"]["hist"].Draw("HIST")

canvas2.SaveAs("ootPUpulse_signal.pdf")

canvas3 = ROOT.TCanvas("canvas3", "canvas3", 2400, 1800); canvas3.cd()

ROOT.gPad.SetTopMargin(0.02)
ROOT.gPad.SetBottomMargin(0.08)
ROOT.gPad.SetLeftMargin(0.06)
ROOT.gPad.SetRightMargin(0.02)

fullPulse.Draw("HIST")

canvas3.SaveAs("ootPUpulse_sigandpu.pdf")
