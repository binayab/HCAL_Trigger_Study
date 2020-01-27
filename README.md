# HCAL Pulse Filter Study

This is a repository of scripts for extracting pulse filter weights and applying the weights. There are three distinct steps to go through in order to get to the level of extracting the weights.

DISCLAIMER: Any file paths implicitly assumed customized for the author and will not work out-of-the-box.

## Step 0: Some House Cleaning

First let's setup a working area for everything. If on LPC, making a `nobackup` are is not necessary. If not at LPC it is encouraged to make a `nobackup` folder as it is assumed by many scripts in this repository.

```
mkdir -p $HOME/nobackup
cd $HOME/nobackup/

git clone git@github.com:JHiltbrand/HCAL_Trigger_Study.git
cd HCAL_Trigger_Study

mkdir cmssw plots input
```

## Step 1: Producing a DIGI-RAW Files With and Without Pileup

Before we can proceed, we need to initialize a `CMSSW` area and compile:

```
cd $HOME/nobackup/HCAL_Trigger_Study/cmssw
cmsrel CMSSW_10_6_1_patch1
cd CMSSW_10_6_1_patch1/src
cmsenv

git cms-addpkg Mixing/Base

scram b -j8
```

The first step is to take a ttbar and/or nugun GEN-SIM file and produce two daughter GEN-SIM-DIGI-RAW files for exactly two different pileup scenarios. One daughter file will have no pileup mixed in while the other file will have pileup mixed in for whichever special pileup scenario is being studied.

Possible centrally-produced GEN-SIM files to be used could be:

**ttbar:**
https://cmsweb.cern.ch/das/request?input=dataset%3D%2FRelValTTbar_13%2FCMSSW_10_6_0_pre4-106X_upgrade2021_realistic_v4-v1%2FGEN-SIM&instance=prod/global

**nugun:**
https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fglobal&input=dataset%3D%2FRelValNuGun%2FCMSSW_10_6_1_patch1-106X_mcRun3_2021_realistic_v3_rsb-v1%2FGEN-SIM

With these input files we can use `cmsDriver.py` to make a `cmsRun` configuration file for completeing the GEN-SIM-DIGI-RAW step. In the case of mixing in pileup we can call an incantation like:

```
cmsDriver.py
  --conditions auto:phase1_2019_realistic \
  --pileup_input das:/RelValMinBias_13/CMSSW_10_6_0_pre4-106X_upgrade2021_realistic_v4-v1/GEN-SIM \
  --filein das:/PUT/DAS/PATH/HERE \
  --era Run3 \
  --eventcontent FEVTDEBUGHLT \
  -s DIGI:pdigi_valid,L1,DIGI2RAW,HLT:@relval2017 \
  --datatier GEN-SIM-DIGI-RAW \
  --pileup AVE_50_BX_25ns \
  --geometry DB:Extended \
  --conditions 106X_upgrade2021_realistic_v4 \
  --fileout ootpu_cfg.py \
  --no_exec
```

As the process of mixing in pileup is intensive, it is recommended that instead of specifying all three GEN-SIM files as input to just specify each one in its own configuration file to be able to run in parallel. To configure for mixing in only out-of-time pileup open up the generated python configuration file and make sure the following lines are configuring the mixing module:

```
process.mix.input.nbPileupEvents.averageNumber = cms.double(50.000000)
process.mix.input.manage_OOT = cms.untracked.bool(True)
process.mix.input.OOT_type = cms.untracked.string("Poisson")
process.mix.input.Special_Pileup_Studies = cms.untracked.string("Fixed_ITPU_Vary_OOTPU")
process.mix.bunchspace = cms.int32(25)
process.mix.minBunch = cms.int32(-10)
process.mix.maxBunch = cms.int32(4)
```

An equivalent `cmsRun` configuration file can be made for the case of no pileup and can be done by excluding the `--pileup_input` and `--pileup` flags and changing the name of the output file when calling `cmsDriver.py`. After running `cmsRun ootpu_cfg.py` and waiting for many hours one will have a GEN-SIM-DIGI-RAW root file with pileup mixed in.

## Step 2: Making HCAL Ntuples

Once the GEN-SIM-DIGI-RAW files for the no pileup and out-of-time pileup scenario have been produced, they are processed with the `cms-hcal-trigger` framework to produce manageable and simple-to-use ROOT TTrees (ntuples) with quantities that are relevant to extracting weights.

To start, we setup a second CMSSW release (assuming working on LPC) and pull in some customized code:

```
cd $HOME/nobackup/HCAL_Trigger_Study/cmssw

cmsrel CMSSW_10_6_0_pre4
cd CMSSW_10_6_0_pre4/src
cmsenv

scram b -j8

git cms-merge-topic --unsafe JHiltbrand:JCH_OOTPU_dev
git clone git@github.com:JHiltbrand/cms-hcal-debug.git Debug/HcalDebug
git checkout -b JCH_OOTPU_dev --track origin/JCH_OOTPU_dev

scram b -j8
```

Before running, make sure to turn off pulse containment in `CalibCalorimetry/HcalTPGAlgos/src/HcaluLUTTPGCoder.cc` by commenting out the line:

