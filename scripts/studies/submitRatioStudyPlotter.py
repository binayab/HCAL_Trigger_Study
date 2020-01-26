#!/usr/bin/env python

# This is a simple wrapper script to run the ratioStudyPlotter over ntuples produced with different weight variations.
# Its sole purpose is to make ratio plotting simple when running over many versions of ntuples 
import os, sys, argparse, subprocess, shutil

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--schemes"   , dest="schemes"   , help="Which PFA to use"           , type=str , nargs="+", required=True)
    parser.add_argument("--process"   , dest="process"   , help="Unique of process (subdir)" , type=str , default="TTbar")
    parser.add_argument("--versions"  , dest="versions"  , help="List versions of weights"   , type=str , nargs="+", required=True)
    parser.add_argument("--variations", dest="variations", help="Do up/down variations"      , default=False, action="store_true")
    parser.add_argument("--depth"     , dest="depth"     , help="Do depth version"           , default=False, action="store_true")
    parser.add_argument("--mean"      , dest="mean"      , help="Do mean version"            , default=False, action="store_true")
    parser.add_argument("--noSubmit"  , dest="noSubmit"  , help="Don't run commands"         , default=False, action="store_true")
    args = parser.parse_args()

    schemes    = args.schemes
    process    = args.process
    versions   = args.versions
    variations = args.variations
    depth      = args.depth
    mean       = args.mean
    noSubmit   = args.noSubmit

    HOME = os.getenv("HOME")

    SCRIPT = "%s/nobackup/HCAL_Trigger_Study/scripts/studies/ratioStudyPlotter.py"%(HOME)

    for scheme in schemes:
        for version in versions:
            
            weights = scheme
            if depth: weights += "_DEPTH_AVE"

            weights += "_%s"%(version)
        
            if mean: weights += "_MEAN"

            INPUTDIR = "%s/%s"%(process, weights)

            theCommand = "(nohup python %s %s > /dev/null 2>&1 &)"%(SCRIPT, INPUTDIR)
            print "Executing command: '%s'"%(theCommand)
            if not noSubmit: subprocess.call(theCommand.split())

            # If we want the up/down variations, make the call for those as well
            if variations:

                INPUTDIRUP = INPUTDIR + "_UP"
                theCommand = "(nohup python %s %s > /dev/null 2>&1 &)"%(SCRIPT, INPUTDIRUP)
                print "Executing command: '%s'"%(theCommand)
                if not noSubmit: subprocess.call(theCommand.split())

                INPUTDIRDOWN = INPUTDIR + "_DOWN"
                theCommand = "(nohup python %s %s > /dev/null 2>&1 &)"%(SCRIPT, INPUTDIRDOWN)
                print "Executing command: '%s'"%(theCommand)
                if not noSubmit: subprocess.call(theCommand.split())
