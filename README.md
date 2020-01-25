# HCAL Pulse Filter Study

This is a repository of scripts for extracting pulse filter weights and applying the weights. There are three distinct steps to go through in order to get to the level of extracting the weights.

## Step 1: Producing a DIGI-RAW Files With and Without Pileup

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
process.mix.input.Special_Pileup_Studies = cms.untracked.string("Fixed ITPU Vary OOTPU")
process.mix.bunchspace = cms.int32(25)
process.mix.minBunch = cms.int32(-10)
process.mix.maxBunch = cms.int32(4)
```

An equivalent `cmsRun` configuration file can be made for the case of no pileup and can be done by excluding the `--pileup_input` and `--pileup` flags and chaning the name of the output file when calling `cmsDriver.py`.


## Step 2: Making HCAL Ntuples

To start, setup a CMSSW release (assuming working on LPC) and perform some other initial steps:

```
mkdir -p $HOME/nobackup
cd $HOME/nobackup/

git clone git@github.com:JHiltbrand/HCAL_Trigger_Study.git

mkdir cmssw plots

cd cmssw
cmsrel CMSSW_10_6_0_pre4
cd CMSSW_10_6_0_pre4/src
cmsenv
```

## Extracting Pulse Filter Weights

Weight extraction is done by the `weightExtraction(ForNuGun).py` script. Several commandline options can be specified and are documented below:

```
--tag       = A unique tag to keep the output organized in own folder.
--fromCache = Read back in root file for making plots (second step).
--contain   = When extracting weights, read input files from within a "Contain" subfolder ("NoContain" default)
--depth     = When extracting weights, read input files from within a "WithDepth" subfolder ("NoDepth" default)
--oot       = When extracting weights, read the OOT.root file instead of the 50PU.root file.
--algo      = Specify which pulse filter to extract weights for (PFA1p, PFA1pp, PFA2p, PFA2pp)
--evtRange  = First element is starting event to process and second element is number of events to process.
```

An example call of the `weightExtraction.py` script to extract no-depth weights for PFA1p for 100 events starting at event 527 could be:

```
python scripts/weightExtraction.py --oot --depth --algo PFA1p --tag WithDepth_TTbar_OOT --evtRange 527 100
```

This will make an output file in `$HOME/nobackup/HCAL_Trigger_Study/plots/Weights/PFA1p/TP/WithDepth_TTbar_OOT/root/histoCache_527.root`

When reading the cache file back in with the `--fromCache` flag, the file must be named `histoCache.root`

### Making an Event Map

To help speed looping over the events tree while extracting weights, one needs to generate an event map that maps an event record in one PU sample to the same event record in the NOPU sample. This is done by running `makeEventMap.py`. A call such as:

```
python makeEventMap.py --oot
```

will generate a python file `eventMap_NoContain_NoDepth_OOT.py` with a map `PU2NOPUMAP`. Copy this map into the `pu2nopuMap.py` file.

### Running on LPC Condor

A condor submission script, `submitWeightExtraction.py` is provided to submit jobs and speed up the extraction of weights when running on an entire input file. An example call to this script would be:

```
python scripts/submitWeightExtraction.py --oot --depth --algo PFA1p --tag WithDepth_TTbar_OOT --nJobs 90
```

The output files will be placed in the same location mentioned when running locally and one needs to hadd these files.

```
cd $HOME/nobackup/HCAL_Trigger_Study/plots/Weights/PFA1p/TP/WithDepth_TTbar_OOT/root
hadd histoCache.root histoCache_*
```
