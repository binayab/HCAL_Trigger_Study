import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras

import sys, os

from algo_weights import pfaWeightsMap
from Configuration.AlCa.GlobalTag import GlobalTag

if len(sys.argv) < 4:
    print("An example call to cmsRun: 'cmsRun analyze_HcalTrig.py PFA3p_PER_IETA 50PU 0'")
    exit()

PFA       = str(sys.argv[2])
inputFile = str(sys.argv[3])
job       = str(sys.argv[4])

isData = "DATA" in inputFile

# Intialize the process based on the era
process = 0
if isData: process = cms.Process('RAW2DIGI', eras.Run2_2018)
else:      process = cms.Process('RAW2DIGI', eras.Run3)

# Import of standard configurations
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
process.load("RecoLocalCalo.Configuration.hcalLocalReco_cff")

# Set the global tag if we are running on MC or data 
process.GlobalTag = GlobalTag(process.GlobalTag, '106X_mcRun3_2021_realistic_v3', '')

print "Using PeakFinderAlgorithm %s"%(PFA)
if "1" not in PFA:
    print "Only using 2 samples"
    process.simHcalTriggerPrimitiveDigis.numberOfSamples = 2
else:
    print "Only using 1 sample"
    process.simHcalTriggerPrimitiveDigis.numberOfSamples = 1

process.simHcalTriggerPrimitiveDigis.numberOfPresamples = 0

if PFA in pfaWeightsMap:
    print "Using weights: "
    print pfaWeightsMap[PFA]
    process.simHcalTriggerPrimitiveDigis.PeakFinderAlgorithmWeights = pfaWeightsMap[PFA] 
else:
    print "No weights defined for algo \"%s\"; defaulting to zero weights!"%(PFA)

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)

# Input source, here a few different pre-defined sets of files
if "DATA" in inputFile:
    process.GlobalTag = GlobalTag(process.GlobalTag, '106X_dataRun2_v26', '')
    process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/data/Run2018D/JetHT/RAW/v1/000/324/021/00000/DC207766-1C12-DC44-B679-89EB77C5EE2A.root', # LS 44 of Run 324021        
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/data/Run2018D/JetHT/RAW/v1/000/324/021/00000/0B051695-EFBF-3F47-874D-92DE9278FA75.root', # LS 45 of Run 324021
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/data/Run2018D/JetHT/RAW/v1/000/324/021/00000/9318ED7A-17EB-6644-9DE8-1FF212666945.root', # LS 49 of Run 324021
        ),
        secondaryFileNames = cms.untracked.vstring(),
    )

elif "TTbar_OOT" in inputFile:
    process.GlobalTag = GlobalTag(process.GlobalTag, '106X_upgrade2021_realistic_v4', '')
    process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/106X_upgrade2021_realistic_v4-v1_50PU/20000/TTbar-DIGI-RAW-50PU-OOT_1.root',
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/106X_upgrade2021_realistic_v4-v1_50PU/20000/TTbar-DIGI-RAW-50PU-OOT_2.root',
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/106X_upgrade2021_realistic_v4-v1_50PU/20000/TTbar-DIGI-RAW-50PU-OOT_3.root',
    
        ),
        secondaryFileNames = cms.untracked.vstring(),
    )

elif "NuGun_OOT" in inputFile:
    process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/relval/CMSSW_10_6_1_patch1/RelValNuGun/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3_50PU/10000/NuGun-DIGI-RAW-50PU_OOT.root',
        ),
        secondaryFileNames = cms.untracked.vstring(),
    )

elif "TTbar_NOPU" in inputFile:
    process.GlobalTag = GlobalTag(process.GlobalTag, '106X_upgrade2021_realistic_v4', '')
    process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/106X_upgrade2021_realistic_v4-v1_50PU/20000/TTbar-DIGI-RAW-NOPU.root',
        ),
        secondaryFileNames = cms.untracked.vstring(),
    )

elif "TTbar_0PU" in inputFile:
    process.GlobalTag = GlobalTag(process.GlobalTag, '106X_upgrade2021_realistic_v4', '')
    process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/106X_upgrade2021_realistic_v4-v1_50PU/20000/TTbar-DIGI-RAW-0PU123.root',
        ),
        secondaryFileNames = cms.untracked.vstring(),
    )

