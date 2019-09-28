#!/usr/bin/env python

import sys, os, ROOT, numpy, argparse, math
from pu2nopuMap import PU2NOPUMAP 

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetLineWidth(2)
ROOT.gStyle.SetFrameLineWidth(4)
ROOT.gStyle.SetPaintTextFormat("3.2f")
ROOT.gStyle.SetErrorX(0)
ROOT.TH1.SetDefaultSumw2()
ROOT.TH2.SetDefaultSumw2()

class WeightExtractor:

    def __init__(self, scheme, inputFilePU, inputFileNOPU, outputPath):

        self.outPath = outputPath              # Base outpath to write everything to
        self.cacheLoc = "%s/root"%(outputPath) # Location to cache histograms in root file

        # _My_ use of word "sample" is any TS >= SOI
        if scheme == "PFA2p":
            self.tpPresamples = 2          # PFA2p uses two presamples
            self.tpSamples = 2             # SOI and SOI+1 are used to sample non-PU pulse
        elif scheme == "PFA3p":
            self.tpPresamples = 1          # PFA3p uses two SOI and SOI+1 fully and SOI-1 presample
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
        self.scheme = scheme               # Which algo
        self.ts2Cut = 3                    # Requirement on TS2 (SOI-1) > n ADC
        self.rebin = 2                     # Rebin factor for weight histograms
        self.ts2Cuts = list(xrange(0,6))   # List of selections on SOI-1 to make
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
        self.pulseShapesNOPU = {}          # Average pulse shapes for NOPU mapped by ieta,depth
        self.ietaDensity = {}              # Number of matched pulses mapped by ieta,depth

        # Initialize map of histos if not loading from cache file
        if not gFromCache:
            self.tfilepu = ROOT.TFile.Open(inputFilePU, "r"); self.tfilenopu = ROOT.TFile.Open(inputFileNOPU, "r")
            self.ttreepu = self.tfilepu.Get("compareReemulRecoSeverity9/events"); self.ttreenopu = self.tfilenopu.Get("compareReemulRecoSeverity9/events")
            self.nevents = self.ttreepu.GetEntriesFast()

            for depth in self.depths:
                self.ietaDensity[depth] = ROOT.TH1F("d%d_nTPs"%(depth), "d%d_nTPs"%(depth), 28, 0.5, 28.5)
                self.corrHistos[depth] = {}
                self.pulseShapesPU[depth] = {}
                self.pulseShapesNOPU[depth] = {}
                self.weightHistos[depth] = {}
                self.fitWeights[depth] = {}
                self.statErrors[depth] = {}
                self.systErrors[depth] = {}
                self.averagePulseStatErrors[depth] = {}
                self.averagePulseSystErrors[depth] = {}

                for ieta in self.HBHEieta:
                    iname = "i%d_d%d"%(ieta,depth)
                    self.weightHistos[depth][ieta] = {}
                    self.fitWeights[depth][ieta] = {}
                    self.corrHistos[depth][ieta] = ROOT.TH2F(iname+"_wcorr", iname+"_wcorr", 360, -50.0, 50.0, 360, -50.0, 50.0)
                    self.pulseShapesPU[depth][ieta] = {} 
                    self.pulseShapesNOPU[depth][ieta] = {} 

                    for ts2Cut in self.ts2Cuts:
                        tname = iname+"_TS2gt%d"%(ts2Cut)
                        self.pulseShapesPU[depth][ieta][ts2Cut] = ROOT.TH2F(tname+"_pulsePU", tname+"_pulsePU", 8, -3.5, 4.5, 2048, -0.5, 2047.5)
                        self.pulseShapesNOPU[depth][ieta][ts2Cut] = ROOT.TH2F(tname+"_pulseNOPU", tname+"_pulseNOPU", 8, -3.5, 4.5, 2048, -0.5, 2047.5)

                    for weight in self.iWeights:
                        wname = iname+"_w%d"%(weight)
                        self.weightHistos[depth][ieta][weight] = ROOT.TH1F(wname, wname, 720, -50.0, 50.0)

    def eventLoop(self, eventRange): 

        if eventRange[0] == -1 or len(eventRange) == 2: return

        self.ttreepu.SetBranchStatus("*", 0);     self.ttreenopu.SetBranchStatus("*", 0)
        self.ttreepu.SetBranchStatus("ieta", 1);  self.ttreenopu.SetBranchStatus("ieta", 1)
        self.ttreepu.SetBranchStatus("iphi", 1);  self.ttreenopu.SetBranchStatus("iphi", 1)
        self.ttreepu.SetBranchStatus("event", 1); self.ttreenopu.SetBranchStatus("event", 1)
        self.ttreepu.SetBranchStatus("depth", 1); self.ttreenopu.SetBranchStatus("depth", 1)

        for iTS in xrange(0,8):
            self.ttreepu.SetBranchStatus("ts%d"%(iTS), 1)
            self.ttreenopu.SetBranchStatus("ts%d"%(iTS), 1)

        print "Constructing per-ieta, per-event 8TS pulses"
        for iEvent in eventRange:

            nTPsPUmap   = {}; pulseMapPU   = {}
            nTPsNOPUmap = {}; pulseMapNOPU = {}

            for ieta in self.HBHEieta:
                pulseMapPU[ieta]   = numpy.zeros((8,1)); nTPsPUmap[ieta] = 0  
                pulseMapNOPU[ieta] = numpy.zeros((8,1)); nTPsNOPUmap[ieta] = 0

            self.ttreepu.GetEntry(iEvent)
            self.ttreenopu.GetEntry(PU2NOPUMAP[self.ttreepu.event])

            print self.ttreepu.event
            if self.ttreepu.event != self.ttreenopu.event:
                print "EVENT MISMATCH, SKIPPING THIS EVENT ENTRY!"
                continue

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

                for jTP in xrange(hotStart, len(self.ttreenopu.ieta)):
                    jeta = self.ttreenopu.ieta[jTP]
                    jphi = self.ttreenopu.iphi[jTP]
                    jdepth = self.ttreenopu.depth[jTP]
            
                    # Due to ordering once we hit HF ieta stop looping! 
                    if abs(jeta) > 28: break 

                    # Always kill all-0 8TS
                    elif self.ttreenopu.ts0[jTP] + self.ttreenopu.ts1[jTP] + self.ttreenopu.ts2[jTP]\
                       + self.ttreenopu.ts3[jTP] + self.ttreenopu.ts4[jTP] + self.ttreenopu.ts5[jTP]\
                       + self.ttreenopu.ts6[jTP] + self.ttreenopu.ts7[jTP] < 1: continue

                    # If we passed in depth then there was no match; break the inner loop and go back to outer loop
                    elif jdepth > idepth:
                        hotStart = jTP
                        break

                    # For same depth, if we pass in phi there was and will not be a match 
                    elif idepth == jdepth:

                        # If we pass in ieta then there is no match; break the inner loop and go back to outer loop
                        if (jeta - ieta) * jeta > 0:
                            hotStart = jTP
                            break

                        # If eta also match then check at phi level
                        elif jeta == ieta:

                            # If we pass in phi then there was no match; break the inner loop and go back to outer loop
                            if jphi > iphi:
                                hotStart = jTP
                                break

                            # Here we match in depth, ieta and phi
                            elif jphi == iphi:

                                # We are here so we must have found a match!
                                print "category   PU | event %s | ieta %d | iphi %d | depth %d | 8TS [%d, %d, %d, %d, %d, %d, %d, %d]"%(self.ttreepu.event, ieta, iphi, idepth, self.ttreepu.ts0[iTP], self.ttreepu.ts1[iTP],self.ttreepu.ts2[iTP],self.ttreepu.ts3[iTP],self.ttreepu.ts4[iTP],self.ttreepu.ts5[iTP],self.ttreepu.ts6[iTP],self.ttreepu.ts7[iTP])
                                print "category NOPU | event %s | ieta %d | iphi %d | depth %d | 8TS [%d, %d, %d, %d, %d, %d, %d, %d]\n"%(self.ttreenopu.event, jeta, jphi, jdepth, self.ttreenopu.ts0[jTP], self.ttreenopu.ts1[jTP],self.ttreenopu.ts2[jTP],self.ttreenopu.ts3[jTP],self.ttreenopu.ts4[jTP],self.ttreenopu.ts5[jTP],self.ttreenopu.ts6[jTP],self.ttreenopu.ts7[jTP])

                                puPulse    = numpy.zeros((8,1));    nopuPulse    = numpy.zeros((8,1))
                                puPulse[0] = self.ttreepu.ts0[iTP]; nopuPulse[0] = self.ttreenopu.ts0[jTP]
                                puPulse[1] = self.ttreepu.ts1[iTP]; nopuPulse[1] = self.ttreenopu.ts1[jTP]
                                puPulse[2] = self.ttreepu.ts2[iTP]; nopuPulse[2] = self.ttreenopu.ts2[jTP]
                                puPulse[3] = self.ttreepu.ts3[iTP]; nopuPulse[3] = self.ttreenopu.ts3[jTP]
                                puPulse[4] = self.ttreepu.ts4[iTP]; nopuPulse[4] = self.ttreenopu.ts4[jTP]
                                puPulse[5] = self.ttreepu.ts5[iTP]; nopuPulse[5] = self.ttreenopu.ts5[jTP]
                                puPulse[6] = self.ttreepu.ts6[iTP]; nopuPulse[6] = self.ttreenopu.ts6[jTP]
                                puPulse[7] = self.ttreepu.ts7[iTP]; nopuPulse[7] = self.ttreenopu.ts7[jTP]

                                for ts2Cut in self.ts2Cuts:
                                    if self.ttreepu.ts2[iTP] > ts2Cut:
                                        self.pulseShapesPU[idepth][abs(ieta)][ts2Cut].Fill(-3, self.ttreepu.ts0[iTP]); self.pulseShapesNOPU[idepth][abs(ieta)][ts2Cut].Fill(-3, self.ttreenopu.ts0[jTP])
                                        self.pulseShapesPU[idepth][abs(ieta)][ts2Cut].Fill(-2, self.ttreepu.ts1[iTP]); self.pulseShapesNOPU[idepth][abs(ieta)][ts2Cut].Fill(-2, self.ttreenopu.ts1[jTP])
                                        self.pulseShapesPU[idepth][abs(ieta)][ts2Cut].Fill(-1, self.ttreepu.ts2[iTP]); self.pulseShapesNOPU[idepth][abs(ieta)][ts2Cut].Fill(-1, self.ttreenopu.ts2[jTP])
                                        self.pulseShapesPU[idepth][abs(ieta)][ts2Cut].Fill( 0, self.ttreepu.ts3[iTP]); self.pulseShapesNOPU[idepth][abs(ieta)][ts2Cut].Fill( 0, self.ttreenopu.ts3[jTP])
                                        self.pulseShapesPU[idepth][abs(ieta)][ts2Cut].Fill( 1, self.ttreepu.ts4[iTP]); self.pulseShapesNOPU[idepth][abs(ieta)][ts2Cut].Fill( 1, self.ttreenopu.ts4[jTP])
                                        self.pulseShapesPU[idepth][abs(ieta)][ts2Cut].Fill( 2, self.ttreepu.ts5[iTP]); self.pulseShapesNOPU[idepth][abs(ieta)][ts2Cut].Fill( 2, self.ttreenopu.ts5[jTP])
                                        self.pulseShapesPU[idepth][abs(ieta)][ts2Cut].Fill( 3, self.ttreepu.ts6[iTP]); self.pulseShapesNOPU[idepth][abs(ieta)][ts2Cut].Fill( 3, self.ttreenopu.ts6[jTP])
                                        self.pulseShapesPU[idepth][abs(ieta)][ts2Cut].Fill( 4, self.ttreepu.ts7[iTP]); self.pulseShapesNOPU[idepth][abs(ieta)][ts2Cut].Fill( 4, self.ttreenopu.ts7[jTP])

                                if self.ttreepu.ts2[iTP] > self.ts2Cut:
                                    self.ietaDensity[idepth].Fill(abs(ieta))
                                    weights = self.extractWeights(puPulse, nopuPulse)

                                    for ts in xrange(0, weights.size): self.weightHistos[idepth][abs(ieta)][ts+1].Fill(weights[ts])
                                    self.corrHistos[idepth][abs(ieta)].Fill(weights[0], weights[1])

                                hotStart = jTP
                                break

            print "Processed event %d => %d..."%(iEvent,eventRange[-1])
        
        # At the very end of the event loop, write the histograms to the cache file
        self.writeHistograms(eventRange)

    # Method for writing the histograms filled during eventLoop to the cache root file
    def writeHistograms(self, eventRange):
        outfile = ROOT.TFile.Open("histoCache_%d.root"%(eventRange[0]), "RECREATE"); outfile.cd()

        # After looping over all events, write out all the histograms to the cache file
        for depth in xrange(0,7):
            for ieta in self.HBHEieta:
                self.corrHistos[depth][ieta].Write(self.corrHistos[depth][ieta].GetName())
                
                for ts2Cut in self.ts2Cuts:
                    self.pulseShapesNOPU[depth][ieta][ts2Cut].Write(self.pulseShapesNOPU[depth][ieta][ts2Cut].GetName())
                    self.pulseShapesPU[depth][ieta][ts2Cut].Write(self.pulseShapesPU[depth][ieta][ts2Cut].GetName())

                for iWeight in self.iWeights:
                    self.weightHistos[depth][ieta][iWeight].Write(self.weightHistos[depth][ieta][iWeight].GetName())

        for depth, histo in self.ietaDensity.iteritems():
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
                ieta = -99; depth = -99
                if len(chunks) >= 3:

                    ieta = int(chunks[0].split("i")[1]); depth = int(chunks[1].split("d")[1]);

                    if depth not in self.pulseShapesNOPU: self.pulseShapesNOPU[depth] = {ieta : {}}
                    if depth not in self.pulseShapesPU: self.pulseShapesPU[depth] = {ieta : {}}
                    if depth not in self.corrHistos: self.corrHistos[depth] = {}
                    if depth not in self.weightHistos: self.weightHistos[depth] = {ieta : {}}
                    if depth not in self.fitWeights: self.fitWeights[depth] = {ieta : {}}
                    if depth not in self.statErrors: self.statErrors[depth] = {ieta : {}}
                    if depth not in self.systErrors: self.systErrors[depth] = {ieta : {}}
                    if depth not in self.averagePulseStatErrors: self.averagePulseStatErrors[depth] = {ieta : {}}
                    if depth not in self.averagePulseSystErrors: self.averagePulseSystErrors[depth] = {ieta : {}}

                    if ieta not in self.weightHistos[depth]: self.weightHistos[depth][ieta] = {}
                    if ieta not in self.fitWeights[depth]: self.fitWeights[depth][ieta] = {}
                    if ieta not in self.statErrors[depth]: self.statErrors[depth][ieta] = {}
                    if ieta not in self.systErrors[depth]: self.systErrors[depth][ieta] = {}
                    if ieta not in self.averagePulseStatErrors[depth]: self.averagePulseStatErrors[depth][ieta] = {}
                    if ieta not in self.averagePulseSystErrors[depth]: self.averagePulseSystErrors[depth][ieta] = {}
                    if ieta not in self.pulseShapesNOPU[depth]: self.pulseShapesNOPU[depth][ieta] = {}
                    if ieta not in self.pulseShapesPU[depth]: self.pulseShapesPU[depth][ieta] = {}

                else:
                    depth = int(chunks[0].split("d")[1])

                if "nTPs" in keyName: self.ietaDensity[depth] = obj
                elif "pulseNOPU" in keyName:
                    tsCut = int(chunks[2].split("TS2gt")[1])
                    self.pulseShapesNOPU[depth][ieta][tsCut] = obj
                elif "pulsePU" in keyName:
                    tsCut = int(chunks[2].split("TS2gt")[1])
                    self.pulseShapesPU[depth][ieta][tsCut] = obj
                elif "wcorr" in keyName: self.corrHistos[depth][ieta] = obj
                elif "w" in keyName:
                    weight = int(chunks[2].split("w")[1])
                    self.weightHistos[depth][ieta][weight] = obj
            f.Close()

    # Method for extracting weights based on the average pulse shape in each ieta ring, depth
    def extractAveragePulseWeights(self):

        for depth in self.depths:

            self.averagePulseWeights[depth] = {}
            for ieta in self.HBHEieta:

                self.averagePulseWeights[depth][ieta] = {}
                for iWeight in self.iWeights:
                    self.averagePulseWeights[depth][ieta][iWeight] = {}

                for ts2Cut in self.ts2Cuts:

                    puPulse   = numpy.zeros((8,1)); puPulseErrors   = numpy.zeros((8,1))
                    nopuPulse = numpy.zeros((8,1)); nopuPulseErrors = numpy.zeros((8,1))

                    avePUpulse   = self.pulseShapesPU[depth][ieta][ts2Cut].ProfileX("i%d_d%d_TSgt%d_PU_prof"%(ieta,depth,ts2Cut), 1, -1)
                    aveNOPUpulse = self.pulseShapesNOPU[depth][ieta][ts2Cut].ProfileX("i%d_d%d_TSgt%d_NOPU_prof"%(ieta,depth,ts2Cut), 1, -1)

                    for ts in xrange(avePUpulse.GetNbinsX()):
                        puPulse[ts]       = avePUpulse.GetBinContent(ts+1)
                        puPulseErrors[ts] = avePUpulse.GetBinError(ts+1)

                    for ts in xrange(aveNOPUpulse.GetNbinsX()):
                        nopuPulse[ts]       = aveNOPUpulse.GetBinContent(ts+1)
                        nopuPulseErrors[ts] = aveNOPUpulse.GetBinError(ts+1)

                    weights = self.extractWeights(puPulse, nopuPulse)
                    for ts in xrange(0, weights.size): self.averagePulseWeights[depth][ieta][ts+1][ts2Cut] = weights[ts]

                    if ts2Cut == 3:
                        weightErrors = self.getAveragePulseStatError(puPulse, nopuPulse, puPulseErrors, nopuPulseErrors)
                        self.averagePulseStatErrors[depth][ieta][1] = weightErrors[0]
                        self.averagePulseStatErrors[depth][ieta][2] = weightErrors[1]

                for iWeight in self.iWeights:

                    # Use different selections on SOI-1 to derive systematic for average pulse weights
                    averagePulseWeights = [] 
                    for ts2Cut in self.ts2Cuts:
                        if self.averagePulseWeights[depth][ieta][iWeight][ts2Cut] != -999:
                            averagePulseWeights.append(self.averagePulseWeights[depth][ieta][iWeight][ts2Cut])
                    
                    if averagePulseWeights == []: self.averagePulseSystErrors[depth][ieta][iWeight] = -999
                    else: self.averagePulseSystErrors[depth][ieta][iWeight] = numpy.std(averagePulseWeights)

    def extractWeights(self, puPulse, nopuPulse):

        # Don't try to extract weights with an empty pulse
        if numpy.count_nonzero(nopuPulse) == 0 or numpy.count_nonzero(puPulse) == 0: 

            weights = numpy.zeros((2,1))
            weights[0] = -999; weights[1] = -999

            return weights

        ifPrint = (1 == 0)

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
        if self.tpSamples == 2: soiMask[2:4] = numpy.ones((2,1))
        elif self.tpSamples == 1: soiMask[2] = 1

        puSums = numpy.matmul(puTSMatrix,soiMask)
        nopuSums = numpy.matmul(nopuTSMatrix,soiMask)
        puContrib = numpy.subtract(nopuSums, puSums)

        W = numpy.array([-999,-999])
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
        if ifPrint and int(W[1]) == W[1]: print toPrint

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
                
                if   category == "PU":   histo = self.pulseShapesPU[depth][ieta][self.ts2Cut]
                elif category == "NOPU": histo = self.pulseShapesNOPU[depth][ieta][self.ts2Cut]
                else: continue

                # No need to print out empty plot (for ieta, depth that does not exist...)
                if histo.GetEntries() == 0: continue

                cname = "c_i%d_d%d_%s"%(ieta,depth,category)
                canvas = ROOT.TCanvas(cname, cname, 2400, 2400); canvas.cd()
                ROOT.gPad.SetRightMargin(0.13)
                ROOT.gPad.SetLeftMargin(0.12)

                averagePulse = histo.ProfileX("prof_i%d_d%d_%s"%(ieta,depth,category),1,-1) 

                histo.SetContour(255)
                theTitle = "|i#eta| = %d"%(ieta)
                if depth != 0: theTitle += ", Depth = %d"%(depth)
                histo.SetTitle(theTitle)
                histo.GetYaxis().SetTitle("ADC (Linearized)")
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

                outPath = "%s/PulseShapes/ieta%d/depth%d/%s"%(self.outPath,ieta,depth,category)
                if not os.path.exists(outPath): os.makedirs(outPath)
                canvas.SaveAs(outPath + "/AveragePulse.pdf")

    # Method for drawing histogram of correlation between wSOI-1 and wSOI-2
    def drawWeightCorrs(self):

        for depth in self.depths:
            for ieta in self.HBHEieta:

                histo = self.corrHistos[depth][ieta]

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
    def drawWeightHisto(self, ieta, depth, iWeight, weight, statError, systError, weightHisto, histoFit):

        canvas = ROOT.TCanvas("c_i%d_d%d_w%d"%(ieta,depth,iWeight), "c_i%d_d%d_w%d"%(ieta,depth,iWeight), 2400, 2400); canvas.cd()
        canvas.SetGridx()
        canvas.SetGridy()
        ROOT.gPad.SetRightMargin(0.03)
        ROOT.gPad.SetLeftMargin(0.15)

        weightHisto.GetXaxis().SetRangeUser(-9,3)
        theTitle = "|ieta| = %d"%(ieta)
        if depth != 0: theTitle += ", Depth = %d"%(depth)
        weightHisto.SetTitle(theTitle)
        weightHisto.GetXaxis().SetTitle("w_{SOI-%d}"%(3-iWeight))
        weightHisto.GetYaxis().SetTitle("A.U.")
        weightHisto.GetYaxis().SetLabelSize(0.6*0.048); weightHisto.GetYaxis().SetTitleSize(0.054); weightHisto.GetYaxis().SetTitleOffset(1.45)
        weightHisto.GetXaxis().SetLabelSize(0.6*0.048); weightHisto.GetXaxis().SetTitleSize(0.054); weightHisto.GetXaxis().SetTitleOffset(0.9)

        weightHisto.SetLineWidth(3)
        weightHisto.SetLineColor(ROOT.kBlack)

        histoFit.SetLineColor(ROOT.kRed)
        histoFit.SetLineWidth(5)
        histoFit.SetLineStyle(7)

        someText = ROOT.TPaveText(0.2, 0.65, 0.6, 0.85, "trNDC")

        someText.AddText("Peak = %3.2f #pm  %3.2f (stat.) #pm  %3.2f (sys.)"%(weight,statError,systError))
        someText.AddText("#chi^{2} / DOF = %3.2f / %d"%(histoFit.GetChisquare(), histoFit.GetNDF()))
        someText.AddText("Entries = %d"%(weightHisto.GetEntries()))
        someText.SetTextAlign(31)
        someText.SetFillColor(ROOT.kWhite);

        weightHisto.Draw("HIST")
        histoFit.Draw("SAME")
        someText.Draw("SAME")
    
        outPath = "%s/Fits/ieta%d/depth%d/SOI-%d"%(self.outPath,ieta,depth,3-iWeight)
        if not os.path.exists(outPath): os.makedirs(outPath)
        canvas.SaveAs(outPath + "/WeightDistribution.pdf")

    # Method for getting weights from fit of weight distribution
    def extractFitWeights(self, ieta, depth, iWeight, save=False):

        for iWeight in self.iWeights:
            for depth in self.depths:
                for ieta in self.HBHEieta:

                    histo = self.weightHistos[depth][ieta][iWeight]
                    if histo.Integral() == 0:
                        self.fitWeights[depth][ieta][iWeight] = -999 
                        self.statErrors[depth][ieta][iWeight] = -999 
                        self.systErrors[depth][ieta][iWeight] = -999 
                        return

                    numEntries = float(histo.GetEntries())
                    histo.Scale(1./histo.Integral())

                    # Keys of these dictionaries correspond to rebinnings
                    rebinHistos     = {0 : 0, 1 : 0, 2 : 0, 3 : 0, 4 : 0}
                    rebinFits       = {0 : 0, 1 : 0, 2 : 0, 3 : 0, 4 : 0}
                    rebinWeights    = numpy.zeros((5,1))
                    rebinStatErrors = numpy.zeros((5,1)) 
                    for rebin in rebinHistos.keys(): rebinHistos[rebin] = histo.Rebin(rebin+1, "r%d_i%d_d%d_w%d"%(rebin,ieta,depth,iWeight))

                    for rebin, rHisto in rebinHistos.iteritems():
                        binmax = rHisto.GetMaximumBin(); xmax = rHisto.GetBinCenter(binmax); binWidth = rHisto.GetBinWidth(1)
                        name = "f_i%d_d%d_r%d_w%d"%(ieta,depth,rebin,iWeight); funcString = "gaus(0)"; theFunc = 0; fitWidth = 2.0*binWidth; fitRange = [xmax-fitWidth,xmax+fitWidth]

                        theFunc = ROOT.TF1(name, funcString, fitRange[0], fitRange[1])
                        theFunc.SetParameters(0.2, 0, 2.5)
                        theFunc.SetParNames("A", "mu", "sigma")
                        theFunc.SetParLimits(1, -2.5,2.5)
                        theFunc.SetParLimits(2, 0, 5)

                        rHisto.Fit(name, "QMRWL")

                        rebinWeights[rebin-1] = theFunc.GetParameter("mu")
                        meanError = theFunc.GetParameter("sigma")

                        rebinFits[rebin-1] = theFunc
                        rebinStatErrors[rebin-1] = meanError / math.sqrt(numEntries) 

                    theWeight = rebinWeights[self.rebin-1]; theStatError = rebinStatErrors[self.rebin-1]

                    # From the five different fits the histogram determine the standard dev of the weights 
                    systError = numpy.std(rebinWeights)
                    self.fitWeights[depth][ieta][iWeight] = theWeight
                    self.statErrors[depth][ieta][iWeight] = theStatError 
                    self.systErrors[depth][ieta][iWeight] = systError

                    if save: self.drawWeightHisto(ieta, depth, iWeight, theWeight, theStatError, systError, rebinHistos[self.rebin], rebinFits[self.rebin])

    # Method for calculating the error on an average weight calculated from an ensemble
    def getAverageError(self, errorDict, det, iWeight):

        runningTotal = 0.0

        for ieta in errorDict.keys():
            
            if errorDict[ieta][iWeight] == -999 or errorDict[ieta][iWeight] == 0.0: continue

            if ieta in self.HBieta  and det == "HB":  runningTotal += 1.0 / errorDict[ieta][iWeight]**2
            if ieta in self.HE1ieta and det == "HE1": runningTotal += 1.0 / errorDict[ieta][iWeight]**2
            if ieta in self.HE2ieta and det == "HE2": runningTotal += 1.0 / errorDict[ieta][iWeight]**2

        if runningTotal == 0.0: return 0.0

        aveError = 1.0 / math.sqrt(runningTotal)

        return aveError

    # Method for calculating the average weight for HB, HE1 and HE2
    def getSubdetAverageWeights(self, weightDict):

        # Keys are detector, iWeight, depth; average over ieta in each detector for each depth 
        subdetAverageWeights = {"HB" : {}, "HE1" : {}, "HE2" : {}};
       
        # Setup maps for average weights and extract the weights from fits
        for iWeight in self.iWeights:
            subdetAverageWeights["HB"][iWeight] =  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            subdetAverageWeights["HE1"][iWeight] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            subdetAverageWeights["HE2"][iWeight] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        for depth in self.depths:
            
            # Empty ietaDensity means we aren't looking at this depth...
            if self.ietaDensity[depth].GetEntries() == 0: continue

            tpsHB  = self.ietaDensity[depth].Integral(1,16)
            tpsHE1 = self.ietaDensity[depth].Integral(17,20)
            tpsHE2 = self.ietaDensity[depth].Integral(21,28)

            for ieta in self.HBHEieta:
                for iWeight in weightDict[depth][ieta].keys():

                    # Not very clean way of getting weight from extra dictionary or not
                    weight = 0
                    if type(weightDict[depth][ieta][iWeight]) is dict: weight = weightDict[depth][ieta][iWeight][self.ts2Cut]
                    else: weight = weightDict[depth][ieta][iWeight]

                    if weight == -999: continue 

                    ietaTPs = float(self.ietaDensity[depth].GetBinContent(ieta))
                    if   ieta in self.HBieta:  subdetAverageWeights["HB"][iWeight][depth]  += weight * ietaTPs / float(tpsHB) 
                    elif ieta in self.HE1ieta: subdetAverageWeights["HE1"][iWeight][depth] += weight * ietaTPs / float(tpsHE1) 
                    elif ieta in self.HE2ieta: subdetAverageWeights["HE2"][iWeight][depth] += weight * ietaTPs / float(tpsHE2) 

        return subdetAverageWeights

    # Method for writing out a text file summarizing all the extracted weights
    def getWeightSummary(self):

        aveSummary = open("%s/aveWeightSummary.txt"%(self.outPath), "w")
        summary = open("%s/weightSummary.txt"%(self.outPath), "w")

        averagePulseSubdetWeights = self.getSubdetAverageWeights(self.averagePulseWeights)
        subdetWeights = self.getSubdetAverageWeights(self.fitWeights)

        for depth in self.depths:
            str2Write = "\nDepth %d:\n"%(depth); str2WriteAve = "\nDepth %d:\n"%(depth)

            for ieta in self.HBHEieta:
                ietaStr = "%d"%(ieta)
                ietaStr = ietaStr.rjust(2)

                str2WriteAve += "ieta: %s   "%(ietaStr)
                for iWeight in reversed(self.averagePulseWeights[depth][ieta].keys()):
                    if self.averagePulseWeights[depth][ieta][iWeight][self.ts2Cut] == -999:
                        str2WriteAve += ". . . . . . . . . . . . . . . . . . . . . . .   " 
                    else:
                        weightStr = "%3.2f"%(self.averagePulseWeights[depth][ieta][iWeight][self.ts2Cut]); weightStr = weightStr.rjust(5)
                        str2WriteAve += "wSOI-%d: %s +/- %3.2f (stat.) +/- %3.2f (sys.)  "%(3-iWeight,weightStr,self.averagePulseStatErrors[depth][ieta][iWeight],self.averagePulseSystErrors[depth][ieta][iWeight])
                str2WriteAve += "\n"

                str2Write += "ieta: %s   "%(ietaStr)
                for iWeight in reversed(self.fitWeights[depth][ieta].keys()):
                    if self.fitWeights[depth][ieta][iWeight] == -999: 
                        str2Write += ". . . . . . . . . . . . . . . . . . . . . . .   " 
                    else: 
                        weightStr = "%3.2f"%(self.fitWeights[depth][ieta][iWeight]); weightStr = weightStr.rjust(5)
                        str2Write += "wSOI-%d: %s +/- %3.2f (stat.) +/- %3.2f (sys.)  "%(3-iWeight,weightStr,self.statErrors[depth][ieta][iWeight],self.systErrors[depth][ieta][iWeight])
                str2Write += "\n"

            aveSummary.write(str2WriteAve)
            summary.write(str2Write)

        summary.write("\n\n"); aveSummary.write("\n\n")
        for det, weightDict in subdetWeights.iteritems():

            summary.write("%s:   \n"%(det)); aveSummary.write("%s:   \n"%(det))
            for iWeight in reversed(weightDict.keys()): 

                summary.write("wSOI-%d   "%(3-iWeight))
                aveSummary.write("wSOI-%d   "%(3-iWeight))
                for iDepth in xrange(len(weightDict[iWeight])):

                    if iDepth == 0: continue
                    # No real average set, no need to print...
                    if weightDict[iWeight][iDepth] != 0.0:
                        aveStatError = self.getAverageError(self.statErrors[iDepth], det, iWeight)
                        aveSystError = self.getAverageError(self.systErrors[iDepth], det, iWeight)
                        summary.write("Depth %d: %3.2f +/- %3.2f (stat.) +/- %3.2f (sys.)   "%(iDepth,weightDict[iWeight][iDepth],aveStatError,aveSystError))
                    else:
                        summary.write(". . . . . . . . . . . . . . . . . . . . . . . .   ")

                    if averagePulseSubdetWeights[det][iWeight][iDepth] != 0.0:
                        aveStatError = self.getAverageError(self.averagePulseStatErrors[iDepth], det, iWeight) 
                        aveSystError = self.getAverageError(self.averagePulseSystErrors[iDepth], det, iWeight) 
                        aveSummary.write("Depth %d: %3.2f +/- %3.2f (stat.) +/- %3.2f (sys.)   "%(iDepth, averagePulseSubdetWeights[det][iWeight][iDepth], aveStatError, aveSystError))
                    else:
                        aveSummary.write(". . . . . . . . . . . . . . . . . . . . . . . .   ")

                summary.write("\n")
                aveSummary.write("\n")
                      
            summary.write("\n\n")
            aveSummary.write("\n\n")
                    
        summary.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--tag"       , dest="tag"       , help="Unique tag for output" , type=str     , default="TAG")
    parser.add_argument("--fromCache" , dest="fromCache" , help="Read from cache file"  , default=False, action="store_true")
    parser.add_argument("--algo"      , dest="algo"      , help="Which reco scheme"     , type=str     , default="ALGO")
    parser.add_argument("--evtRange"  , dest="evtRange"  , help="Start and number"      , type=int     , nargs="+", default=[-1,0])
    
    arg = parser.parse_args()

    gFromCache = arg.fromCache
    eventRange = xrange(arg.evtRange[0], arg.evtRange[0]+arg.evtRange[1]) 

    aPath = ""; outPath = "./plots/Weights/%s/TP/%s"%(scheme,arg.tag)
                
    PUFile   = "root://cmseos.fnal.gov//store/user/jhiltbra/HCAL_Trigger_Study/WeightExtraction/NoContain/Depth/OOT.root"
    noPUFile = "root://cmseos.fnal.gov//store/user/jhiltbra/HCAL_Trigger_Study/WeightExtraction/NoContain/Depth/NOPU.root"

    theExtractor = WeightExtractor(arg.algo, PUFile, noPUFile, outPath)
    theExtractor.eventLoop(eventRange)

    if gFromCache:
        theExtractor.loadHistograms()
        theExtractor.extractFitWeights()
        theExtractor.extractAveragePulseWeights()
        theExtractor.getWeightSummary()

        theExtractor.drawPulseShapes("PU")
        theExtractor.drawPulseShapes("NOPU")
        theExtractor.drawWeightCorrs()
