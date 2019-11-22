#!/bin/bash

CODE=$1
SELECT=$2

NTUPLES="/store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/"
PROCESS=$3

SWITCH="$((2#${CODE}))"

if (( ${SWITCH}&(2**12) ))
then
    (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA2 ./input/Ratios/PFA2/${PROCESS}/TP > /dev/null 2>&1 &)
fi

if (( ${SELECT} == 0 ))
then
    # All PFA3p variations
    if (( ${SWITCH}&(2**0) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA3p_AVE ./input/Ratios/PFA3p/${PROCESS}/TP/NoDepth/AVE > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**1) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA3p_AVE_UP ./input/Ratios/PFA3p/${PROCESS}/TP/NoDepth/AVE/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**2) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA3p_AVE_DOWN ./input/Ratios/PFA3p/${PROCESS}/TP/NoDepth/AVE/Down > /dev/null 2>&1 &)
    fi
    
    if (( ${SWITCH}&(2**3) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA3p_PER_IETA ./input/Ratios/PFA3p/${PROCESS}/TP/NoDepth/ieta > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**4) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA3p_PER_IETA_UP ./input/Ratios/PFA3p/${PROCESS}/TP/NoDepth/ieta/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**5) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA3p_PER_IETA_DOWN ./input/Ratios/PFA3p/${PROCESS}/TP/NoDepth/ieta/Down > /dev/null 2>&1 &)
    fi
     
    if (( ${SWITCH}&(2**6) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA3p_DEPTH_AVE_AVE ./input/Ratios/PFA3p/${PROCESS}/TP/WithDepth/AVE > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**7) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA3p_DEPTH_AVE_AVE_UP ./input/Ratios/PFA3p/${PROCESS}/TP/WithDepth/AVE/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**8) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA3p_DEPTH_AVE_AVE_DOWN ./input/Ratios/PFA3p/${PROCESS}/TP/WithDepth/AVE/Down > /dev/null 2>&1 &)
    fi
     
    if (( ${SWITCH}&(2**9) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA3p_DEPTH_AVE_PER_IETA ./input/Ratios/PFA3p/${PROCESS}/TP/WithDepth/ieta > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**10) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA3p_DEPTH_AVE_PER_IETA_UP ./input/Ratios/PFA3p/${PROCESS}/TP/WithDepth/ieta/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**11) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA3p_DEPTH_AVE_PER_IETA_DOWN ./input/Ratios/PFA3p/${PROCESS}/TP/WithDepth/ieta/Down > /dev/null 2>&1 &)
    fi
else

    # All PFA1p variations
    if (( ${SWITCH}&(2**0) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA1p_AVE ./input/Ratios/PFA1p/${PROCESS}/TP/NoDepth/AVE > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**1) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA1p_AVE_UP ./input/Ratios/PFA1p/${PROCESS}/TP/NoDepth/AVE/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**2) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA1p_AVE_DOWN ./input/Ratios/PFA1p/${PROCESS}/TP/NoDepth/AVE/Down > /dev/null 2>&1 &)
    fi
    
    if (( ${SWITCH}&(2**3) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA1p_PER_IETA ./input/Ratios/PFA1p/${PROCESS}/TP/NoDepth/ieta > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**4) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA1p_PER_IETA_UP ./input/Ratios/PFA1p/${PROCESS}/TP/NoDepth/ieta/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**5) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA1p_PER_IETA_DOWN ./input/Ratios/PFA1p/${PROCESS}/TP/NoDepth/ieta/Down > /dev/null 2>&1 &)
    fi
     
    if (( ${SWITCH}&(2**6) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA1p_DEPTH_AVE_AVE ./input/Ratios/PFA1p/${PROCESS}/TP/WithDepth/AVE > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**7) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA1p_DEPTH_AVE_AVE_UP ./input/Ratios/PFA1p/${PROCESS}/TP/WithDepth/AVE/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**8) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA1p_DEPTH_AVE_AVE_DOWN ./input/Ratios/PFA1p/${PROCESS}/TP/WithDepth/AVE/Down > /dev/null 2>&1 &)
    fi
     
    if (( ${SWITCH}&(2**9) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA1p_DEPTH_AVE_PER_IETA ./input/Ratios/PFA1p/${PROCESS}/TP/WithDepth/ieta > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**10) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA1p_DEPTH_AVE_PER_IETA_UP ./input/Ratios/PFA1p/${PROCESS}/TP/WithDepth/ieta/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**11) ))
    then
        (nohup python scripts/ratioStudyPlotter.py ${NTUPLES}/${PROCESS}/PFA1p_DEPTH_AVE_PER_IETA_DOWN ./input/Ratios/PFA1p/${PROCESS}/TP/WithDepth/ieta/Down > /dev/null 2>&1 &)
    fi
fi
