#!/usr/bin/env python

import ROOT, sys, numpy
from array import array

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetFrameLineWidth(2)
ROOT.gStyle.SetPaintTextFormat("3.2f")
ROOT.gErrorIgnoreLevel = ROOT.kWarning
ROOT.gStyle.SetEndErrorSize(5.0)
ROOT.TH1.SetDefaultSumw2()

def getAverageWeights(argv):

    wavearr = array('d')
    wstdarr = array('d')
    for ieta in xrange(len(argv[0])):
        wave = 0
        wstdtemp = array('d') 
        for warr in argv:
            wave += warr[ieta]
            wstdtemp.append(warr[ieta])

        wave /= len(argv)
        wstd = numpy.std(wstdtemp)        

        wavearr.append(wave)
        wstdarr.append(wstd)

    return wavearr, wstdarr

def parseFile(f):

    line = f.readline()

    weights = array('d')
    errors = array('d') 
    
    count = 0
    while line:

        if "&" not in line or "HB" in line or "HE1" in line or "HE2" in line:
            line = f.readline()
            continue

        linesplit = [x.strip() for x in line.split(' & ')]

        ieta = float(linesplit[0])

        weightAndError = linesplit[1].strip("$").split("_")

        weight = float(weightAndError[0])
        error  = float(weightAndError[1].strip("{\pm ").split("}")[0])

        weights.append(weight); errors.append(error)
        count += 1
        line = f.readline()

    return weights, errors

tttag = "TTbar"; nutag = "NuGun"
ttpaths = []; nupaths = []
ttweights = []; nuweights = []
tterrors = []; nuerrors = []
ttgraphs = []; nugraphs = []
xVals = []
nupaths.append("/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/plots/Weights/PFA1p/NoDepth_NuGun_25PU_OOT/weightSummaryMean.txt")
nupaths.append("/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/plots/Weights/PFA1p/NoDepth_NuGun_50PU_OOT/weightSummaryMean.txt")  
nupaths.append("/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/plots/Weights/PFA1p/NoDepth_NuGun_75PU_OOT/weightSummaryMean.txt")  
nupaths.append("/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/plots/Weights/PFA1p/NoDepth_NuGun_100PU_OOT/weightSummaryMean.txt") 

ttpaths.append("/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/plots/Weights/PFA1p/NoDepth_TTbar_25PU_OOT/weightSummaryMean.txt")
ttpaths.append("/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/plots/Weights/PFA1p/NoDepth_TTbar_50PU_OOT/weightSummaryMean.txt")  
ttpaths.append("/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/plots/Weights/PFA1p/NoDepth_TTbar_75PU_OOT/weightSummaryMean.txt")  
ttpaths.append("/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/plots/Weights/PFA1p/NoDepth_TTbar_100PU_OOT/weightSummaryMean.txt") 

for path in ttpaths:

    f = open(path, "r")
    y, yerr = parseFile(f)
    f.close()

    ttweights.append(y); tterrors.append(yerr)

for path in nupaths:

    f = open(path, "r")
    y, yerr = parseFile(f)
    f.close()

    nuweights.append(y); nuerrors.append(yerr)

ttaveweights, ttstd = getAverageWeights(ttweights)
nuaveweights, nustd = getAverageWeights(nuweights)

ttx = array('d')
nux = array('d')
ietaWidth = array('d')
ieta0Width = array('d')
x25 = array('d'); x50 = array('d'); x75 = array('d'); x100 = array('d')
for i in xrange(1, 29):
    x25.append(float(i)-3.0*0.083333333)
    x50.append(float(i)-0.08333333)
    x75.append(float(i)+0.08333333)
    x100.append(float(i)+3.0*0.083333333)
    ttx.append(float(i)-0.125)
    nux.append(float(i)+0.125)
    ietaWidth.append(0.08333333)
    ieta0Width.append(0)

xVals.append(x25); xVals.append(x50); xVals.append(x75); xVals.append(x100)
ttavegraph = ROOT.TGraphErrors(28, ttx, ttaveweights, ieta0Width, ttstd)
nuavegraph = ROOT.TGraphErrors(28, nux, nuaveweights, ieta0Width, nustd)

for i in xrange(len(ttweights)): ttgraphs.append(ROOT.TGraphErrors(28, xVals[i], ttweights[i],  ietaWidth, tterrors[i]))
for i in xrange(len(nuweights)): nugraphs.append(ROOT.TGraphErrors(28, xVals[i], nuweights[i],  ietaWidth, nuerrors[i]))

#ttcolors = [ROOT.TColor.GetColor("#a6cee3"), ROOT.TColor.GetColor("#b2df8a"), ROOT.TColor.GetColor("#cab2d6"), ROOT.TColor.GetColor("#fb9a99")]
#nucolors = [ROOT.TColor.GetColor("#1f78b4"), ROOT.TColor.GetColor("#33a02c"), ROOT.TColor.GetColor("#6a3d9a"), ROOT.TColor.GetColor("#e31a1c")]

ttcolors = [ROOT.TColor.GetColor("#9ecae1"), ROOT.TColor.GetColor("#6baed6"), ROOT.TColor.GetColor("#2171b5"), ROOT.TColor.GetColor("#08306b")]
nucolors = [ROOT.TColor.GetColor("#a1d99b"), ROOT.TColor.GetColor("#74c476"), ROOT.TColor.GetColor("#238b45"), ROOT.TColor.GetColor("#00441b")]

width = 0
size  = 2
ttstyle = 20
nustyle = 22

