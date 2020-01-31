#!/usr/bin/env python

# This is a simple wrapper script to run the ratioStudyPlotter over ntuples produced with different weight variations.
# Its sole purpose is to make ratio plotting simple when running over many versions of ntuples 
import os, sys, argparse, subprocess, shutil

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--schemes"  , dest="schemes"   , help="Which PFA to use"           , type=str , nargs="+", required=True)
    parser.add_argument("--inputPath", dest="inputPath" , help="Subpath to input files"     , type=str , required=True)
    parser.add_argument("--versions" , dest="versions"  , help="List versions of weights"   , type=str , nargs="+", default=[""])
    parser.add_argument("--updown"   , dest="updown"    , help="Do up/down variations"      , default=False, action="store_true")
    parser.add_argument("--depth"    , dest="depth"     , help="Do depth version"           , default=False, action="store_true")
    parser.add_argument("--mean"     , dest="mean"      , help="Do mean version"            , default=False, action="store_true")
    parser.add_argument("--noSubmit" , dest="noSubmit"  , help="Don't run commands"         , default=False, action="store_true")
    args = parser.parse_args()

    schemes    = args.schemes
    inputStub  = args.inputPath
    versions   = args.versions
    updown     = args.updown
    depth      = args.depth
    mean       = args.mean
    noSubmit   = args.noSubmit

    HOME = os.getenv("HOME")

    SCRIPT = "%s/nobackup/HCAL_Trigger_Study/scripts/studies/ratioStudyPlotter.py"%(HOME)

    # Loop over the schemes (PFA2p, PFA1p, etc.)
    # and for each scheme construct the different
    # versions (PER_IETA, AVE, MEAN)
    for scheme in schemes:
        for version in versions:
            
            # Begin constructing the unique weights tag
            weights = scheme

            if depth: weights += "_DEPTH_AVE"
            if version: weights += "_%s"%(version)
            if mean: weights += "_MEAN"

            INPUTDIR = "%s/%s"%(inputStub, weights)

            theCommand = "python %s --inputSubPath %s"%(SCRIPT, INPUTDIR)
            print "Executing command: '%s'"%(theCommand)

            FOUT = open("%s.txt"%(weights), 'w')
            if not noSubmit: subprocess.Popen(theCommand.split(), stdout=FOUT, stderr=subprocess.STDOUT)

            # If we want the up/down variations, make the call for those as well
            if updown:

                INPUTDIRUP = INPUTDIR + "_UP"
                theCommand = "python %s --inputSubPath %s"%(SCRIPT, INPUTDIRUP)
                print "Executing command: '%s'"%(theCommand)

                FOUTUP = open("%s_UP.txt"%(weights), 'w')
                if not noSubmit: subprocess.Popen(theCommand.split(), stdout=FOUTUP, stderr=subprocess.STDOUT)

                INPUTDIRDOWN = INPUTDIR + "_DOWN"
                theCommand = "python %s --inputSubPath %s"%(SCRIPT, INPUTDIRDOWN)
                print "Executing command: '%s'"%(theCommand)

                if not noSubmit: subprocess.Popen(theCommand.split(), stdout=FOUTDOWN, stderr=subprocess.STDOUT)
                FOUTDOWN = open("%s_DOWN.txt"%(weights), 'w')
