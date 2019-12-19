#!/bin/bash

CODE=$1
SELECT=$2

NTUPLES="/eos/uscms/store/user/jhiltbra/HCAL_Trigger_Study/hcalNtuples/"
PROCESS=$3

INPUTDIR="${NTUPLES}/${PROCESS}"

SWITCH="$((2#${CODE}))"

SCRIPTDIR="${HOME}/nobackup/HCAL_Trigger_Study/scripts"
OUTBASE="${HOME}/nobackup/HCAL_Trigger_Study/input/Ratios"

if (( ${SWITCH}&(2**12) ))
then
    (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA2 ${OUTBASE}/PFA2/${PROCESS}/TP > /dev/null 2>&1 &)
fi

if (( ${SELECT} == 0 ))
then
    ALGOSTUB="${OUTBASE}/PFA3p/${PROCESS}/TP"

    # All PFA3p variations
    if (( ${SWITCH}&(2**0) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA3p_AVE ${ALGOSTUB}/NoDepth/AVE > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**1) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA3p_AVE_UP ${ALGOSTUB}/NoDepth/AVE/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**2) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA3p_AVE_DOWN ${ALGOSTUB}/NoDepth/AVE/Down > /dev/null 2>&1 &)
    fi
    
    if (( ${SWITCH}&(2**3) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA3p_PER_IETA ${ALGOSTUB}/NoDepth/ieta > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**4) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA3p_PER_IETA_UP ${ALGOSTUB}/NoDepth/ieta/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**5) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA3p_PER_IETA_DOWN ${ALGOSTUB}/NoDepth/ieta/Down > /dev/null 2>&1 &)
    fi
     
    if (( ${SWITCH}&(2**6) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA3p_DEPTH_AVE_AVE ${ALGOSTUB}/WithDepth/AVE > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**7) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA3p_DEPTH_AVE_AVE_UP ${ALGOSTUB}/WithDepth/AVE/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**8) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA3p_DEPTH_AVE_AVE_DOWN ${ALGOSTUB}/WithDepth/AVE/Down > /dev/null 2>&1 &)
    fi
     
    if (( ${SWITCH}&(2**9) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA3p_DEPTH_AVE_PER_IETA ${ALGOSTUB}/WithDepth/ieta > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**10) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA3p_DEPTH_AVE_PER_IETA_UP ${ALGOSTUB}/WithDepth/ieta/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**11) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA3p_DEPTH_AVE_PER_IETA_DOWN ${ALGOSTUB}/WithDepth/ieta/Down > /dev/null 2>&1 &)
    fi
else

    ALGOSTUB="${OUTBASE}/PFA1p/${PROCESS}/TP"

    # All PFA1p variations
    if (( ${SWITCH}&(2**0) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_AVE ${ALGOSTUB}/NoDepth/AVE > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**1) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_AVE_UP ${ALGOSTUB}/NoDepth/AVE/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**2) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_AVE_DOWN ${ALGOSTUB}/NoDepth/AVE/Down > /dev/null 2>&1 &)
    fi
    
    if (( ${SWITCH}&(2**3) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_PER_IETA ${ALGOSTUB}/NoDepth/ieta > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**4) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_PER_IETA_UP ${ALGOSTUB}/NoDepth/ieta/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**5) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_PER_IETA_DOWN ${ALGOSTUB}/NoDepth/ieta/Down > /dev/null 2>&1 &)
    fi
     
    if (( ${SWITCH}&(2**6) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_DEPTH_AVE_AVE ${ALGOSTUB}/WithDepth/AVE > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**7) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_DEPTH_AVE_AVE_UP ${ALGOSTUB}/WithDepth/AVE/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**8) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_DEPTH_AVE_AVE_DOWN ${ALGOSTUB}/WithDepth/AVE/Down > /dev/null 2>&1 &)
    fi
     
    if (( ${SWITCH}&(2**9) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_DEPTH_AVE_PER_IETA ${ALGOSTUB}/WithDepth/ieta > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**10) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_DEPTH_AVE_PER_IETA_UP ${ALGOSTUB}/WithDepth/ieta/Up > /dev/null 2>&1 &)
    fi
    if (( ${SWITCH}&(2**11) ))
    then
        (nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_DEPTH_AVE_PER_IETA_DOWN ${ALGOSTUB}/WithDepth/ieta/Down > /dev/null 2>&1 &)
    fi
fi
