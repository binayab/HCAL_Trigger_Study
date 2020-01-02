import sys, os, ROOT, numpy

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetLineWidth(2)
ROOT.gStyle.SetFrameLineWidth(4)
ROOT.gStyle.SetPaintTextFormat("3.2f")
ROOT.gStyle.SetErrorX(0)
ROOT.TH1.SetDefaultSumw2()

cut0ietaMap = {1 : [ -0.42, 0.56 ], 
               2 : [ -0.42, 0.58 ],
               3 : [ -0.41, 0.54 ],
               4 : [ -0.44, 0.58 ],
               5 : [ -0.46, 0.55 ],
               6 : [ -0.44, 0.57 ],
               7 : [ -0.45, 0.53 ],
               8 : [ -0.45, 0.54 ],
               9 : [ -0.46, 0.56 ],
               10 :[ -0.45, 0.55 ],
               11 :[ -0.48, 0.55 ],
               12 :[ -0.47, 0.56 ],
               13 :[ -0.50, 0.55 ],
               14 :[ -0.51, 0.59 ],
               15 :[ -0.54, 0.61 ],
               16 :[ -0.54, 0.57 ],
               17 :[ -0.52, 0.47 ],
               18 :[ -0.53, 0.50 ],
               19 :[ -0.51, 0.45 ],
               20 :[ -0.52, 0.47 ],
               21 :[ -0.63, 0.64 ],
               22 :[ -0.69, 0.71 ],
               23 :[ -0.78, 0.75 ],
               24 :[ -0.89, 0.01 ],
               25 :[ -1.10, 0.80 ],
               26 :[ -1.27, 0.74 ],
               27 :[ -1.22, 0.78 ],
               28 :[ -1.75, 0.36 ]}

cut1ietaMap = {1 : [ -0.39, 0.29 ],
               2 : [ -0.38, 0.28 ],
               3 : [ -0.36, 0.27 ],
               4 : [ -0.39, 0.28 ],
               5 : [ -0.40, 0.26 ],
               6 : [ -0.38, 0.26 ],
               7 : [ -0.40, 0.27 ],
               8 : [ -0.40, 0.27 ],
               9 : [ -0.40, 0.24 ],
               10 :[ -0.40, 0.26 ],
               11 :[ -0.41, 0.27 ],
               12 :[ -0.40, 0.27 ],
               13 :[ -0.41, 0.25 ],
               14 :[ -0.43, 0.29 ],
               15 :[ -0.46, 0.30 ],
               16 :[ -0.46, 0.28 ],
               17 :[ -0.45, 0.21 ],
               18 :[ -0.46, 0.25 ],
               19 :[ -0.44, 0.22 ],
               20 :[ -0.44, 0.22 ],
               21 :[ -0.57, 0.34 ],
               22 :[ -0.63, 0.40 ],
               23 :[ -0.72, 0.01 ],
               24 :[ -0.88, 0.01 ],
               25 :[ -1.09, 0.01 ],
               26 :[ -1.27, 0.63 ],
               27 :[ -1.21, 0.01 ],
               28 :[ -1.75, 0.36 ]}

cut2ietaMap = {1 : [ -0.36, 0.19 ],
               2 : [ -0.35, 0.19 ],
               3 : [ -0.34, 0.19 ],
               4 : [ -0.37, 0.19 ],
               5 : [ -0.38, 0.18 ],
               6 : [ -0.35, 0.19 ],
               7 : [ -0.37, 0.18 ],
               8 : [ -0.37, 0.18 ],
               9 : [ -0.37, 0.17 ],
               10 :[ -0.37, 0.18 ],
               11 :[ -0.37, 0.19 ],
               12 :[ -0.37, 0.18 ],
               13 :[ -0.38, 0.18 ],
               14 :[ -0.39, 0.20 ],
               15 :[ -0.43, 0.01 ],
               16 :[ -0.42, 0.19 ],
               17 :[ -0.42, 0.16 ],
               18 :[ -0.43, 0.17 ],
               19 :[ -0.41, 0.15 ],
               20 :[ -0.41, 0.15 ],
               21 :[ -0.54, 0.24 ],
               22 :[ -0.60, 0.90 ],
               23 :[ -0.70, 0.01 ],
               24 :[ -0.82, 0.39 ],
               25 :[ -1.06, 0.01 ],
               26 :[ -1.25, 0.01 ],
               27 :[ -1.18, 0.01 ],
               28 :[ -1.75, 0.36 ]}

