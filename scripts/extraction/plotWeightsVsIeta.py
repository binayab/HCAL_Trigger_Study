#!/usr/bin/env python

import ROOT, sys, os, numpy, argparse
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

def fillMap(infile, m, topKey):

    line = infile.readline()
    
    while line:

        line = line.rstrip()

        if "ieta" not in line:
            line = infile.readline()
            continue

        ieta   = "NULL"
        depth  = "NULL"
        weight = "NULL"
        stat   = "NULL"
        syst   = "NULL"
        rms    = "NULL"

        linesplit = [x.strip() for x in line.split(',')]

        for chunk in linesplit:
            if   "ieta"   in chunk: ieta = chunk.split("ieta")[-1]
            elif "depth"  in chunk: depth = chunk.split("depth")[-1]
            elif "weight" in chunk: weight = chunk.split("weight")[-1]
            elif "stat"   in chunk: stat = chunk.split("stat")[-1]
            elif "syst"   in chunk: syst = chunk.split("syst")[-1]
            elif "rms"    in chunk: rms = chunk.split("rms")[-1]

        try:
            m.setdefault(topKey, {}).setdefault(int(ieta), {}).setdefault(int(depth), {}).setdefault("Weight", float(weight))
            m.setdefault(topKey, {}).setdefault(int(ieta), {}).setdefault(int(depth), {}).setdefault("RMS", float(rms))
        except:
            print "Ignoring parameter combination: %s, %s, %s"%(ieta, depth, weight)

        line = infile.readline()

def getWeightInfo(m):

    ttweights = {"25" : array('d'), "50" : array('d'), "75" : array('d'), "100" : array('d')}; nuweights = {"25" : array('d'), "50" : array('d'), "75" : array('d'), "100" : array('d')}
    ttrms     = {"25" : array('d'), "50" : array('d'), "75" : array('d'), "100" : array('d')}; nurms     = {"25" : array('d'), "50" : array('d'), "75" : array('d'), "100" : array('d')}

    for ieta in xrange(1,29):
       for pu in xrange(25,125,25):
            
            ttweights[str(pu)].append(m["TTbar%d"%(pu)][ieta][0]["Weight"])
            ttrms[str(pu)].append(m["TTbar%d"%(pu)][ieta][0]["RMS"])

            nuweights[str(pu)].append(m["NuGun%d"%(pu)][ieta][0]["Weight"])
            nurms[str(pu)].append(m["NuGun%d"%(pu)][ieta][0]["RMS"])
      
    return ttweights, ttrms, nuweights, nurms

parser = argparse.ArgumentParser()
parser.add_argument("--tag", dest="tag", help="Custom tag for output", type=str, required=True)
args = parser.parse_args()

USER = os.getenv("USER")

mapEverything = {}

ttgraphs = {"25" : [], "50" : [], "75" : [], "100" : []}; nugraphs = {"25" : [], "50" : [], "75" : [], "100" : []} 
xVals = {"25" : array('d'), "50" : array('d'), "75" : array('d'), "100" : array('d')} 

pfa_25PU_nugun =  "/uscms/home/%s/nobackup/HCAL_Trigger_Study/plots/Weights/%s/NoDepth_NuGun_25PU_OOT/weightSummaryMean.txt"%(USER,args.tag)
pfa_50PU_nugun =  "/uscms/home/%s/nobackup/HCAL_Trigger_Study/plots/Weights/%s/NoDepth_NuGun_50PU_OOT/weightSummaryMean.txt"%(USER,args.tag)
pfa_75PU_nugun =  "/uscms/home/%s/nobackup/HCAL_Trigger_Study/plots/Weights/%s/NoDepth_NuGun_75PU_OOT/weightSummaryMean.txt"%(USER,args.tag)
pfa_100PU_nugun = "/uscms/home/%s/nobackup/HCAL_Trigger_Study/plots/Weights/%s/NoDepth_NuGun_100PU_OOT/weightSummaryMean.txt"%(USER,args.tag)

