import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras

import sys

sys.path.insert(0, "/uscms/home/jhiltb/nobackup/HCAL_Trigger_Study/scripts/")

from algo_weights import pfaWeightsMap

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

if PFA in pfaWeightsMap:
    print "Using weights: "
    print pfaWeightsMap[PFA]
    process.simHcalTriggerPrimitiveDigis.PeakFinderAlgorithmWeights = pfaWeightsMap[PFA] 
else:
    print "No weights defined for algo \"%s\"; defaulting to zero weights!"%(PFA)

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)

# Input source
if inputFile == "OOT":
    process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(
            'root://cmsxroot.fnal.gov//store/user/jhiltbra/HCAL_Trigger_Study/TTbar_RelVal/TTbar-DIGI-RAW-50PU-OOT1.root',
            'root://cmsxroot.fnal.gov//store/user/jhiltbra/HCAL_Trigger_Study/TTbar_RelVal/TTbar-DIGI-RAW-50PU-OOT2.root',
            'root://cmsxroot.fnal.gov//store/user/jhiltbra/HCAL_Trigger_Study/TTbar_RelVal/TTbar-DIGI-RAW-50PU-OOT3.root',
    
        ),
        secondaryFileNames = cms.untracked.vstring(),
    )
elif inputFile == "NOPU":
    process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(
            'root://cmsxrootd.fnal.gov//store/user/jhiltbra/HCAL_Trigger_Study/TTbar_RelVal/TTbar-DIGI-RAW-0PU123.root',
        ),
        secondaryFileNames = cms.untracked.vstring(),
    )

elif inputFile == "50PU": 
    process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(
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

            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/043D2BF4-43C5-614F-BD81-D3C88968DD54.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/0FD371C3-32CA-6F4B-BCF4-013E0E73E988.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/1E38A61E-9906-6C4C-A286-524E5A59FB08.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/2AB2AC8F-C73A-0E42-8273-5FC1DC8C51E1.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/31958CF2-326B-6147-A06B-E51D7F493A33.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/31A48641-DF74-E244-970A-A69360E555E5.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/3FEE5DBF-DBDB-354E-9621-511A6908B009.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/56CE3E5D-6B17-9848-850B-B64142220B27.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/61FCF587-60D7-534A-8840-42C5736DD89D.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/64CD68F1-F9DE-554A-A997-BC4C2D1D3555.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/65E41851-B549-B24C-936A-040D5E0FB438.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/72978C5E-F4AC-ED4A-AD24-0CEEEB914300.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/79337207-D3E7-1A4A-8ECB-78ACBA3EFC43.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/9D068ED9-57BA-374A-99B4-188A8B017283.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/9D73926A-B466-004C-ABBD-50747ABE5565.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/9D922D01-3F40-314C-B50C-BB63B3B7A32F.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/AF74BABA-08FF-7D44-A577-A3C29343DD15.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/C756B891-8A34-EE43-B927-71806654289A.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/D24BCD6F-D41B-8143-AFB3-A6205999FD12.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/D8F3426D-B596-7B49-95D0-3C854169407C.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/DF4E49C7-1447-AF43-A86C-170AB21A8384.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/E727ABB5-7B1D-D74B-9D4B-682D5230388D.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/EEFEF44C-05F0-874B-B69D-C1F19A5AC94C.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/F68D0E05-BE8A-3344-9A65-33091666B3EE.root',
            'root://cmsxrootd.fnal.gov///store/user/jhiltbra/HCAL_Trigger_Study/Run3Summer19DR/TTbar_14TeV_TuneCP5_Pythia8/GEN-SIM-DIGI-RAW/106X_mcRun3_2021_realistic_v3-v2/130000/FDF31EC8-D103-AE49-B3CA-9E58F67C07F1.root',

        ),
        secondaryFileNames = cms.untracked.vstring(),
    )

else:
    process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring('%s'%(inputFile),),
        secondaryFileNames = cms.untracked.vstring(),
    )

#process.source.eventsToProcess = cms.untracked.VEventRange(cms.EventRange("1:2903-1:2903"),)

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
