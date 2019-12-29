import sys, os, ROOT, subprocess

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetLineWidth(4)
ROOT.gStyle.SetFrameLineWidth(4)
ROOT.TH1.SetDefaultSumw2()

# From the events do a draw to make a 3D histo with RH or TP ET on z, TP/RH ratio on y and ieta on x
# Regardless if RH or TP ET on z, always impose TP ET > 0.5
def ratioUnpackVsReemul_Eta_ET(evtsTree):

    h3 = ROOT.TH3F("h3_ET", "h3_ET", 57, -28.5, 28.5, 721, -0.0139, 20.0139, 257, -0.25, 128.25)

    evtsTree.Draw("et:et/et_emul:ieta>>h3_ET", "et>0.0 && et_emul>0.0")

    h3 = ROOT.gDirectory.Get("h3_ET")

    return h3

# Make a TP/RH vs ieta 2D plot
def ratioUnpackVsReemul_Eta(outfile, histo, etRange = []):

    outfile.cd()

    htemp = histo.Clone()

    h2 = 0
    if   len(etRange) == 0: htemp.GetZaxis().SetRange(1, htemp.GetZaxis().GetNbins())
    elif len(etRange) == 1: htemp.GetZaxis().SetRange(htemp.GetZaxis().FindBin(etRange[0]),htemp.GetZaxis().FindBin(etRange[0]))
    elif len(etRange) == 2: htemp.GetZaxis().SetRange(htemp.GetZaxis().FindBin(etRange[0])+1,htemp.GetZaxis().FindBin(etRange[1]))

    htemp.GetZaxis().SetBit(ROOT.TAxis.kAxisRange)
    h2 = htemp.Project3D("yx")

    h2.SetTitle("")
    h2.GetXaxis().SetTitle("i#eta")
    h2.GetYaxis().SetTitle("E_{T,Unpacked} / E_{T,Reemul}")

    if   len(etRange) == 0: h2.Write("UnpackReemul_vs_Eta")
    elif len(etRange) == 1: h2.Write("UnpackReemul_vs_Eta_ET%0.1f"%(etRange[0]))
    elif len(etRange) == 2: h2.Write("UnpackReemul_vs_Eta_ET%0.1fto%0.1f"%(etRange[0],etRange[1]))

def ratioUnpackVsReemul(evtsTree):

    h3 = ROOT.TH3F("h3_ET_comp", "h3_ET_comp", 257, -0.25, 128.25, 257, -0.25, 128.25, 57, -28.5, 28.5)

    evtsTree.Draw("ieta:et_emul:et>>h3_ET_comp", "")

    h3 = ROOT.gDirectory.Get("h3_ET_comp")

    return h3

# 2D plot of Unpack vs Reemul with a selection on ieta
def ratioUnpackVsReemul_Comp(outfile, histo, ietaRange = [1,28]):

    outfile.cd()

    htempp = histo.Clone(histo.GetName()+"_pos")
    htempn = histo.Clone(histo.GetName()+"_neg")

    h2pos = 0; h2neg = 0; ietaStr = ""
    if len(ietaRange) == 1:
        htempp.GetZaxis().SetRange(htempp.GetZaxis().FindBin(ietaRange[0]), htempp.GetZaxis().FindBin(ietaRange[0]))
        htempn.GetZaxis().SetRange(htempn.GetZaxis().FindBin(-ietaRange[0]),htempn.GetZaxis().FindBin(-ietaRange[0]))

        ietaStr = "_ieta%d"%(ietaRange[0])
    elif len(ietaRange) == 2:
        htempp.GetZaxis().SetRange(htempp.GetZaxis().FindBin(ietaRange[0]), htempp.GetZaxis().FindBin(ietaRange[1]))
        htempn.GetZaxis().SetRange(htempn.GetZaxis().FindBin(-ietaRange[1]),htempn.GetZaxis().FindBin(-ietaRange[0]))

        ietaStr = "_ieta%dto%d"%(ietaRange[0],ietaRange[1])

    htempp.GetZaxis().SetBit(ROOT.TAxis.kAxisRange)
    htempn.GetZaxis().SetBit(ROOT.TAxis.kAxisRange)

    h2pos = htempp.Project3D("yx")
    h2neg = htempn.Project3D("yx")

    h2pos.Add(h2neg)

    h2pos.SetTitle("")
    h2pos.GetYaxis().SetTitle("E_{T,Reemul} [GeV]")
    h2pos.GetXaxis().SetTitle("E_{T,Unpacked} [GeV]")

    h2pos.Write("UnpackReemul_vs_ET%s"%(ietaStr))

def analysis(inputDir, outputDir):

    onEOS = "store" in inputDir

    if not os.path.exists(outputDir): os.makedirs(outputDir)

    outFile = ROOT.TFile.Open(outputDir + "/ratios.root", "RECREATE")

    chain = ROOT.TChain("compare/tps")

    # Whether on EOS or locally, get the list of files to run on 
    proc = 0;  allItems = []
    if onEOS: 
        proc = subprocess.Popen(["xrdfs", "root://cmseos.fnal.gov", "ls", inputDir], stdout=subprocess.PIPE)
        allItems = proc.stdout.readlines();  allItems = [item.rstrip() for item in allItems]
    else:
        allItems = os.listdir(inputDir)

    # Add only honest root files to TChain
    for item in allItems:
        
        if ".root" not in item: continue
        if "ratio" in item:     continue
    
        if onEOS: chain.AddFile("root://cmseos.fnal.gov/"+item)
        else:     chain.AddFile(item)

    TPUnpackvReemulvEta      = ratioUnpackVsReemul_Eta_ET(chain); TPUnpackvReemulvEta.SetDirectory(0)
    TPUnpackvReemulvEta_Comp = ratioUnpackVsReemul(chain);        TPUnpackvReemulvEta_Comp.SetDirectory(0)

    for ieta in xrange(1,29): ratioUnpackVsReemul_Comp(outFile,TPUnpackvReemulvEta_Comp,[ieta])

    ratioUnpackVsReemul_Eta(outFile,TPUnpackvReemulvEta,[0.5,10])
    ratioUnpackVsReemul_Eta(outFile,TPUnpackvReemulvEta,[10, 1000])

    outFile.Close()
   
if __name__ == '__main__':

    inputDir  = str(sys.argv[1])
    outputDir = str(sys.argv[2])

    analysis(inputDir, outputDir)