cut3ietaMap = {1 : [ -0.33, 0.01 ],
               2 : [ -0.32, 0.16 ],
               3 : [ -0.30, 0.16 ],
               4 : [ -0.33, 0.01 ],
               5 : [ -0.35, 0.15 ],
               6 : [ -0.33, 0.15 ],
               7 : [ -0.34, 0.01 ],
               8 : [ -0.33, 0.01 ],
               9 : [ -0.33, 0.01 ],
               10 :[ -0.34, 0.15 ],
               11 :[ -0.33, 0.16 ],
               12 :[ -0.33, 0.15 ],
               13 :[ -0.34, 0.14 ],
               14 :[ -0.35, 0.01 ],
               15 :[ -0.38, 0.01 ],
               16 :[ -0.38, 0.01 ],
               17 :[ -0.39, 0.01 ],
               18 :[ -0.39, 0.14 ],
               19 :[ -0.37, 0.01 ],
               20 :[ -0.37, 0.01 ],
               21 :[ -0.50, 0.01 ],
               22 :[ -0.56, 0.01 ],
               23 :[ -0.65, 0.01 ],
               24 :[ -0.79, 0.01 ],
               25 :[ -1.02, 0.01 ],
               26 :[ -1.21, 0.01 ],
               27 :[ -1.13, 0.01 ],
               28 :[ -1.75, 0.36 ]}

cut4ietaMap = {1 : [ -0.34, 0.01 ],
               2 : [ -0.34, 0.01 ],
               3 : [ -0.32, 0.13 ],
               4 : [ -0.35, 0.01 ],
               5 : [ -0.36, 0.12 ],
               6 : [ -0.34, 0.12 ],
               7 : [ -0.35, 0.01 ],
               8 : [ -0.35, 0.01 ],
               9 : [ -0.34, 0.01 ],
               10 :[ -0.35, 0.12 ],
               11 :[ -0.35, 0.13 ],
               12 :[ -0.34, 0.12 ],
               13 :[ -0.36, 0.12 ],
               14 :[ -0.37, 0.01 ],
               15 :[ -0.40, 0.01 ],
               16 :[ -0.39, 0.01 ],
               17 :[ -0.41, 0.01 ],
               18 :[ -0.41, 0.11 ],
               19 :[ -0.39, 0.01 ],
               20 :[ -0.39, 0.01 ],
               21 :[ -0.51, 0.01 ],
               22 :[ -0.56, 0.01 ],
               23 :[ -0.66, 0.01 ],
               24 :[ -0.79, 0.01 ],
               25 :[ -1.00, 0.01 ],
               26 :[ -1.17, 0.00 ],
               27 :[ -1.09, 0.01 ],
               28 :[ -1.75, 0.35 ]}

cut5ietaMap = {1 : [ -0.34, 0.01 ],
               2 : [ -0.34, 0.05 ],
               3 : [ -0.32, 0.10 ],
               4 : [ -0.34, 0.01 ],
               5 : [ -0.36, 0.10 ],
               6 : [ -0.34, 0.01 ],
               7 : [ -0.35, 0.01 ],
               8 : [ -0.35, 0.01 ],
               9 : [ -0.34, 0.02 ],
               10 :[ -0.35, 0.10 ],
               11 :[ -0.35, 0.11 ],
               12 :[ -0.34, 0.11 ],
               13 :[ -0.36, 0.01 ],
               14 :[ -0.37, 0.01 ],
               15 :[ -0.39, 0.01 ],
               16 :[ -0.39, 0.01 ],
               17 :[ -0.41, 0.01 ],
               18 :[ -0.41, 0.10 ],
               19 :[ -0.40, 0.01 ],
               20 :[ -0.39, 0.09 ],
               21 :[ -0.51, 0.01 ],
               22 :[ -0.56, 0.00 ],
               23 :[ -0.65, 0.01 ],
               24 :[ -0.77, 0.01 ],
               25 :[ -0.97, 0.00 ],
               26 :[ -1.13, 0.00 ],
               27 :[ -1.05, 0.00 ],
               28 :[ -1.75, 0.34 ]}

colors = ["#e41a1c",
          "#377eb8",
          "#4daf4a",
          "#984ea3",
          "#ff7f00",
          "#ffff33",
          "#a65628",
          "#f781bf"
          ]

histos = {}
for ieta in xrange(1,29):
    histos[ieta] = ROOT.TH1F("h_%s"%(ieta), "h_%s"%(ieta), 6, 0.5, 6.5)

for ieta, valPair in cut0ietaMap.iteritems():
    histos[ieta].SetBinContent(1, valPair[0])