pfa_25PU_ttbar =  "/uscms/home/%s/nobackup/HCAL_Trigger_Study/plots/Weights/%s/NoDepth_TTbar_25PU_OOT/weightSummaryMean.txt"%(USER,args.tag)
pfa_50PU_ttbar =  "/uscms/home/%s/nobackup/HCAL_Trigger_Study/plots/Weights/%s/NoDepth_TTbar_50PU_OOT/weightSummaryMean.txt"%(USER,args.tag)
pfa_75PU_ttbar =  "/uscms/home/%s/nobackup/HCAL_Trigger_Study/plots/Weights/%s/NoDepth_TTbar_75PU_OOT/weightSummaryMean.txt"%(USER,args.tag)
pfa_100PU_ttbar = "/uscms/home/%s/nobackup/HCAL_Trigger_Study/plots/Weights/%s/NoDepth_TTbar_100PU_OOT/weightSummaryMean.txt"%(USER,args.tag)

pfa_tt25 = open(pfa_25PU_ttbar, "r")
pfa_tt50 = open(pfa_50PU_ttbar, "r")
pfa_tt75 = open(pfa_75PU_ttbar, "r")
pfa_tt100 = open(pfa_100PU_ttbar, "r")

pfa_nu25 = open(pfa_25PU_nugun, "r")
pfa_nu50 = open(pfa_50PU_nugun, "r")
pfa_nu75 = open(pfa_75PU_nugun, "r")
pfa_nu100 = open(pfa_100PU_nugun, "r")

fillMap(pfa_tt25, mapEverything, "TTbar25")
fillMap(pfa_tt50, mapEverything, "TTbar50")
fillMap(pfa_tt75, mapEverything, "TTbar75")
fillMap(pfa_tt100, mapEverything, "TTbar100")

fillMap(pfa_nu25, mapEverything, "NuGun25")
fillMap(pfa_nu50, mapEverything, "NuGun50")
fillMap(pfa_nu75, mapEverything, "NuGun75")
fillMap(pfa_nu100, mapEverything, "NuGun100")

ttweights, ttrms, nuweights, nurms = getWeightInfo(mapEverything)

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

xVals["25"] = x25; xVals["50"] = x50; xVals["75"] = x75; xVals["100"] = x100

for pu in xVals.keys(): ttgraphs[pu] = ROOT.TGraphErrors(28, xVals[pu], ttweights[pu],  ietaWidth, ttrms[pu])
for pu in xVals.keys(): nugraphs[pu] = ROOT.TGraphErrors(28, xVals[pu], nuweights[pu],  ietaWidth, nurms[pu])

#ttcolors = {"25" : ROOT.TColor.GetColor("#9ecae1"), "50" : ROOT.TColor.GetColor("#6baed6"), "75" : ROOT.TColor.GetColor("#2171b5"), "100" : ROOT.TColor.GetColor("#08306b")}
#nucolors = {"25" : ROOT.TColor.GetColor("#a1d99b"), "50" : ROOT.TColor.GetColor("#74c476"), "75" : ROOT.TColor.GetColor("#238b45"), "100" : ROOT.TColor.GetColor("#00441b")}

ttcolors = {"25" : ROOT.TColor.GetColor("#bdd7e7"), "50" : ROOT.TColor.GetColor("#6baed6"), "75" : ROOT.TColor.GetColor("#3182bd"), "100" : ROOT.TColor.GetColor("#08519c")}
nucolors = {"25" : ROOT.TColor.GetColor("#bae4b3"), "50" : ROOT.TColor.GetColor("#74c476"), "75" : ROOT.TColor.GetColor("#31a354"), "100" : ROOT.TColor.GetColor("#006d2c")}

width = 0
size  = 2
ttstyle = 20
nustyle = 22

