import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Eras import eras

import sys

if len(sys.argv) < 5:
    print("An example call to cmsRun: 'cmsRun analyze_HcalTrig.py 3 325170 Run3 /path/to/input.root'")
    exit()

PFA =  str(sys.argv[2])
run = str(sys.argv[3])
era = str(sys.argv[4])
inputFile = str(sys.argv[5])

stub = ""
if inputFile != "NULL": stub = "_" + inputFile.split("/")[-1].split(".root")[0]

process = 0
if era == "Run2": process = cms.Process('RAW2DIGI',eras.Run2_2018)
elif era == "Run3": process = cms.Process('RAW2DIGI',eras.Run3)

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
process.load("RecoLocalCalo.Configuration.hcalLocalReco_cff")

print "Using PeakFinderAlgorithm %s"%(PFA)
if "1" not in PFA:
    print "Only using 2 samples"
    process.simHcalTriggerPrimitiveDigis.numberOfSamples = 2
    process.simHcalTriggerPrimitiveDigis.numberOfPresamples = 0
else:
    print "Only using 1 sample"
    process.simHcalTriggerPrimitiveDigis.numberOfSamples = 1
    process.simHcalTriggerPrimitiveDigis.numberOfPresamples = 0

process.simHcalTriggerPrimitiveDigis.PeakFinderAlgorithmName = cms.untracked.string(PFA)

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)

# Input source
if inputFile == "NULL":
    process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(
            #'root://cmsxrootd.fnal.gov//store/user/jhiltbra/HCAL_Trigger_Study/TTbar_RelVal/TTbar-DIGI-RAW-50PU-OOT1.root',
            #'root://cmsxrootd.fnal.gov//store/user/jhiltbra/HCAL_Trigger_Study/TTbar_RelVal/TTbar-DIGI-RAW-50PU-OOT2.root',
            #'root://cmsxrootd.fnal.gov//store/user/jhiltbra/HCAL_Trigger_Study/TTbar_RelVal/TTbar-DIGI-RAW-50PU-OOT3.root',
    
            'root://cmsxrootd.fnal.gov//store/user/jhiltbra/HCAL_Trigger_Study/TTbar_RelVal/TTbar-DIGI-RAW-0PU123.root',
    
            #'root://cmsxrootd.fnal.gov///store/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/PU25ns_106X_upgrade2021_realistic_v4-v1/20000/C2FD7B09-F941-BD42-AB29-C3E4233A60A8.root',
            #'root://cmsxrootd.fnal.gov///store/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/PU25ns_106X_upgrade2021_realistic_v4-v1/20000/1B8D20FE-65FD-484E-9591-B5EF9025F64A.root',
            #'root://cmsxrootd.fnal.gov///store/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/PU25ns_106X_upgrade2021_realistic_v4-v1/20000/B8C949D2-75D7-EC40-A0AF-6E8CE5B636C5.root',
            #'root://cmsxrootd.fnal.gov///store/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/PU25ns_106X_upgrade2021_realistic_v4-v1/20000/29C59DF4-E379-8A46-9225-4AD096E34B2D.root',
            #'root://cmsxrootd.fnal.gov///store/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/PU25ns_106X_upgrade2021_realistic_v4-v1/20000/7728EE99-30F5-5745-9399-B571D5A9C1A0.root',
            #'root://cmsxrootd.fnal.gov///store/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/PU25ns_106X_upgrade2021_realistic_v4-v1/20000/1E7FF9EC-E676-514B-B596-14EFF93459DC.root',
            #'root://cmsxrootd.fnal.gov///store/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/PU25ns_106X_upgrade2021_realistic_v4-v1/20000/3ADC0D8C-F124-4C42-8256-9DABA8E18B4B.root',
            #'root://cmsxrootd.fnal.gov///store/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/PU25ns_106X_upgrade2021_realistic_v4-v1/20000/9D396CD1-6877-1C45-818C-065F0DCC6679.root',
            #'root://cmsxrootd.fnal.gov///store/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/PU25ns_106X_upgrade2021_realistic_v4-v1/20000/20ABB548-20CD-C747-9651-2B866BD26CC3.root',
            #'root://cmsxrootd.fnal.gov///store/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/PU25ns_106X_upgrade2021_realistic_v4-v1/20000/D8AB293D-0A3C-1E43-B298-B0A0D8A6A0D2.root',
            #'root://cmsxrootd.fnal.gov///store/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/PU25ns_106X_upgrade2021_realistic_v4-v1/20000/0B463A31-161D-584F-A6DA-B16E38A84688.root',
            #'root://cmsxrootd.fnal.gov///store/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/PU25ns_106X_upgrade2021_realistic_v4-v1/20000/83A2AB7B-63D0-5B4A-A179-83E0C80F00D5.root',
            #'root://cmsxrootd.fnal.gov///store/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/PU25ns_106X_upgrade2021_realistic_v4-v1/20000/E77229CD-490D-C44A-B74B-E83A8080377E.root',
            #'root://cmsxrootd.fnal.gov///store/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/PU25ns_106X_upgrade2021_realistic_v4-v1/20000/58998776-8BED-7242-A91F-F14DC8307A91.root',
            #'root://cmsxrootd.fnal.gov///store/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/PU25ns_106X_upgrade2021_realistic_v4-v1/20000/A39EE7C2-4D29-F346-9449-5D67A69C67CF.root',
            #'root://cmsxrootd.fnal.gov///store/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/PU25ns_106X_upgrade2021_realistic_v4-v1/20000/10149E52-5B6C-CE4A-8FAD-9BA2DF4E48BC.root',
            #'root://cmsxrootd.fnal.gov///store/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/PU25ns_106X_upgrade2021_realistic_v4-v1/20000/D7D9FE11-43DD-0045-936B-0FAAFA5525F7.root',
            #'root://cmsxrootd.fnal.gov///store/relval/CMSSW_10_6_0_pre4/RelValTTbar_13/GEN-SIM-DIGI-RAW/PU25ns_106X_upgrade2021_realistic_v4-v1/20000/8B4A80CD-AFF2-0B42-9E72-2D4FAB0D88C5.root',
        ),
        secondaryFileNames = cms.untracked.vstring(),
    )