#    histos[ieta].SetBinError(1, valPair[1])
    histos[ieta].GetXaxis().SetBinLabel(1, "TS_{SOI-1} > 0")

for ieta, valPair in cut1ietaMap.iteritems():
    histos[ieta].SetBinContent(2, valPair[0])
#    histos[ieta].SetBinError(2, valPair[1])
    histos[ieta].GetXaxis().SetBinLabel(2, "TS_{SOI-1} > 1")

for ieta, valPair in cut2ietaMap.iteritems():
    histos[ieta].SetBinContent(3, valPair[0])
#    histos[ieta].SetBinError(3, valPair[1])
    histos[ieta].GetXaxis().SetBinLabel(3, "TS_{SOI-1} > 2")

for ieta, valPair in cut3ietaMap.iteritems():
    histos[ieta].SetBinContent(4, valPair[0])
#    histos[ieta].SetBinError(4, valPair[1])
    histos[ieta].GetXaxis().SetBinLabel(4, "TS_{SOI-1} > 3")

for ieta, valPair in cut4ietaMap.iteritems():
    histos[ieta].SetBinContent(5, valPair[0])
#    histos[ieta].SetBinError(5, valPair[1])
    histos[ieta].GetXaxis().SetBinLabel(5, "TS_{SOI-1} > 4")
    
for ieta, valPair in cut5ietaMap.iteritems():
    histos[ieta].SetBinContent(6, valPair[0])
#    histos[ieta].SetBinError(6, valPair[1])
    histos[ieta].GetXaxis().SetBinLabel(6, "TS_{SOI-1} > 5")

def drawHistos(aCanvas, ietaRange, weightRange, tag):

    aCanvas.cd()
    aCanvas.SetGridy()
    aCanvas.SetGridx()

    ROOT.gPad.SetTopMargin(0.02)
    ROOT.gPad.SetLeftMargin(0.11)
    ROOT.gPad.SetBottomMargin(0.05)
    ROOT.gPad.SetRightMargin(0.01)

    iamLegend = ROOT.TLegend(0.8, 0.1, 0.95, 0.35, "", "trNDC")
    iamLegend.SetTextSize(0.03)

    cid = 0
    for ieta in xrange(ietaRange[0], ietaRange[1]):
        histos[ieta].SetMarkerSize(4)
        histos[ieta].SetLineWidth(4)
        histos[ieta].SetMarkerStyle(20)
        histos[ieta].GetXaxis().SetLabelSize(0.05)
        histos[ieta].GetYaxis().SetTitleSize(0.05)
        histos[ieta].GetYaxis().SetTitleOffset(1.1)
        histos[ieta].SetTitle("")
        histos[ieta].GetYaxis().SetTitle("w_{SOI-1}")
        histos[ieta].SetMarkerColor(ROOT.TColor.GetColor(colors[cid]))
        histos[ieta].SetLineColor(ROOT.TColor.GetColor(colors[cid]))
        histos[ieta].SetMinimum(weightRange[0])
        histos[ieta].SetMaximum(weightRange[1])

        iamLegend.AddEntry(histos[ieta], "|i#eta| = %s"%(ieta), "PL")

        histos[ieta].Draw("LP SAME")

        cid += 1

    iamLegend.Draw("SAME")
    aCanvas.SaveAs("cutStudy_%s.pdf"%(tag))

hb1Canvas = ROOT.TCanvas("c_HB1", "c_HB1", 2400, 2000)
hb2Canvas = ROOT.TCanvas("c_HB2", "c_HB2", 2400, 2000)
he1Canvas = ROOT.TCanvas("c_HE1", "c_HE1", 2400, 2000)
he2Canvas = ROOT.TCanvas("c_HE2", "c_HE2", 2400, 2000)

#drawHistos(hb1Canvas, [1,9],   [-2,0.5], "HB1")
#drawHistos(hb2Canvas, [9,17],  [-2,0.5], "HB2")
#drawHistos(he1Canvas, [17,21], [-2,0.5], "HE1")
#drawHistos(he2Canvas, [21,29], [-3.5,0.5], "HE2")

drawHistos(hb1Canvas, [1,9],   [-0.5,-0.25], "HB1")
drawHistos(hb2Canvas, [9,17],  [-0.6,-0.3], "HB2")
drawHistos(he1Canvas, [17,21], [-0.6,-0.3], "HE1")
drawHistos(he2Canvas, [21,29], [-3.5,-0.3], "HE2")
