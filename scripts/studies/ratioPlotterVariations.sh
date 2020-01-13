#!/bin/bash

CODE=$1
SELECT=$2
PROCESS=$3

INPUTDIR="${PROCESS}"

SWITCH="$((2#${CODE}))"

SCRIPTDIR="${HOME}/nobackup/HCAL_Trigger_Study/scripts/studies"

COMMAND=""

if (( ${SWITCH}&(2**12) ))
then
    if (( ${SELECT} == 0 ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA2 PFA2/${PROCESS} > /dev/null 2>&1 &)"
    fi
    if (( ${SELECT} == 1 ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1 PFA1/${PROCESS} > /dev/null 2>&1 &)"
    fi
fi

if (( ${SELECT} == 0 ))
then
    ALGOSTUB="PFA2p/${PROCESS}"

    # All PFA2p variations
    if (( ${SWITCH}&(2**0) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA2p_AVE ${ALGOSTUB}/NoDepth/AVE > /dev/null 2>&1 &)"
    fi
    if (( ${SWITCH}&(2**1) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA2p_AVE_UP ${ALGOSTUB}/NoDepth/AVE/Up > /dev/null 2>&1 &)"
    fi
    if (( ${SWITCH}&(2**2) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA2p_AVE_DOWN ${ALGOSTUB}/NoDepth/AVE/Down > /dev/null 2>&1 &)"
    fi
    
    if (( ${SWITCH}&(2**3) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA2p_PER_IETA ${ALGOSTUB}/NoDepth/ieta > /dev/null 2>&1 &)"
    fi
    if (( ${SWITCH}&(2**4) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA2p_PER_IETA_UP ${ALGOSTUB}/NoDepth/ieta/Up > /dev/null 2>&1 &)"
    fi
    if (( ${SWITCH}&(2**5) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA2p_PER_IETA_DOWN ${ALGOSTUB}/NoDepth/ieta/Down > /dev/null 2>&1 &)"
    fi
     
    if (( ${SWITCH}&(2**6) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA2p_DEPTH_AVE_AVE ${ALGOSTUB}/WithDepth/AVE > /dev/null 2>&1 &)"
    fi
    if (( ${SWITCH}&(2**7) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA2p_DEPTH_AVE_AVE_UP ${ALGOSTUB}/WithDepth/AVE/Up > /dev/null 2>&1 &)"
    fi
    if (( ${SWITCH}&(2**8) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA2p_DEPTH_AVE_AVE_DOWN ${ALGOSTUB}/WithDepth/AVE/Down > /dev/null 2>&1 &)"
    fi
     
    if (( ${SWITCH}&(2**9) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA2p_DEPTH_AVE_PER_IETA ${ALGOSTUB}/WithDepth/ieta > /dev/null 2>&1 &)"
    fi
    if (( ${SWITCH}&(2**10) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA2p_DEPTH_AVE_PER_IETA_UP ${ALGOSTUB}/WithDepth/ieta/Up > /dev/null 2>&1 &)"
    fi
    if (( ${SWITCH}&(2**11) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA2p_DEPTH_AVE_PER_IETA_DOWN ${ALGOSTUB}/WithDepth/ieta/Down > /dev/null 2>&1 &)"
    fi
else

    ALGOSTUB="PFA1p/${PROCESS}"

    # All PFA1p variations
    if (( ${SWITCH}&(2**0) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_AVE ${ALGOSTUB}/NoDepth/AVE > /dev/null 2>&1 &)"
    fi
    if (( ${SWITCH}&(2**1) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_AVE_UP ${ALGOSTUB}/NoDepth/AVE/Up > /dev/null 2>&1 &)"
    fi
    if (( ${SWITCH}&(2**2) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_AVE_DOWN ${ALGOSTUB}/NoDepth/AVE/Down > /dev/null 2>&1 &)"
    fi
    
    if (( ${SWITCH}&(2**3) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_PER_IETA ${ALGOSTUB}/NoDepth/ieta > /dev/null 2>&1 &)"
    fi
    if (( ${SWITCH}&(2**4) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_PER_IETA_UP ${ALGOSTUB}/NoDepth/ieta/Up > /dev/null 2>&1 &)"
    fi
    if (( ${SWITCH}&(2**5) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_PER_IETA_DOWN ${ALGOSTUB}/NoDepth/ieta/Down > /dev/null 2>&1 &)"
    fi
     
    if (( ${SWITCH}&(2**6) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_DEPTH_AVE_AVE ${ALGOSTUB}/WithDepth/AVE > /dev/null 2>&1 &)"
    fi
    if (( ${SWITCH}&(2**7) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_DEPTH_AVE_AVE_UP ${ALGOSTUB}/WithDepth/AVE/Up > /dev/null 2>&1 &)"
    fi
    if (( ${SWITCH}&(2**8) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_DEPTH_AVE_AVE_DOWN ${ALGOSTUB}/WithDepth/AVE/Down > /dev/null 2>&1 &)"
    fi
     
    if (( ${SWITCH}&(2**9) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_DEPTH_AVE_PER_IETA ${ALGOSTUB}/WithDepth/ieta > /dev/null 2>&1 &)"
    fi
    if (( ${SWITCH}&(2**10) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_DEPTH_AVE_PER_IETA_UP ${ALGOSTUB}/WithDepth/ieta/Up > /dev/null 2>&1 &)"
    fi
    if (( ${SWITCH}&(2**11) ))
    then
        COMMAND="(nohup python ${SCRIPTDIR}/ratioStudyPlotter.py ${INPUTDIR}/PFA1p_DEPTH_AVE_PER_IETA_DOWN ${ALGOSTUB}/WithDepth/ieta/Down > /dev/null 2>&1 &)"
    fi
fi

echo "We are executing: $COMMAND"
eval $COMMAND
