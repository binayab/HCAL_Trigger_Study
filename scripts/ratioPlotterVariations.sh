#!/bin/bash

CODE=$1
SELECT=$2

SWITCH="$((2#${CODE}))"

(nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA2 ./input/Ratios/PFA2/store/TP > /dev/null 2>&1 &)

if (( ${SELECT} == 0 ))
then
    # All PFA3p variations
    if (( ${SWITCH}&(2**0) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA3p_AVE ./input/Ratios/PFA3p/store/TP/NoDepth/AVE > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**1) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA3p_AVE_UP ./input/Ratios/PFA3p/store/TP/NoDepth/AVE/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**2) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA3p_AVE_DOWN ./input/Ratios/PFA3p/store/TP/NoDepth/AVE/Down > /dev/null 2>&1 &)
    fi
    
    if (( ${SWITCH}&(2**4) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA3p_PER_IETA ./input/Ratios/PFA3p/store/TP/NoDepth/ieta > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**5) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA3p_PER_IETA_UP ./input/Ratios/PFA3p/store/TP/NoDepth/ieta/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**6) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA3p_PER_IETA_DOWN ./input/Ratios/PFA3p/store/TP/NoDepth/ieta/Down > /dev/null 2>&1 &)
    fi
     
    if (( ${SWITCH}&(2**8) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA3p_DEPTH_AVE_AVE ./input/Ratios/PFA3p/store/TP/WithDepth/AVE > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**9) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA3p_DEPTH_AVE_AVE_UP ./input/Ratios/PFA3p/store/TP/WithDepth/AVE/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**10) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA3p_DEPTH_AVE_AVE_UP ./input/Ratios/PFA3p/store/TP/WithDepth/AVE/Down > /dev/null 2>&1 &)
    fi
     
    if (( ${SWITCH}&(2**12) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA3p_DEPTH_AVE_PER_IETA ./input/Ratios/PFA3p/store/TP/WithDepth/ieta > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**13) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA3p_DEPTH_AVE_PER_IETA ./input/Ratios/PFA3p/store/TP/WithDepth/ieta/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**14) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA3p_DEPTH_AVE_PER_IETA ./input/Ratios/PFA3p/store/TP/WithDepth/ieta/Down > /dev/null 2>&1 &)
    fi
else

    # All PFA1p variations
    if (( ${SWITCH}&(2**0) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA1p_AVE ./input/Ratios/PFA1p/store/TP/NoDepth/AVE > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**1) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA1p_AVE_UP ./input/Ratios/PFA1p/store/TP/NoDepth/AVE/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**2) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA1p_AVE_DOWN ./input/Ratios/PFA1p/store/TP/NoDepth/AVE/Down > /dev/null 2>&1 &)
    fi
    
    if (( ${SWITCH}&(2**4) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA1p_PER_IETA ./input/Ratios/PFA1p/store/TP/NoDepth/ieta > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**5) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA1p_PER_IETA_UP ./input/Ratios/PFA1p/store/TP/NoDepth/ieta/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**6) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA1p_PER_IETA_DOWN ./input/Ratios/PFA1p/store/TP/NoDepth/ieta/Down > /dev/null 2>&1 &)
    fi
     
    if (( ${SWITCH}&(2**8) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA1p_DEPTH_AVE_AVE ./input/Ratios/PFA1p/store/TP/WithDepth/AVE > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**9) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA1p_DEPTH_AVE_AVE_UP ./input/Ratios/PFA1p/store/TP/WithDepth/AVE/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**10) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA1p_DEPTH_AVE_AVE_UP ./input/Ratios/PFA1p/store/TP/WithDepth/AVE/Down > /dev/null 2>&1 &)
    fi
     
    if (( ${SWITCH}&(2**12) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA1p_DEPTH_AVE_PER_IETA ./input/Ratios/PFA1p/store/TP/WithDepth/ieta > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**13) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA1p_DEPTH_AVE_PER_IETA ./input/Ratios/PFA1p/store/TP/WithDepth/ieta/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**14) ))
    then
        (nohup python scripts/ratioStudyPlotter.py /store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/store/PFA1p_DEPTH_AVE_PER_IETA ./input/Ratios/PFA1p/store/TP/WithDepth/ieta/Down > /dev/null 2>&1 &)
    fi
fi
