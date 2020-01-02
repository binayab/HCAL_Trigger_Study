# HCAL_Trigger_Study

A repository of scripts for extracting pulse filter weights and applying the weights.

## Extracting Pulse Filter Weights

Weight extraction is done by the `weightExtraction(ForNuGun).py` script. Several commandline options can be specified and are documented below:

```
--tag = A unique tag to keep the output organized and separated in the case of running different configurations.
--fromCache = Read the root file containing all necessary information from its designated location for making plots
--contain = When extracting weights, designates reading input files from within a "Contain" subfolder
--depth = When extracting weights, designates reading input files from within a "WithDepth" subfolder ("NoDepth" default)
--oot = When extracting weights, read the OOT.root file instead of the 50PU.root file.
--algo = Specify which pulse filter to extract weights for (PFA1p, PFA1pp, PFA2p, PFA2pp)
--evtRange = First element is starting event to process and second element is number of events to process.
```

An example call of the `weightExtraction.py` script to extract weights could be:

```
python weightExtraction.py --oot --depth --algo PFA1p --tag WithDepth_TTbar_OOT --evtRange 0 100
```
