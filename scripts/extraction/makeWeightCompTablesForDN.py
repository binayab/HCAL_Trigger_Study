#!/usr/bin/env python

import argparse
from collections import defaultdict

def writeHeader(outfile):

    outfile.write("\\rotatebox{0}{\n")
    outfile.write("\def\\arraystretch{1.8}\n")
    outfile.write("     \\begin{tabular}{|c|c|c|c|c|c|c|c|c|}\n")
    outfile.write("         \hline\n")
    outfile.write("         \phantom{\\null} & \multicolumn{2}{c|}{\\boldmath\\textbf{\PFAonep}} & \multicolumn{2}{c|}{\\boldmath\\textbf{\PFAtwop}}\\\\\\hline\n")
    outfile.write("         \phantom{\\null} & \multicolumn{1}{c|}{\\textbf{No-Depth}} & \multicolumn{1}{c|}{\\textbf{Depth-Averaged}} & \multicolumn{1}{c|}{\\textbf{No-Depth}} & \multicolumn{1}{c|}{\\textbf{Depth-Averaged}}\\\\\\hline\n")

def writeFooter(outfile):

    outfile.write("     \end{tabular}\n")
    outfile.write("\n")
    outfile.write("}\n")

def write2Latex(outfile, m, det):

    ietaLow = -1; ietaHigh = -1
    if   det == "HB":  ietaLow = 1;  ietaHigh = 16
    elif det == "HE1": ietaLow = 17; ietaHigh = 20
    elif det == "HE2": ietaLow = 21; ietaHigh = 28
    else: return 

    for ieta in xrange(1, 29):
        if ieta >= ietaLow and ieta <= ietaHigh:
            pfa1pnodepthmean   = m["PFA1pMean"][str(ieta)]["0"]
            pfa1pwithdepthmean = m["PFA1pMean"][str(ieta)]["Ave"]

            pfa2pnodepthmean   = m["PFA2pMean"][str(ieta)]["0"]
            pfa2pwithdepthmean = m["PFA2pMean"][str(ieta)]["Ave"]

            outfile.write("         \\textbf{%d}   & $%s$ & $%s$ & $%s$ & $%s$ \\\\\\hline"%(ieta, pfa1pnodepthmean, pfa1pwithdepthmean, pfa2pnodepthmean, pfa2pwithdepthmean))

            if ieta == ietaHigh: outfile.write("\\rowcolor{lightgray}\n")
            else:                outfile.write("\n")

    pfa1pnodepthmean   = m["PFA1pMean"][det]["0"]
    pfa1pwithdepthmean = m["PFA1pMean"][det]["Ave"]

    pfa2pnodepthmean   = m["PFA2pMean"][det]["0"]
    pfa2pwithdepthmean = m["PFA2pMean"][det]["Ave"]

    outfile.write("         \\textbf{%s} & \\textbf{$%s$} & \\textbf{$%s$} & \\textbf{$%s$} & \\textbf{$%s$} \\\\\\hline\n"%(det, pfa1pnodepthmean, pfa1pwithdepthmean, pfa2pnodepthmean, pfa2pwithdepthmean))

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

        m.setdefault(topKey, {}).setdefault(str(ieta), {}).setdefault(str(depth), weight)

        line = infile.readline()

#parser = argparse.ArgumentParser()
#parser.add_argument("--tag", dest="tag", help="Custom tag for output", type=str, required=True)
#args = parser.parse_args()

#tag = args.tag

mapEverything = {}

pfa1pNoDepthMean   = "/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/plots/Weights/PFA1p/NoDepth_TTbar_OOT/weightSummaryMean.txt"
pfa1pWithDepthMean = "/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/plots/Weights/PFA1p/WithDepth_TTbar_OOT/weightSummaryMean.txt"

pfa2pNoDepthMean   = "/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/plots/Weights/PFA2p/NoDepth_TTbar_OOT/weightSummaryMean.txt"
pfa2pWithDepthMean = "/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/plots/Weights/PFA2p/WithDepth_TTbar_OOT/weightSummaryMean.txt"

pfa1p_ndm  = open(pfa1pNoDepthMean,  "r")
pfa1p_wdm  = open(pfa1pWithDepthMean,"r")

pfa2p_ndm  = open(pfa2pNoDepthMean,  "r")
pfa2p_wdm  = open(pfa2pWithDepthMean,"r")

fillMap(pfa1p_ndm, mapEverything, "PFA1pMean")
fillMap(pfa1p_wdm, mapEverything, "PFA1pMean")

fillMap(pfa2p_ndm, mapEverything, "PFA2pMean")
fillMap(pfa2p_wdm, mapEverything, "PFA2pMean")

outfileHB = open("WeightsHB.tex", "w")
outfileHE = open("WeightsHE.tex", "w")

writeHeader(outfileHB); writeHeader(outfileHE)
write2Latex(outfileHB, mapEverything, "HB")
write2Latex(outfileHE, mapEverything, "HE1")
write2Latex(outfileHE, mapEverything, "HE2")
writeFooter(outfileHB); writeFooter(outfileHE)
