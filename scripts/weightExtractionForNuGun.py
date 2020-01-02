#!/usr/bin/env python

import sys, os, ROOT, numpy, argparse, math
from pu2nopuMap import PU2NOPUMAP 
from collections import defaultdict

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetLineWidth(2)
ROOT.gStyle.SetFrameLineWidth(4)
ROOT.gStyle.SetPaintTextFormat("3.2f")
ROOT.gStyle.SetErrorX(0)
ROOT.gErrorIgnoreLevel = ROOT.kWarning
ROOT.TH1.SetDefaultSumw2()
ROOT.TH2.SetDefaultSumw2()

class WeightExtractor:

    def __init__(self, scheme, inputFilePU, outputPath):

        self.outPath = outputPath              # Base outpath to write everything to
        self.cacheLoc = "%s/root"%(outputPath) # Location to cache histograms in root file

        # _My_ use of word "sample" is any TS >= SOI
        if scheme == "PFA2pp":
            self.tpPresamples = 2          # PFA2pp uses two presamples
            self.tpSamples = 2             # SOI and SOI+1 are used to sample non-PU pulse
        elif scheme == "PFA2p":
            self.tpPresamples = 1          # PFA2p uses two SOI and SOI+1 fully and SOI-1 presample
            self.tpSamples = 2             # SOI and SOI+1 are used to sample non-PU pulse
        elif scheme == "PFA1p":
            self.tpPresamples = 1          # PFA1 uses SOI fully and SOI-1 presample to subtract
            self.tpSamples = 1             # Only SOI is used to sample non-PU pulse
        elif scheme == "PFA1pp":
            self.tpPresamples = 2          # PFA1p uses SOI fully and SOI-2 and SOI-1 presamples to subtract
            self.tpSamples = 1             # Only SOI is used to sample non-PU pulse

        self.SOI = 3                       # SOI for 8TS digi is always 3
        self.offset = 3                    # We need this offset to scan 8TS digi starting from 0
        self.event = -1                    # Current event we are looking at
        self.scheme = scheme               # Which pulse filter scheme 
        self.ts2Cut = 3                    # Requirement on TS2 (SOI-1) > n ADC
        self.rebin = 2                     # Rebin factor for weight histograms
        self.ts2Cuts = list(xrange(0,5))   # List of selections on SOI-1 to make
        self.depths = list(xrange(0,7))    # List of all possible depths (not all for any given ieta!)
        self.iWeights = list(xrange(1,3))  # List of i weights 

        self.HBHEieta = list(xrange(1,29))
        self.HBieta   = list(xrange(1,17))
        self.HE1ieta  = list(xrange(17,21))
        self.HE2ieta  = list(xrange(21,29))

        self.weightHistos = {}             # Map ieta,depth,iWeight to 1D histo of said weight 
        self.averagePulseWeights = {}      # Map of depth,ieta,iWeight to weight from average pulses 
        self.corrHistos = {}               # Map of depth,ieta to w1 vs w2
        self.fitWeights = {}               # Maps depth,ieta,iWeight to a weight extracted from fit of distribution
        self.averagePulseStatErrors = {}   # Maps depth,ieta,TS2 Cut,iWeight to a stat error for the average pulse-derived weight
        self.averagePulseSystErrors = {}   # Maps depth,ieta,iWeight to a syst error for the average pulse-derived weight
        self.statErrors = {}               # Maps depth,ieta,iWeight to a statistical error on the weight 
        self.systErrors = {}               # Maps depth,ieta,iWeight to a systematic error on the weight 
        self.pulseShapesPU = {}            # Average pulse shapes for PU mapped by ieta,depth
        self.ietaDensity = {}              # Number of matched pulses mapped by ieta,depth

        # Initialize map of histos if not loading from cache file
        if not gFromCache:
            self.tfilepu = ROOT.TFile.Open(inputFilePU, "r")
            self.ttreepu = self.tfilepu.Get("compareReemulRecoSeverity9/events")
            self.nevents = self.ttreepu.GetEntriesFast()

            for depth in self.depths:
                for ts2Cut in self.ts2Cuts:
                    self.ietaDensity.setdefault(depth, {}).setdefault(ts2Cut, ROOT.TH1F("depth%d_nTPs_TS2gt%d"%(depth,ts2Cut), "depth%d_nTPs_TS2gt%d"%(depth,ts2Cut), 28, 0.5, 28.5))

                for ieta in self.HBHEieta:
                    iname = "ieta%d_depth%d"%(ieta,depth)
                    for ts2Cut in self.ts2Cuts:
                        tname = iname+"_wcorr_TS2gt%d"%(ts2Cut)
                        self.corrHistos.setdefault(depth, {}).setdefault(ieta, {}).setdefault(ts2Cut, ROOT.TH2F(tname, tname, 360, -50.0, 50.0, 360, -50.0, 50.0))

                    for weight in self.iWeights:
                        wname = iname+"_w%d"%(weight)
                        for ts2Cut in self.ts2Cuts:
                            tname = wname+"_TS2gt%d"%(ts2Cut)
                            self.weightHistos.setdefault(depth, {}).setdefault(ieta, {}).setdefault(weight, {}).setdefault(ts2Cut, ROOT.TH1F(tname, tname, 720, -50.0, 50.0))

                    for ts2Cut in self.ts2Cuts:
                        tname1 = iname+"_pulsePU_TS2gt%d"%(ts2Cut)
                        self.pulseShapesPU.setdefault(depth, {}).setdefault(ieta, {}).setdefault(ts2Cut, ROOT.TH2F(tname1, tname1, 8, -3.5, 4.5, 2049, -0.5, 2048.5))

    def eventLoop(self, eventRange): 

        if eventRange[0] == -1 or len(eventRange) == 2: return

        self.ttreepu.SetBranchStatus("*", 0);    
        self.ttreepu.SetBranchStatus("ieta", 1); 
        self.ttreepu.SetBranchStatus("iphi", 1); 
        self.ttreepu.SetBranchStatus("event", 1);
        self.ttreepu.SetBranchStatus("depth", 1);

        for iTS in xrange(0,8):
            self.ttreepu.SetBranchStatus("ts%d"%(iTS), 1)

        print "Constructing per-ieta, per-event 8TS pulses"
        for iEvent in eventRange:

            self.ttreepu.GetEntry(iEvent)

            self.event = self.ttreepu.event

            # Due to ordering of TPs in depth, ieta, iphi we can be smart about breaking out of the inner loop as soon as possible
            # Use the hotStart to move the starting line for the inner loop as we go along
            hotStart = 0
            for iTP in xrange(0, len(self.ttreepu.ieta)):
                ieta = self.ttreepu.ieta[iTP]
                iphi = self.ttreepu.iphi[iTP]
                idepth = self.ttreepu.depth[iTP]

                # Due to ordering once we hit HF ieta stop looping!
                if abs(ieta) > 28: break 

                # Always kill all-0 8TS
                if self.ttreepu.ts0[iTP] + self.ttreepu.ts1[iTP] + self.ttreepu.ts2[iTP]\
                 + self.ttreepu.ts3[iTP] + self.ttreepu.ts4[iTP] + self.ttreepu.ts5[iTP]\
                 + self.ttreepu.ts6[iTP] + self.ttreepu.ts7[iTP] < 1: continue

                print "category   PU | event %s | ieta %d | iphi %d | depth %d | 8TS [%d, %d, %d, %d, %d, %d, %d, %d]"%(self.ttreepu.event, ieta, iphi, idepth, self.ttreepu.ts0[iTP], self.ttreepu.ts1[iTP],self.ttreepu.ts2[iTP],self.ttreepu.ts3[iTP],self.ttreepu.ts4[iTP],self.ttreepu.ts5[iTP],self.ttreepu.ts6[iTP],self.ttreepu.ts7[iTP])

                puPulse    = numpy.zeros((8,1))
                nopuPulse  = numpy.zeros((8,1))
                puPulse[0] = self.ttreepu.ts0[iTP]
                puPulse[1] = self.ttreepu.ts1[iTP]
                puPulse[2] = self.ttreepu.ts2[iTP]
                puPulse[3] = self.ttreepu.ts3[iTP]
                puPulse[4] = self.ttreepu.ts4[iTP]
                puPulse[5] = self.ttreepu.ts5[iTP]
                puPulse[6] = self.ttreepu.ts6[iTP]
                puPulse[7] = self.ttreepu.ts7[iTP]

                for ts2Cut in self.ts2Cuts:
                    if self.ttreepu.ts2[iTP] > ts2Cut:
                        self.pulseShapesPU[idepth][abs(ieta)][ts2Cut].Fill(-3, self.ttreepu.ts0[iTP])
                        self.pulseShapesPU[idepth][abs(ieta)][ts2Cut].Fill(-2, self.ttreepu.ts1[iTP])
                        self.pulseShapesPU[idepth][abs(ieta)][ts2Cut].Fill(-1, self.ttreepu.ts2[iTP])
                        self.pulseShapesPU[idepth][abs(ieta)][ts2Cut].Fill( 0, self.ttreepu.ts3[iTP])
                        self.pulseShapesPU[idepth][abs(ieta)][ts2Cut].Fill( 1, self.ttreepu.ts4[iTP])
                        self.pulseShapesPU[idepth][abs(ieta)][ts2Cut].Fill( 2, self.ttreepu.ts5[iTP])
                        self.pulseShapesPU[idepth][abs(ieta)][ts2Cut].Fill( 3, self.ttreepu.ts6[iTP])
                        self.pulseShapesPU[idepth][abs(ieta)][ts2Cut].Fill( 4, self.ttreepu.ts7[iTP])
                        self.ietaDensity[idepth][ts2Cut].Fill(abs(ieta))

                        weights = self.extractWeights(puPulse, nopuPulse)

                        #print weights

                        for ts in xrange(0, weights.size): self.weightHistos[idepth][abs(ieta)][ts+1][ts2Cut].Fill(weights[ts])
                        self.corrHistos[idepth][abs(ieta)][ts2Cut].Fill(weights[0], weights[1])

            print "Processed event %d => %d..."%(iEvent,eventRange[-1])
        
        # At the very end of the event loop, write the histograms to the cache file
        self.writeHistograms(eventRange)

    # Method for writing the histograms filled during eventLoop to the cache root file
    def writeHistograms(self, eventRange):
        outfile = ROOT.TFile.Open("histoCache_%d.root"%(eventRange[0]), "RECREATE"); outfile.cd()

        # After looping over all events, write out all the histograms to the cache file
        for depth in xrange(0,7):
            for ieta in self.HBHEieta:
                for ts2Cut in self.ts2Cuts:
                    self.pulseShapesPU[depth][ieta][ts2Cut].Write(self.pulseShapesPU[depth][ieta][ts2Cut].GetName())
                    self.corrHistos[depth][ieta][ts2Cut].Write(self.corrHistos[depth][ieta][ts2Cut].GetName())

                    for iWeight in self.iWeights:
                        self.weightHistos[depth][ieta][iWeight][ts2Cut].Write(self.weightHistos[depth][ieta][iWeight][ts2Cut].GetName())

        for depth, ts2Dict in self.ietaDensity.iteritems():
            for ts2Cut, histo in ts2Dict.iteritems():
                histo.Write(histo.GetName())

        outfile.Close()
    
    # Method for loading in the histograms from the cache file
    def loadHistograms(self):
        
        cacheFilePath = self.cacheLoc + "/histoCache.root"
        if gFromCache and os.path.isfile(cacheFilePath):

            print "Reloading histograms from cache location \"%s\""%(cacheFilePath)
            f = ROOT.TFile.Open(cacheFilePath)

            # Make a dictionary of TTrees from the file to be split
            for key in f.GetListOfKeys():
                obj = key.ReadObj(); obj.SetDirectory(0)
                keyName = str(key.GetName()); chunks = keyName.split("_")

                if "wcorr" in keyName:
                    ieta = int(chunks[0].split("ieta")[1]); depth = int(chunks[1].split("depth")[1]); ts2Cut = int(chunks[-1].split("TS2gt")[1])
                    self.corrHistos.setdefault(depth, {}).setdefault(ieta, {}).setdefault(ts2Cut, obj)

                elif "w" in keyName:
                    ieta = int(chunks[0].split("ieta")[1]); depth = int(chunks[1].split("depth")[1]); ts2Cut = int(chunks[-1].split("TS2gt")[1]); weight = int(chunks[-2].split("w")[1])
                    self.weightHistos.setdefault(depth, {}).setdefault(ieta, {}).setdefault(weight, {}).setdefault(ts2Cut, obj)

                elif "nTPs" in keyName:
                    depth = int(chunks[0].split("depth")[1]); ts2Cut = int(chunks[-1].split("TS2gt")[1])
                    self.ietaDensity.setdefault(depth, {}).setdefault(ts2Cut, obj)

                elif "pulsePU" in keyName:
                    ieta = int(chunks[0].split("ieta")[1]); depth = int(chunks[1].split("depth")[1]); ts2Cut = int(chunks[-1].split("TS2gt")[1])
                    self.pulseShapesPU.setdefault(depth, {}).setdefault(ieta, {}).setdefault(ts2Cut, obj)

            f.Close()

    # Method for extracting weights based on the average pulse shape in each ieta ring, depth
    def extractAveragePulseWeights(self):

        for depth in self.depths:
            for ieta in self.HBHEieta:
                for ts2Cut in self.ts2Cuts:

                    puPulse   = numpy.zeros((8,1)); puPulseErrors   = numpy.zeros((8,1))
                    nopuPulse = numpy.zeros((8,1)); nopuPulseErrors = numpy.zeros((8,1))

                    avePUpulse   = self.pulseShapesPU[depth][ieta][ts2Cut].ProfileX("i%d_d%d_TSgt%d_PU_prof"%(ieta,depth,ts2Cut), 1, -1)

                    for ts in xrange(avePUpulse.GetNbinsX()):
                        puPulse[ts]       = avePUpulse.GetBinContent(ts+1)
                        puPulseErrors[ts] = avePUpulse.GetBinError(ts+1)

                    weights = self.extractWeights(puPulse, nopuPulse)
                    for ts in xrange(0, weights.size): self.averagePulseWeights.setdefault(depth, {}).setdefault(ieta, {}).setdefault(ts+1, {}).setdefault(ts2Cut, weights[ts])

                    weightErrors = self.getAveragePulseStatError(puPulse, nopuPulse, puPulseErrors, nopuPulseErrors)
                    self.averagePulseStatErrors.setdefault(depth, {}).setdefault(ieta, {}).setdefault(1, {}).setdefault(ts2Cut, weightErrors[0])
                    self.averagePulseStatErrors.setdefault(depth, {}).setdefault(ieta, {}).setdefault(2, {}).setdefault(ts2Cut, weightErrors[1])

                for iWeight in self.iWeights:

                    # Use different selections on SOI-1 to derive systematic for average pulse weights
                    averagePulseWeights = [] 
                    for ts2Cut in self.ts2Cuts:
                        if self.averagePulseWeights[depth][ieta][iWeight][ts2Cut] != -999:
                            averagePulseWeights.append(self.averagePulseWeights[depth][ieta][iWeight][ts2Cut])
                    
                    for ts2Cut in self.ts2Cuts:
                        if averagePulseWeights == []: self.averagePulseSystErrors.setdefault(depth, {}).setdefault(ieta, {}).setdefault(iWeight, {}).setdefault(ts2Cut, -999)
                        else: self.averagePulseSystErrors.setdefault(depth, {}).setdefault(ieta, {}).setdefault(iWeight, {}).setdefault(ts2Cut, numpy.std(averagePulseWeights))

    def extractWeights(self, puPulse, nopuPulse):

        # Don't try to extract weights with an empty pulse
        if numpy.count_nonzero(puPulse) == 0: 

            weights = numpy.zeros((2,1))
            weights[0] = -999.0; weights[1] = -999.0

            return weights

        ifPrint = (1 == 1)

        toPrint = ""
        if ifPrint:
            toPrint += "\n\n"
            toPrint += "event: " + str(self.event) + "\n"
            toPrint += "puPulse: " + str(puPulse) + "\n"
            toPrint += "nopuPulse: " + str(nopuPulse) + "\n"

        # Each row will be a 4TS window
        # = [SOI-2, SOI-1, SOI,   SOI+1
        #    SOI-1, SOI,   SOI+1, SOI+2
        #    SOI,   SOI+1, SOI+2, SOI+3
        #    SOI+1, SOI+2, SOI+3, SOI+4]
        puTSMatrix = numpy.zeros((4,4))

        # Vector of 4TS sums for 0PU
        nopuTSMatrix = numpy.zeros((4,4))

        # Fill out the samples matrix and vector of sums
        for ts in xrange(0, puPulse.size):
            for tpts in xrange(0,4):

                idx = ts+self.SOI+tpts-self.offset
                if ts > 3: break 
                if idx >= puPulse.size: break 

                puTSMatrix[ts][tpts] = puPulse[idx]
                nopuTSMatrix[ts][tpts] = nopuPulse[idx]

        soiMask = numpy.zeros((4,1))
        if   self.tpSamples == 2: soiMask[2:4] = numpy.ones((2,1))
        elif self.tpSamples == 1: soiMask[2] = 1

        puSums = numpy.matmul(puTSMatrix,soiMask)
        nopuSums = numpy.matmul(nopuTSMatrix,soiMask)
        puContrib = numpy.subtract(nopuSums, puSums)

        W = numpy.array([-999.0,-999.0])
        coeffs = 0; sums = 0
        if self.tpPresamples == 1:
            coeffs = puTSMatrix[1][1]
            sums = puContrib[1]
        elif self.tpPresamples == 2:
            coeffs = puTSMatrix[0:2,0:2]
            sums = puContrib[0:2]

        # Thus, sums = coeffs x W ===> W = coeffs^-1 x sums
        if self.tpPresamples == 1:
            try: W[1] = float(sums) / float(coeffs)
            except: return W
        elif self.tpPresamples == 2:
            try: W = numpy.matmul(numpy.linalg.inv(coeffs), sums)
            except: return W

        if ifPrint: toPrint += "weights: " + str(W) + "\n"

        #print "W: " + str(W)
        if ifPrint: print toPrint

        return W

    # Method for propagating errors in average pulses to average pulse-derived weight(s)
    def getAveragePulseStatError(self, puPulse, nopuPulse, puPulseErrors, nopuPulseErrors):

        weightErrors = numpy.zeros((2,1))
        if numpy.count_nonzero(nopuPulse) == 0 or numpy.count_nonzero(puPulse) == 0: 

            weightErrors = numpy.zeros((2,1))
            weightErrors[0] = -999; weightErrors[1] = -999

        else: 

            w2Error = math.sqrt(nopuPulseErrors[3]**2 + nopuPulseErrors[4]**2 + puPulseErrors[3]**2 + puPulseErrors[4]**2) / puPulse[2]
            weightErrors[0] = -999
            weightErrors[1] = w2Error

        return weightErrors

    # Method for drawing average pulse for given pileup scenario
    def drawPulseShapes(self, category):

        name = "pulse" + category; histo = 0
        for depth in self.depths:
            for ieta in self.HBHEieta:
                for ts2Cut in self.ts2Cuts:
                
                    if   category == "PU":   histo = self.pulseShapesPU[depth][ieta][ts2Cut]
                    else: continue

                    # No need to print out empty plot (for ieta, depth that does not exist...)
                    if histo.GetEntries() == 0: continue

                    cname = "c_i%d_d%d_TS2gt%d_%s"%(ieta,depth,ts2Cut,category)
                    canvas = ROOT.TCanvas(cname, cname, 2400, 2400); canvas.cd()
                    ROOT.gPad.SetRightMargin(0.13)
                    ROOT.gPad.SetLeftMargin(0.12)

                    averagePulse = histo.ProfileX("prof_i%d_d%d_TSgt%d_%s"%(ieta,depth,ts2Cut,category),1,-1) 

                    histo.SetContour(255)
                    theTitle = "|i#eta| = %d"%(ieta)
                    if depth != 0: theTitle += ", Depth = %d"%(depth)
                    histo.SetTitle(theTitle)
                    histo.GetYaxis().SetTitle("Linearized ADC")
                    histo.GetXaxis().SetTitle("TS")
                    histo.GetYaxis().SetRangeUser(0,35)

                    histo.GetYaxis().SetLabelSize(0.045); histo.GetYaxis().SetTitleSize(0.051); histo.GetYaxis().SetTitleOffset(1.05)
                    histo.GetXaxis().SetLabelSize(0.045); histo.GetXaxis().SetTitleSize(0.051); histo.GetXaxis().SetTitleOffset(0.95)
                    histo.GetZaxis().SetLabelSize(0.045); 

                    histo.Draw("COLZ")

                    averagePulse.SetLineWidth(5)
                    averagePulse.SetMarkerSize(3)
                    averagePulse.SetMarkerStyle(20)
                    averagePulse.SetMarkerColor(ROOT.kBlack)
                    averagePulse.SetLineColor(ROOT.kBlack)
                    averagePulse.Draw("SAME")
    
                    canvas.SetLogz()

                    if ts2Cut == 0:
                        outPath = "%s/PulseShapes/ieta%d/depth%d/TS2gt%d/%s"%(self.outPath,ieta,depth,ts2Cut,category)
                        if not os.path.exists(outPath): os.makedirs(outPath)
                        canvas.SaveAs(outPath + "/AveragePulse.pdf")

    # Method for drawing histogram of correlation between wSOI-1 and wSOI-2
    def drawWeightCorrs(self):

        for depth in self.depths:
            for ieta in self.HBHEieta:

                histo = self.corrHistos[depth][ieta][self.ts2Cut]

                # No need to print out empty plot (for ieta, depth that don't exist...)
                if histo.Integral() == 0: continue

                cname = "c_i%d_d%d_wcorr"%(ieta,depth)
                canvas = ROOT.TCanvas(cname, cname, 2400, 2400); canvas.cd()
                ROOT.gPad.SetLeftMargin(0.12)
                ROOT.gPad.SetRightMargin(0.13)

                histo.SetContour(255)
                histo.RebinX(3); histo.RebinY(3)
                theTitle = "|i#eta| = %d"%(ieta)
                if depth != 0: theTitle += ", Depth = %d"%(depth)
                histo.SetTitle(theTitle)
                histo.GetYaxis().SetTitle("w_{SOI-1}")
                histo.GetYaxis().SetRangeUser(-20,20)
                histo.GetXaxis().SetTitle("w_{SOI-2}")
                histo.GetXaxis().SetRangeUser(-20,20)

                histo.GetYaxis().SetLabelSize(0.039); histo.GetYaxis().SetTitleSize(0.051); histo.GetYaxis().SetTitleOffset(1.18)
                histo.GetXaxis().SetTitleSize(0.051); histo.GetXaxis().SetTitleOffset(0.9)
                histo.GetXaxis().SetLabelSize(0.039)
                histo.Draw("COLZ")

                canvas.SetLogz(); canvas.SetGridx(); canvas.SetGridy()

                outPath = "%s/Fits/ieta%d/depth%d"%(self.outPath,ieta,depth)
                if not os.path.exists(outPath): os.makedirs(outPath)
                canvas.SaveAs(outPath + "/WeightCorrelation.pdf")

    # Method for drawing histogram of an extracted weight with its fit
    def drawWeightHisto(self, ieta, depth, iWeight, rebin, ts2Cut, weight, statError, systError, weightHisto, histoFit):

        canvas = ROOT.TCanvas("c_i%d_d%d_w%d_r%d_TS2gt%d"%(ieta,depth,iWeight,rebin,ts2Cut), "c_i%d_d%d_w%d_r%d_TS2gt%d"%(ieta,depth,iWeight,rebin,ts2Cut), 2400, 2400); canvas.cd()
        canvas.SetGridx()
        canvas.SetGridy()
        ROOT.gPad.SetRightMargin(0.03)
        ROOT.gPad.SetLeftMargin(0.15)

        weightHisto.GetXaxis().SetRangeUser(-9,3)
        theTitle = "|i#eta| = %d"%(ieta)
        if depth != 0: theTitle += ", Depth = %d"%(depth)
        weightHisto.SetTitle(theTitle)
        weightHisto.GetXaxis().SetTitle("w_{SOI-%d}"%(3-iWeight))
        weightHisto.GetYaxis().SetTitle("A.U.")
        weightHisto.GetYaxis().SetLabelSize(0.048); weightHisto.GetYaxis().SetTitleSize(0.054); weightHisto.GetYaxis().SetTitleOffset(1.45)
        weightHisto.GetXaxis().SetLabelSize(0.048); weightHisto.GetXaxis().SetTitleSize(0.054); weightHisto.GetXaxis().SetTitleOffset(0.9)

        weightHisto.SetLineWidth(3)
        weightHisto.SetLineColor(ROOT.kBlack)

        histoFit.SetLineColor(ROOT.kRed)
        histoFit.SetLineWidth(5)
        histoFit.SetLineStyle(7)

        someText = ROOT.TPaveText(0.2, 0.65, 0.6, 0.85, "trNDC")

        someText.AddText("Peak = %3.2f #pm  %3.2f (stat.) #pm  %3.2f (syst.)"%(weight,statError,systError))
        someText.AddText("#chi^{2} / DOF = %3.2f / %d"%(histoFit.GetChisquare(), histoFit.GetNDF()))
        someText.AddText("Entries = %d"%(weightHisto.GetEntries()))
        someText.SetTextAlign(31)
        someText.SetFillColor(ROOT.kWhite);

        weightHisto.Draw("HIST")
        histoFit.Draw("SAME")
        someText.Draw("SAME")
    
        if rebin <= self.rebin and ts2Cut == self.ts2Cut: 
            outPath = "%s/Fits/ieta%d/depth%d/SOI-%d/TS2gt%d"%(self.outPath,ieta,depth,3-iWeight,ts2Cut)
            if not os.path.exists(outPath): os.makedirs(outPath)
            canvas.SaveAs(outPath + "/WeightDistribution_rebin%d.pdf"%(rebin))

    # Method for getting weights from fit of weight distribution
    def extractFitWeights(self, save=False):

        for iWeight in self.iWeights:
            for depth in self.depths:
                for ieta in self.HBHEieta:
                    for ts2Cut in self.ts2Cuts:

                        histo = self.weightHistos[depth][ieta][iWeight][ts2Cut]
                        if histo.Integral() == 0:
                            self.fitWeights.setdefault(depth, {}).setdefault(ieta, {}).setdefault(iWeight, {}).setdefault(ts2Cut, -999)
                            self.statErrors.setdefault(depth, {}).setdefault(ieta, {}).setdefault(iWeight, {}).setdefault(ts2Cut, -999)
                            self.systErrors.setdefault(depth, {}).setdefault(ieta, {}).setdefault(iWeight, {}).setdefault(ts2Cut, -999)
                            continue 

                        numEntries = float(histo.GetEntries())
                        histo.Scale(1./histo.Integral())

                        # Keys of these dictionaries correspond to rebinnings
                        rebinHistos     = {1 : 0, 2 : 0, 3 : 0, 4 : 0}
                        rebinFits       = {1 : 0, 2 : 0, 3 : 0, 4 : 0}
                        rebinWeights    = numpy.zeros((5,1))
                        rebinStatErrors = numpy.zeros((5,1)) 
                        for rebin in rebinHistos.keys(): rebinHistos[rebin] = histo.Rebin(rebin, "r%d_i%d_d%d_w%d_TS2gt%d"%(rebin,ieta,depth,iWeight,ts2Cut))

                        for rebin, rHisto in rebinHistos.iteritems():

                            binmax = rHisto.GetMaximumBin(); xmax = rHisto.GetBinCenter(binmax); binWidth = rHisto.GetBinWidth(1)

                            if ieta <= 28 or self.tpSamples == 1:

                                name = "f_i%d_d%d_r%d_w%d_TS2gt%d"%(ieta,depth,rebin,iWeight,ts2Cut); funcString = "[0]*TMath::Landau(-x, [1], [2])*TMath::CauchyDist(-x, [3], [4])"; theFunc = 0; fitWidth = 2.0*binWidth; fitRange = [xmax-fitWidth,xmax+fitWidth]
                                #theFunc = ROOT.TF1(name, funcString, fitRange[0], fitRange[1])
                                theFunc = ROOT.TF1(name, funcString, -5, 1.0)

                                theFunc.SetParameters(0.2, 0, 2.5, 0, 2.5)
                                theFunc.SetParNames("A", "position", "scale", "mu", "sigma")
                                theFunc.SetParLimits(0, 0.0, 25.0)
                                theFunc.SetParLimits(1, 0.0, 25.0)
                                theFunc.SetParLimits(2, 0.0, 25.0)
                                theFunc.SetParLimits(3, 0.0, 25.0)
                                theFunc.SetParLimits(4, 0.0, 25.0)

                            #elif ieta > 20:

                            #    name = "f_i%d_d%d_r%d_w%d_TS2gt%d"%(ieta,depth,rebin,iWeight,ts2Cut); funcString = "[0]*TMath::Gaus(-x, [1], [2])*TMath::Landau(-x, [3], [4])"; theFunc = 0; fitWidth = 2.0*binWidth; fitRange = [xmax-fitWidth,xmax+fitWidth]
                            #    #theFunc = ROOT.TF1(name, funcString, fitRange[0], fitRange[1])
                            #    theFunc = ROOT.TF1(name, funcString, -5, 1.0)

                            #    theFunc.SetParameters(0.2, 0, 2.5, 2.5, 2.5)
                            #    theFunc.SetParNames("A", "mu", "sigma", "lmu", "lsigma")
                            #    theFunc.SetParLimits(0, 0.0, 25.0)
                            #    theFunc.SetParLimits(1, 0.0, 25.0)
                            #    theFunc.SetParLimits(2, 0.0, 5.0)
                            #    theFunc.SetParLimits(3, 0.0, 25.0)
                            #    theFunc.SetParLimits(3, 0.0, 25.0)

                            rHisto.Fit(name, "QMRWL") # https://root.cern.ch/doc/master/classTH1.html#a63eb028df86bc86c8e20c989eb23fb2a
                            theFunc.SetNpx(1000)

                            rebinWeights[rebin] = theFunc.GetMaximumX(-5.0,5.0)
                            meanError = theFunc.GetParameter("sigma")

                            rebinFits[rebin] = theFunc
                            rebinStatErrors[rebin] = meanError / math.sqrt(numEntries) 

                            if rebin != self.rebin: self.drawWeightHisto(ieta, depth, iWeight, rebin, ts2Cut, rebinWeights[rebin], rebinStatErrors[rebin], -1.0, rebinHistos[rebin], rebinFits[rebin])
                            
                        theWeight = rebinWeights[self.rebin]; theStatError = rebinStatErrors[self.rebin]

                        # From the five different fits the histogram determine the standard dev of the weights 
                        theSystError = abs(numpy.amax(rebinWeights[1:])-numpy.amin(rebinWeights[1:]))
                        self.fitWeights.setdefault(depth, {}).setdefault(ieta, {}).setdefault(iWeight, {}).setdefault(ts2Cut, theWeight)
                        self.statErrors.setdefault(depth, {}).setdefault(ieta, {}).setdefault(iWeight, {}).setdefault(ts2Cut, theStatError)
                        self.systErrors.setdefault(depth, {}).setdefault(ieta, {}).setdefault(iWeight, {}).setdefault(ts2Cut, theSystError)

                        if save: self.drawWeightHisto(ieta, depth, iWeight, self.rebin, ts2Cut, theWeight, theStatError, theSystError, rebinHistos[self.rebin], rebinFits[self.rebin])

    # Method for calculating the averaged-over-depth weight for each ieta and average-over-depth for HB, HE1, HE2
    def getDepthAverageWeightsAndErrors(self, weightDict, statErrorDict, systErrorDict):

        # Intialize some temporary dictionaries
        depthAverageWeights = {}; depthAverageStatErrors = {}; depthAverageSystErrors = {}
        ietaDensityDepthSum = {}
        for ieta in self.HBHEieta:
            ietaDensityDepthSum[ieta] = 0 
            for iWeight in self.iWeights:
                depthAverageWeights.setdefault(ieta, {}).setdefault(iWeight, -999)
                depthAverageStatErrors.setdefault(ieta, {}).setdefault(iWeight, 0.0)
                depthAverageSystErrors.setdefault(ieta, {}).setdefault(iWeight, 0.0)

        subDetDepthAverageWeights = {"HB" : {}, "HE1" : {}, "HE2" : {}}; subDetDepthAverageStatErrors = {"HB" : {}, "HE1" : {}, "HE2" : {}}; subDetDepthAverageSystErrors = {"HB" : {}, "HE1" : {}, "HE2" : {}}
        subDetDensity = {"HB" : 0, "HE1" : 0, "HE2" : 0}
        for det, wDict in subDetDepthAverageWeights.iteritems():
            for iWeight in self.iWeights:
                subDetDepthAverageWeights[det][iWeight]    = -999 
                subDetDepthAverageStatErrors[det][iWeight] = 0.0 
                subDetDepthAverageSystErrors[det][iWeight] = 0.0 

        # Sum over the depths of each ieta to calculate the total TPs in that ieta
        for depth in self.depths:
            for ieta in self.HBHEieta:

                ietaDensityDepthSum[ieta] += self.ietaDensity[depth][self.ts2Cut].GetBinContent(ieta)
                if   ieta in self.HBieta:  subDetDensity["HB"]  += self.ietaDensity[depth][self.ts2Cut].GetBinContent(ieta) 
                elif ieta in self.HE1ieta: subDetDensity["HE1"] += self.ietaDensity[depth][self.ts2Cut].GetBinContent(ieta) 
                elif ieta in self.HE2ieta: subDetDensity["HE2"] += self.ietaDensity[depth][self.ts2Cut].GetBinContent(ieta) 

        # Now compute summed-over-depth average weight for each ieta
        for depth in self.depths:
            for ieta in self.HBHEieta:
                depthTPs = self.ietaDensity[depth][self.ts2Cut].GetBinContent(ieta)

                # Empty ietaDensity means we aren't looking at this depth...
                if depthTPs == 0: continue

                for iWeight in weightDict[depth][ieta].keys():

                    # Not very clean way of getting weight from extra dictionary or not
                    weight    = weightDict[depth][ieta][iWeight][self.ts2Cut]
                    statError = statErrorDict[depth][ieta][iWeight][self.ts2Cut]
                    systError = systErrorDict[depth][ieta][iWeight][self.ts2Cut]

                    if weight == -999: continue
                    
                    if depthAverageWeights[ieta][iWeight]        == -999: depthAverageWeights[ieta][iWeight] += 999
                    if subDetDepthAverageWeights["HB"][iWeight]  == -999: subDetDepthAverageWeights["HB"][iWeight] += 999
                    if subDetDepthAverageWeights["HE1"][iWeight] == -999: subDetDepthAverageWeights["HE1"][iWeight] += 999
                    if subDetDepthAverageWeights["HE2"][iWeight] == -999: subDetDepthAverageWeights["HE2"][iWeight] += 999

                    depthAverageWeights[ieta][iWeight] += weight * depthTPs / float(ietaDensityDepthSum[ieta])
                    if   ieta in self.HBieta:  subDetDepthAverageWeights["HB"][iWeight]  += weight * depthTPs / float(subDetDensity["HB"])
                    elif ieta in self.HE1ieta: subDetDepthAverageWeights["HE1"][iWeight] += weight * depthTPs / float(subDetDensity["HE1"]) 
                    elif ieta in self.HE2ieta: subDetDepthAverageWeights["HE2"][iWeight] += weight * depthTPs / float(subDetDensity["HE2"]) 

                    depthAverageStatErrors[ieta][iWeight] += statError * depthTPs / float(ietaDensityDepthSum[ieta])
                    if   ieta in self.HBieta:  subDetDepthAverageStatErrors["HB"][iWeight]  += statError * depthTPs / float(subDetDensity["HB"])
                    elif ieta in self.HE1ieta: subDetDepthAverageStatErrors["HE1"][iWeight] += statError * depthTPs / float(subDetDensity["HE1"]) 
                    elif ieta in self.HE2ieta: subDetDepthAverageStatErrors["HE2"][iWeight] += statError * depthTPs / float(subDetDensity["HE2"]) 

                    depthAverageSystErrors[ieta][iWeight] += systError * depthTPs / float(ietaDensityDepthSum[ieta])
                    if   ieta in self.HBieta:  subDetDepthAverageSystErrors["HB"][iWeight]  += systError * depthTPs / float(subDetDensity["HB"])
                    elif ieta in self.HE1ieta: subDetDepthAverageSystErrors["HE1"][iWeight] += systError * depthTPs / float(subDetDensity["HE1"]) 
                    elif ieta in self.HE2ieta: subDetDepthAverageSystErrors["HE2"][iWeight] += systError * depthTPs / float(subDetDensity["HE2"]) 

        return depthAverageWeights, subDetDepthAverageWeights, depthAverageStatErrors, depthAverageSystErrors, subDetDepthAverageStatErrors, subDetDepthAverageSystErrors

    # Method for writing out a text file summarizing all the extracted weights
    def getWeightSummary(self):

        aveSummary = open("%s/aveWeightSummary.txt"%(self.outPath), "w")
        summary = open("%s/weightSummary.txt"%(self.outPath), "w")

        depthAverageWeights, subdetDepthAverageWeights, depthAverageStatErrors, \
        depthAverageSystErrors, subdetDepthAverageStatErrors, subdetDepthAverageSystErrors = self.getDepthAverageWeightsAndErrors(self.fitWeights, self.statErrors, self.systErrors)

        averagePulseDepthAverageWeights, averagePulseSubdetDepthAverageWeights, averagePulseDepthAverageStatErrors, \
        averagePulseDepthAverageSystErrors, averagePulseSubdetDepthAverageStatErrors, averagePulseSubdetDepthAverageSystErrors \
        = self.getDepthAverageWeightsAndErrors(self.averagePulseWeights, self.averagePulseStatErrors, self.averagePulseSystErrors)

        emptyStr = "              -               & "
        for iWeight in self.iWeights:
            str2Write = "\nwSOI-%d:\n"%(3-iWeight); str2WriteAve = str2Write

            for ieta in self.HBHEieta:
                ietaStr = "%d"%(ieta)
                ietaStr = ietaStr.rjust(2)

                str2Write += "ieta: %s   "%(ietaStr); str2WriteAve += "ieta: %s   "%(ietaStr)
                
                if averagePulseDepthAverageWeights[ieta][iWeight] == -999:
                     str2WriteAve += emptyStr
                else:
                    statError = averagePulseDepthAverageStatErrors[ieta][iWeight]
                    systError = averagePulseDepthAverageSystErrors[ieta][iWeight]
                    weightStr = "%3.2f"%(averagePulseDepthAverageWeights[ieta][iWeight]); weightStr = weightStr.rjust(5)
                    str2WriteAve += "$%s_{\pm %3.2f}^{\pm %3.2f}$ & "%(weightStr,statError,systError)

                for depth in self.depths:
                    if self.averagePulseWeights[depth][ieta][iWeight][self.ts2Cut] == -999:
                        str2WriteAve += emptyStr 
                    else:
                        weightStr = "%3.2f"%(self.averagePulseWeights[depth][ieta][iWeight][self.ts2Cut]); weightStr = weightStr.rjust(5)
                        statError = self.averagePulseStatErrors[depth][ieta][iWeight][self.ts2Cut]
                        systError = self.averagePulseSystErrors[depth][ieta][iWeight][self.ts2Cut]
                        str2WriteAve += "$%s_{\pm %3.2f}^{\pm %3.2f}$ & "%(weightStr,statError,systError)
                str2WriteAve += "\n"

                if depthAverageWeights[ieta][iWeight] == -999:
                    str2Write += emptyStr
                else:
                    statError = depthAverageStatErrors[ieta][iWeight]
                    systError = depthAverageSystErrors[ieta][iWeight]
                    weightStr = "%3.2f"%(depthAverageWeights[ieta][iWeight]); weightStr = weightStr.rjust(5)
                    str2Write += "$%s_{\pm %3.2f}^{\pm %3.2f}$ & "%(weightStr,statError,systError)

                for depth in self.depths:
                    if self.fitWeights[depth][ieta][iWeight][self.ts2Cut] == -999: 
                        str2Write += emptyStr 
                    else: 
                        weightStr = "%3.2f"%(self.fitWeights[depth][ieta][iWeight][self.ts2Cut]); weightStr = weightStr.rjust(5)
                        statError = self.statErrors[depth][ieta][iWeight][self.ts2Cut]
                        systError = self.systErrors[depth][ieta][iWeight][self.ts2Cut]
                        str2Write += "$%s_{\pm %3.2f}^{\pm %3.2f}$ & "%(weightStr,statError,systError)
                str2Write += "\n"

            str2Write += "\n"; str2WriteAve += "\n"
            for det, weightDict in subdetDepthAverageWeights.iteritems():
                detStr = "%s"%(det)
                detStr = detStr.rjust(8)
                detStr += "   "
                str2Write += detStr; str2WriteAve += detStr
           
                if weightDict[iWeight] == -999:
                    str2Write += emptyStr
                else:
                    statError = subdetDepthAverageStatErrors[det][iWeight]
                    systError = subdetDepthAverageSystErrors[det][iWeight]
                    weightStr = "%3.2f"%(weightDict[iWeight]); weightStr = weightStr.rjust(5)
                    str2Write += "$%s_{\pm %3.2f}^{\pm %3.2f}$  "%(weightStr,statError,systError)

                if averagePulseSubdetDepthAverageWeights[det][iWeight] == -999:
                     str2WriteAve += emptyStr
                else:
                    statError = averagePulseSubdetDepthAverageStatErrors[det][iWeight]
                    systError = averagePulseSubdetDepthAverageSystErrors[det][iWeight]
                    weightStr = "%3.2f"%(averagePulseSubdetDepthAverageWeights[det][iWeight]); weightStr = weightStr.rjust(5)
                    str2WriteAve += "$%s_{\pm %3.2f}^{\pm %3.2f}$  "%(weightStr,statError,systError)
                str2Write += "\n"; str2WriteAve += "\n"

            aveSummary.write(str2WriteAve)
            summary.write(str2Write)                   
                    
        summary.write("\n\n"); aveSummary.write("\n\n")

        summary.close(); aveSummary.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--tag"       , dest="tag"       , help="Unique tag for output"     , type=str     , default="TAG")
    parser.add_argument("--fromCache" , dest="fromCache" , help="Read from cache file"      , default=False, action="store_true")
    parser.add_argument("--contain"   , dest="contain"   , help="With pulse containment"    , default=False, action="store_true")
    parser.add_argument("--depth"     , dest="depth"     , help="Extract with depth"        , default=False, action="store_true")
    parser.add_argument("--oot"       , dest="oot"       , help="Use OOT sample"            , default=False, action="store_true")
    parser.add_argument("--scheme"    , dest="scheme"    , help="Which pulse filter scheme" , type=str     , default="ALGO")
    parser.add_argument("--evtRange"  , dest="evtRange"  , help="Start and number"          , type=int     , nargs="+", default=[-1,1])
    
    arg = parser.parse_args()

    # Everything will work inside sandbox
    HOME = os.getenv("HOME")
    SANDBOX = HOME + "/nobackup/HCAL_Trigger_Study"
    INPUTLOC = "root://cmseos.fnal.gov//store/user/jhiltbra/HCAL_Trigger_Study/WeightExtraction"

    # Default to use OOT + IT sample: called 50PU.root
    puStr = "50PU"
    if arg.oot: puStr = "OOT"

    containStr = "NoContain"
    if arg.contain: containStr = "Contain"

    depthStr = "NoDepth"
    if arg.depth: depthStr = "Depth"

    gFromCache = arg.fromCache
    eventRange = xrange(arg.evtRange[0], arg.evtRange[0]+arg.evtRange[1]) 

    aPath = ""; outPath = "%s/plots/Weights/%s/%s"%(SANDBOX,arg.scheme,arg.tag)
    
    PUFile   = "%s/NuGun/%s/%s/%s.root"%(INPUTLOC,containStr, depthStr, puStr)

    theExtractor = WeightExtractor(arg.scheme, PUFile, outPath)
    theExtractor.eventLoop(eventRange)

    if gFromCache:
        theExtractor.loadHistograms()
        theExtractor.extractFitWeights(save=True)
        theExtractor.extractAveragePulseWeights()
        theExtractor.getWeightSummary()

        theExtractor.drawPulseShapes("PU")
        theExtractor.drawWeightCorrs()
