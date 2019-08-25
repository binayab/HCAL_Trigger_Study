# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: l1Ntuple -s RAW2DIGI --python_filename=ntuple_maker_def.py -n 10 --no_output --era=Run2_2018 --data --conditions=101X_dataRun2_HLT_v7 --customise=L1Trigger/Configuration/customiseReEmul.L1TReEmulFromRAWsimHcalTP --customise=L1Trigger/L1TNtuples/customiseL1Ntuple.L1NtupleRAWEMU --customise_commands=process.HcalTPGCoderULUT.LUTGenerationMode=cms.bool(False) --filein=/store/express/Run2017B/ExpressPhysics/FEVT/Express-v1/000/297/562/00000/EE1F5F26-145B-E711-A146-02163E019C23.root --no_exec
import FWCore.ParameterSet.Config as cms
import FWCore.PythonUtilities.LumiList as LumiList
from Configuration.StandardSequences.Eras import eras

import sys

process = cms.Process('RAW2DIGI',eras.Run2_2018)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff')
process.load('Configuration.StandardSequences.RawToDigi_Data_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load("SimCalorimetry.HcalTrigPrimProducers.hcaltpdigi_cff")                                                                                                                             

JSONfile = "" 
runNumber = int(sys.argv[2])
if runNumber == 325170:
    JSONfile = "/uscms_data/d3/jhiltb/HCAL_Trigger_Study/data/lumimask_325170.json"
elif runNumber == 325308:
    JSONfile = "/uscms_data/d3/jhiltb/HCAL_Trigger_Study/data/lumimask_325308.json"

PFA = int(sys.argv[3])
print "Using PeakFinderAlgorithm %d"%(PFA)
process.simHcalTriggerPrimitiveDigis.PeakFinderAlgorithm = cms.int32(PFA)

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(50000)
)

process.dump = cms.EDAnalyzer("EventContentAnalyzer")

# Input source
inputFiles = cms.untracked.vstring('%s'%(str(sys.argv[4])),)
process.source = cms.Source("PoolSource",
    fileNames = inputFiles,
    secondaryFileNames = cms.untracked.vstring()
)

if JSONfile == "":
    process.source.lumisToProcess = LumiList.LumiList(filename = JSONfile).getVLuminosityBlockRange()

process.options = cms.untracked.PSet(
    SkipEvent = cms.untracked.vstring('ProductNotFound'),
)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('l1Ntuple nevts:10'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
if runNumber == 0 or runNumber == 50:
    process.GlobalTag = GlobalTag(process.GlobalTag, '102X_upgrade2018_realistic_v12', '')
else:
    process.GlobalTag = GlobalTag(process.GlobalTag, '103X_dataRun2_HLT_v1', '')

# Path and EndPath definitions
process.raw2digi_step = cms.Path(process.RawToDigi)
process.endjob_step = cms.EndPath(process.endOfProcess)

# Schedule definition
process.schedule = cms.Schedule(process.raw2digi_step,process.endjob_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# customisation of the process.

# Automatic addition of the customisation function from L1Trigger.Configuration.customiseReEmul
from L1Trigger.Configuration.customiseReEmul import L1TReEmulFromRAWsimHcalTP 

#call to customisation function L1TReEmulFromRAWsimHcalTP imported from L1Trigger.Configuration.customiseReEmul
process = L1TReEmulFromRAWsimHcalTP(process)

# Automatic addition of the customisation function from L1Trigger.L1TNtuples.customiseL1Ntuple
from L1Trigger.L1TNtuples.customiseL1Ntuple import L1NtupleAODRAWEMU 

#call to customisation function L1NtupleRAWEMU imported from L1Trigger.L1TNtuples.customiseL1Ntuple
process = L1NtupleAODRAWEMU(process)

# End of customisation functions

# Customisation from command line
process.TFileService.fileName=cms.string('%s'%(str(sys.argv[5])))

process.HcalTPGCoderULUT.LUTGenerationMode=cms.bool(False)
# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