for pu in ttgraphs.keys():
    ttgraphs[pu].SetLineColor(ttcolors[pu])
    ttgraphs[pu].SetMarkerColor(ttcolors[pu])
    ttgraphs[pu].SetFillColorAlpha(ttcolors[pu],0.15)
    ttgraphs[pu].SetLineWidth(width)
    ttgraphs[pu].SetMarkerSize(size)
    ttgraphs[pu].SetMarkerStyle(ttstyle)
    ttgraphs[pu].SetLineStyle(3)

    nugraphs[pu].SetLineColor(nucolors[pu])
    nugraphs[pu].SetFillColorAlpha(nucolors[pu],0.15)
    nugraphs[pu].SetMarkerColor(nucolors[pu])
    nugraphs[pu].SetLineWidth(width)
    nugraphs[pu].SetMarkerSize(size)
    nugraphs[pu].SetMarkerStyle(nustyle)

dummy = ROOT.TH1F("h", ";;w_{SOI-1}", 168, 0.5, 28.5)
dummy.GetYaxis().SetRangeUser(-1.7,0.7)
dummy.GetYaxis().SetLabelSize(0.055); dummy.GetYaxis().SetTitleSize(0.095); dummy.GetYaxis().SetTitleOffset(0.4)
dummy.GetXaxis().SetLabelSize(0.055); dummy.GetXaxis().SetTitleSize(0.095); dummy.GetXaxis().SetTitleOffset(0.7)
dummy.SetLineWidth(0)

masterLab = 0.055; masterTitle = 0.095
pad1 = 0.6; pad2 = 0.15; pad3 = 0.25

dummyZoom1 = ROOT.TH1F("hZoom1", ";;", 168, 0.5, 28.5)
if args.tag == "PFA1p": dummyZoom1.GetYaxis().SetRangeUser(-0.67,-0.35)
else:                   dummyZoom1.GetYaxis().SetRangeUser(-1.54,-0.41)
dummyZoom1.GetYaxis().SetLabelSize(masterLab/(pad2/0.6)); dummyZoom1.GetYaxis().SetTitleSize(masterTitle/(pad2/0.6)); dummyZoom1.GetYaxis().SetTitleOffset(0.9)
dummyZoom1.GetXaxis().SetLabelSize(masterLab/(pad2/0.6)); dummyZoom1.GetXaxis().SetTitleSize(masterTitle/(pad2/0.6)); dummyZoom1.GetXaxis().SetTitleOffset(0.9)
dummyZoom1.SetLineWidth(0)

dummyZoom2 = ROOT.TH1F("hZoom2", ";|i#eta|;", 168, 0.5, 28.5)
if args.tag == "PFA1p": dummyZoom2.GetYaxis().SetRangeUser(-0.65,-0.25)
else:                   dummyZoom2.GetYaxis().SetRangeUser(-1.49,-0.41)
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
for pu, graph in ttgraphs.iteritems():
    graph.Draw("2SAME")
    graph.Draw("2SAME")
    nugraphs[pu].Draw("2SAME")
    nugraphs[pu].Draw("2SAME")
for pu, graph in ttgraphs.iteritems():
    graph.Draw("XEP SAME")
    nugraphs[pu].Draw("XEP SAME")

c.cd(2)
ROOT.gPad.SetGridx()
ROOT.gPad.SetGridy()
ROOT.gPad.SetPad(0,0.25,1,0.4)

dummyZoom1.GetYaxis().SetNdivisions(6,5,0)
dummyZoom1.Draw()
for pu, graph in ttgraphs.iteritems():
    graph.Draw("2SAME")
    graph.Draw("XP SAME")

c.cd(3)
ROOT.gPad.SetGridx()
ROOT.gPad.SetGridy()
ROOT.gPad.SetPad(0,0.0,1,0.25)

dummyZoom2.GetYaxis().SetNdivisions(6,5,0)
dummyZoom2.Draw()
for pu, graph in nugraphs.iteritems():
    graph.Draw("2SAME")
    graph.Draw("XP SAME")

c.SaveAs("weightsPlot_%s.pdf"%(args.tag))