elif "TTbar_50PU" in inputFile: 
    process.GlobalTag = GlobalTag(process.GlobalTag, '106X_upgrade2021_realistic_v4', '')
    process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/106X_upgrade2021_realistic_v4-v1_50PU/20000/TTbar-DIGI-RAW-50PU-50PU_1.root',
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/106X_upgrade2021_realistic_v4-v1_50PU/20000/TTbar-DIGI-RAW-50PU-50PU_2.root',
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/106X_upgrade2021_realistic_v4-v1_50PU/20000/TTbar-DIGI-RAW-50PU-50PU_3.root',
        ),
        secondaryFileNames = cms.untracked.vstring(),
    )
elif "NuGun_50PU" in inputFile:
    process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/relval/CMSSW_10_6_1_patch1/RelValNuGun/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3_50PU/10000/NuGun-DIGI-RAW-50PU.root',
        ),
        secondaryFileNames = cms.untracked.vstring(),
    )

elif "TimeSlew_NOPU" in inputFile:
    process.GlobalTag = GlobalTag(process.GlobalTag, '106X_upgrade2021_realistic_v4', '')
    process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/relval/CMSSW_10_6_1/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_TimeSlew0_v3-v1/10000/TTbar-DIGI-RAW-NOPU123-FixedSlew.root',
        ),
        secondaryFileNames = cms.untracked.vstring(),
    )
elif "TimeSlew_PU" in inputFile:
    process.GlobalTag = GlobalTag(process.GlobalTag, '106X_upgrade2021_realistic_v4', '')
    process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/relval/CMSSW_10_6_1/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_TimeSlew0_v3-v1/10000/TTbar-DIGI-RAW-55to75PU-FixedSlew_1.root',
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/relval/CMSSW_10_6_1/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_TimeSlew0_v3-v1/10000/TTbar-DIGI-RAW-55to75PU-FixedSlew_901.root',
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/relval/CMSSW_10_6_1/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_TimeSlew0_v3-v1/10000/TTbar-DIGI-RAW-55to75PU-FixedSlew_1801.root',
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/relval/CMSSW_10_6_1/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_TimeSlew0_v3-v1/10000/TTbar-DIGI-RAW-55to75PU-FixedSlew_2701.root',
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/relval/CMSSW_10_6_1/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_TimeSlew0_v3-v1/10000/TTbar-DIGI-RAW-55to75PU-FixedSlew_3601.root',
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/relval/CMSSW_10_6_1/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_TimeSlew0_v3-v1/10000/TTbar-DIGI-RAW-55to75PU-FixedSlew_4501.root',
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/relval/CMSSW_10_6_1/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_TimeSlew0_v3-v1/10000/TTbar-DIGI-RAW-55to75PU-FixedSlew_5401.root',
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/relval/CMSSW_10_6_1/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_TimeSlew0_v3-v1/10000/TTbar-DIGI-RAW-55to75PU-FixedSlew_6301.root',
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/relval/CMSSW_10_6_1/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_TimeSlew0_v3-v1/10000/TTbar-DIGI-RAW-55to75PU-FixedSlew_7201.root',
            'root://cmseos.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/relval/CMSSW_10_6_1/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_TimeSlew0_v3-v1/10000/TTbar-DIGI-RAW-55to75PU-FixedSlew_8101.root',
        ),
        secondaryFileNames = cms.untracked.vstring(),
    )

else:
    process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring('%s'%(inputFile),),
        secondaryFileNames = cms.untracked.vstring(),
    )

process.options = cms.untracked.PSet()

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('analyze nevts:-1'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Make an analysis path
process.startjob = cms.Path(                                                   
  process.hcalDigis*                                                                        
  process.hbheprereco
)

# Path and EndPath definitions
process.endjob_step = cms.EndPath(process.endOfProcess)

# Schedule definition
process.schedule = cms.Schedule(process.startjob,process.endjob_step)      
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# Automatic addition of the customisation function from Debug.HcalDebug.customize
from Debug.HcalDebug.customize import use_data_reemul_tp,compare_raw_reemul_tp,compare_reemul_reco_sev9 

process =  use_data_reemul_tp(process)

#call to customisation function compare_raw_reemul_tp imported from Debug.HcalDebug.customize
#process = compare_raw_reemul_tp(process)

#call to customisation function compare_reemul_reco_sev9 imported from Debug.HcalDebug.customize
process = compare_reemul_reco_sev9(process)

process.TFileService.fileName=cms.string('hcalNtuple_%s.root'%(job))

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