```containmentCorrection2TSCorrected = pulseCorr_->correction(cell, 2, correctionPhaseNS, correctedCharge);```

then recompile again.

Once these steps are completed we are able to process the GEN-SIM-DIGI-RAW files and make ntuples for extracting pulse filter weights. An example of doing this would be:

```
cd $HOME/nobackup/HCAL_Trigger_Study/scripts

cmsRun analyze_HcalTrig.py PFA2 TTbar_OOT 27
```

Here `PFA2` is used more or less as a placeholder and is a meaningless option at this point. The `TTbar_OOT` will be parsed with the script and be used to determine which GEN-SIM-DIGI-RAW files will be run on. Lastly, the `27` will be used in the output root file name `hcalNtuples_27.root` which contains a simple TTree with information that can be used to extract weights.

### Making an Event Map

When we produce the ntuple files for no pileup and out-of-time pileup files, although all the same events are present in each, the events are not necessarily in the same order. To help speedup looping over the events tree while extracting weights, one needs to generate an event map that maps an event record in the OOT PU file to the same event record in the NOPU file. This is done by running `makeEventMap.py`. A call such as:

```
python makeEventMap.py --oot
```

will generate a python file `eventMap_NoContain_NoDepth_OOT.py` with a map `PU2NOPUMAP`. Copy this map into the `pu2nopuMap.py` file.

### Submitting to LPC Condor

The `analyze_HcalTrig.py` can be used in batch mode when submitting jobs to condor on LPC. The script `submitHcalTrigNtuples.py` handles all the condor job logistics and has several command line options.

```
--tag       = A unique tag to keep the output organized in its own folder.
--mean      = Make ntuples using mean version of weights.
--depth     = Make ntuples using depth averaged version of weights.
--dataset   = Either a DAS path or EOS path to DIGI-RAW files.
--updown    = Make ntuples with the up/down variation of the specified weights.
--versions  = A list of AVE and/or PER_IETA for the specified weights to use.
--schemes   = A list of PFA2p, PFA1p etc of which scheme to make ntuples with.
--noSubmit  = Don't submit to condor
```

Thus, for example, to generate ntuples when reconstructing with the PFA2p, PFA1p schemes and the mean, per-ieta and subdet average weights one could do:

 ```
 python submitHcalTrigNtuples.py \
     --tag 20200126 \
     --mean \
     --dataset /TTbar_14TeV_TuneCP5_Pythia8/Run3Summer19DR-106X_mcRun3_2021_realistic_v3-v2/GEN-SIM-DIGI-RAW \
     --versions PER_IETA AVE \
     --schemes PFA1p PFA2p
 ```

## Step 3: Extracting Pulse Filter Weights

Weight extraction is done by the `weightExtraction.py` script in the `extraction` subfolder. The script is run in two successive executions. The first execution does the looping over the HCAL ntuple files and extracts raw weights and writes raw histograms to a cache file. Then the script is run again to process the cache for making final plots and text files. Several commandline options can be specified and are documented below:

```
--tag       = A unique tag to keep the output organized in its own folder.
--fromCache = Read back in root file for making final plots and txt files (second step).
--contain   = When extracting weights, read input files from within a "Contain" subfolder ("NoContain" default)
--depth     = When extracting weights, read input files from within a "WithDepth" subfolder ("NoDepth" default)
--oot       = When extracting weights, read the OOT.root file instead of the 50PU.root file.
--nugun     = When extracting weights, assume we are running on nugun files (there will be no NOPU.root).
--scheme    = Specify which pulse filter to extract weights for (PFA1p, PFA1pp, PFA2p, PFA2pp)
--evtRange  = First element is starting event to process and second element is number of events to process.
```

A particular file/folder structure is anticipated when accessing the HCAL ntuple files. Most of the file path is built up based on the specified command line options. An example call of the `weightExtraction.py` script to extract no-depth weights for PFA1p for 100 events starting at event 527 (in the OOT pileup file) would be:

```
python scripts/weightExtraction.py --oot --depth --scheme PFA1p --tag WithDepth_TTbar_OOT --evtRange 527 100
```

This will make an output file in `$HOME/nobackup/HCAL_Trigger_Study/plots/Weights/PFA1p/WithDepth_TTbar_OOT/root/histoCache_527.root`

Since this script is also used to run in batch, each job would gets its own unique number and the above directory would be filled with `histoCache_XYZ.root` files. These need to be hadded together into a single `histoCache.root` file which will be looked for by the script when specifying the `--fromCache` option.

### Running on LPC Condor

A condor submission script, `submitWeightExtraction.py` is provided to submit jobs and speed up the extraction of weights when running on an entire input file. An example call to this script would be:

```
python scripts/submitWeightExtraction.py --oot --depth --scheme PFA1p --tag WithDepth_TTbar_OOT --nJobs 90
```

The output files will be placed in the same location mentioned when running locally and one needs to hadd these files.

```
cd $HOME/nobackup/HCAL_Trigger_Study/plots/Weights/PFA1p/TP/WithDepth_TTbar_OOT/root
hadd histoCache.root histoCache_*
```
