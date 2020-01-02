# HCAL_Trigger_Study

A repository of scripts for extracting pulse filter weights and applying the weights. To start, setup a CMSSW release (assuming working on LPC) and perform some other initial steps:

```
mkdir -p $HOME/nobackup/HCAL_Trigger_Study/{scripts,cmssw,plots}
cd $HOME/nobackup/HCAL_Trigger_Study

git clone git@github.com:JHiltbrand/HCAL_Trigger_Study.git

cd ../cmssw
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
python weightExtraction.py --oot --depth --algo PFA1p --tag WithDepth_TTbar_OOT --evtRange 527 100
```

This will make an output file in `../plots/Weights/PFA1p/TP/WithDepth_TTbar_OOT/root/histoCache_527.root`

When reading the cache file back in with the `--fromCache` flag, the file must be named `histoCache.root`