else:
    process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring('%s'%(inputFile),),
        secondaryFileNames = cms.untracked.vstring(),
    )

#process.source.eventsToProcess = cms.untracked.VEventRange(cms.EventRange("1:2904-1:2904"),)

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('analyze nevts:-1'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
if "MC" in run:
    if era == "Run2":
        process.GlobalTag = GlobalTag(process.GlobalTag, '102X_upgrade2018_realistic_v12', '')
    elif era == "Run3":
        process.GlobalTag = GlobalTag(process.GlobalTag, '106X_upgrade2021_realistic_v4', '')
else:
    process.GlobalTag = GlobalTag(process.GlobalTag, '101X_dataRun2_Prompt_v11', '')

process.startjob = cms.Path(                                                   
  process.hcalDigis*                                                                        
#  process.RawToDigi*                                                                        
  process.hfprereco*
  process.hfreco*
  process.hbheprereco

)
# Path and EndPath definitions
#process.raw2digi_step = cms.Path(process.RawToDigi)
process.endjob_step = cms.EndPath(process.endOfProcess)

# Schedule definition
process.schedule = cms.Schedule(process.startjob,process.endjob_step)      
#process.schedule = cms.Schedule(process.raw2digi_step,process.endjob_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# customisation of the process.

# Automatic addition of the customisation function from Debug.HcalDebug.customize
from Debug.HcalDebug.customize import use_data_reemul_tp,compare_raw_reemul_tp,compare_reemul_reco_sev9 

process =  use_data_reemul_tp(process)

#call to customisation function compare_raw_reemul_tp imported from Debug.HcalDebug.customize
process = compare_raw_reemul_tp(process)

#call to customisation function compare_reemul_reco_sev9 imported from Debug.HcalDebug.customize
process = compare_reemul_reco_sev9(process)

# End of customisation functions

process.TFileService.fileName=cms.string('hcalNtuple%s_%s.root'%(stub,PFA))
# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