ttavegraph.SetLineColor(ROOT.kBlack); ttavegraph.SetMarkerColor(ROOT.kBlack); ttavegraph.SetLineWidth(2); ttavegraph.SetMarkerSize(2); ttavegraph.SetMarkerStyle(20)
nuavegraph.SetLineColor(ROOT.kOrange+8); nuavegraph.SetMarkerColor(ROOT.kOrange+8); nuavegraph.SetLineWidth(2); nuavegraph.SetMarkerSize(2); nuavegraph.SetMarkerStyle(22)

for graph in ttgraphs:
    index = ttgraphs.index(graph)
    graph.SetLineColor(ttcolors[index])
    graph.SetMarkerColor(ttcolors[index])
    graph.SetFillColorAlpha(ttcolors[index],0.15)
    graph.SetLineWidth(width)
    graph.SetMarkerSize(size)
    graph.SetMarkerStyle(ttstyle)
    graph.SetLineStyle(3)

for graph in nugraphs:
    index = nugraphs.index(graph)
    graph.SetLineColor(nucolors[index])
    graph.SetFillColorAlpha(nucolors[index],0.15)
    graph.SetMarkerColor(nucolors[index])
    graph.SetLineWidth(width)
    graph.SetMarkerSize(size)
    graph.SetMarkerStyle(nustyle)

dummy = ROOT.TH1F("h", ";;w_{SOI-1}", 168, 0.5, 28.5)
dummy.GetYaxis().SetRangeUser(-1.7,0.7)
dummy.GetYaxis().SetLabelSize(0.055); dummy.GetYaxis().SetTitleSize(0.095); dummy.GetYaxis().SetTitleOffset(0.4)
dummy.GetXaxis().SetLabelSize(0.055); dummy.GetXaxis().SetTitleSize(0.095); dummy.GetXaxis().SetTitleOffset(0.7)
dummy.SetLineWidth(0)

masterLab = 0.055; masterTitle = 0.095
pad1 = 0.6; pad2 = 0.15; pad3 = 0.25

dummyZoom1 = ROOT.TH1F("hZoom1", ";;", 168, 0.5, 28.5)
dummyZoom1.GetYaxis().SetRangeUser(-0.67,-0.35)
dummyZoom1.GetYaxis().SetLabelSize(masterLab/(pad2/0.6)); dummyZoom1.GetYaxis().SetTitleSize(masterTitle/(pad2/0.6)); dummyZoom1.GetYaxis().SetTitleOffset(0.9)
dummyZoom1.GetXaxis().SetLabelSize(masterLab/(pad2/0.6)); dummyZoom1.GetXaxis().SetTitleSize(masterTitle/(pad2/0.6)); dummyZoom1.GetXaxis().SetTitleOffset(0.9)
dummyZoom1.SetLineWidth(0)

dummyZoom2 = ROOT.TH1F("hZoom2", ";|i#eta|;", 168, 0.5, 28.5)
dummyZoom2.GetYaxis().SetRangeUser(-0.65,-0.25)
dummyZoom2.GetYaxis().SetLabelSize(masterLab/(pad3/0.6)); dummyZoom2.GetYaxis().SetTitleSize(masterTitle/(pad3/0.6)); dummyZoom2.GetYaxis().SetTitleOffset(0.9)
dummyZoom2.GetXaxis().SetLabelSize(masterLab/(pad3/0.6)); dummyZoom2.GetXaxis().SetTitleSize(masterTitle/(pad3/0.6)); dummyZoom2.GetXaxis().SetTitleOffset(0.6)
dummyZoom2.SetLineWidth(0)

c = ROOT.TCanvas("c", "c", 1600, 1200)
c.Divide(1,3,0,0)
c.cd(1)
ROOT.gPad.SetGridx()
ROOT.gPad.SetGridy()
ROOT.gPad.SetTopMargin(0.05)
ROOT.gPad.SetBottomMargin(0)
ROOT.gPad.SetRightMargin(0.02)
ROOT.gPad.SetLeftMargin(0.08)

c.cd(2)
ROOT.gPad.SetTopMargin(0.0)
ROOT.gPad.SetBottomMargin(0.0)
ROOT.gPad.SetRightMargin(0.02)
ROOT.gPad.SetLeftMargin(0.08)

c.cd(3)
ROOT.gPad.SetTopMargin(0.0)
ROOT.gPad.SetBottomMargin(0.4)
ROOT.gPad.SetRightMargin(0.02)
ROOT.gPad.SetLeftMargin(0.08)

c.cd(1)
ROOT.gPad.SetPad(0,0.4,1,1)
dummy.Draw()
for graph in ttgraphs:
    graph.Draw("2SAME")
    graph.Draw("2SAME")
for graph in nugraphs:
    graph.Draw("2SAME")
    graph.Draw("2SAME")
for graph in ttgraphs: graph.Draw("XEP SAME")
for graph in nugraphs: graph.Draw("XEP SAME")

c.cd(2)
ROOT.gPad.SetGridx()
ROOT.gPad.SetGridy()
ROOT.gPad.SetPad(0,0.25,1,0.4)

dummyZoom1.GetYaxis().SetNdivisions(6,5,0)
dummyZoom1.Draw()
for graph in ttgraphs:
    graph.Draw("2SAME")
    graph.Draw("XP SAME")

c.cd(3)
ROOT.gPad.SetGridx()
ROOT.gPad.SetGridy()
ROOT.gPad.SetPad(0,0.0,1,0.25)

dummyZoom2.GetYaxis().SetNdivisions(6,5,0)
dummyZoom2.Draw()
for graph in nugraphs:
    graph.Draw("2SAME")
    graph.Draw("XP SAME")

c.SaveAs("weightsPlot.pdf")
