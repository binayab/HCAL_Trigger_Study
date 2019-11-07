#!/bin/bash

DATASET=$1
CODE=$2
TOGGLE=$3

SWITCH="$((2#${CODE}))"

#python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA2

if (( ${TOGGLE} == 0 ))
then
    # All PFA3p variations
    if (( ${SWITCH}&(2**0) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA3p_AVE
    fi
    if (( ${SWITCH}&(2**1) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA3p_AVE_UP
    fi
    if (( ${SWITCH}&(2**2) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA3p_AVE_DOWN
    fi
    
    if (( ${SWITCH}&(2**4) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA3p_PER_IETA
    fi
    if (( ${SWITCH}&(2**5) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA3p_PER_IETA_UP
    fi
    if (( ${SWITCH}&(2**6) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA3p_PER_IETA_DOWN
    fi
     
    if (( ${SWITCH}&(2**8) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA3p_DEPTH_AVE_AVE
    fi
    if (( ${SWITCH}&(2**9) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA3p_DEPTH_AVE_AVE_UP
    fi
    if (( ${SWITCH}&(2**10) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA3p_DEPTH_AVE_AVE_DOWN
    fi
     
    if (( ${SWITCH}&(2**12) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA3p_DEPTH_AVE_PER_IETA
    fi
    if (( ${SWITCH}&(2**13) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA3p_DEPTH_AVE_PER_IETA_UP
    fi
    if (( ${SWITCH}&(2**14) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA3p_DEPTH_AVE_PER_IETA_DOWN
    fi
fi

if (( ${TOGGLE} == 1 ))
then

    # All PFA1p variations
    if (( ${SWITCH}&(2**0) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA1p_AVE
    fi
    if (( ${SWITCH}&(2**1) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA1p_AVE_UP
    fi
    if (( ${SWITCH}&(2**2) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA1p_AVE_DOWN
    fi
    
    if (( ${SWITCH}&(2**4) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA1p_PER_IETA
    fi
    if (( ${SWITCH}&(2**5) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA1p_PER_IETA_UP
    fi
    if (( ${SWITCH}&(2**6) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA1p_PER_IETA_DOWN
    fi
    
    if (( ${SWITCH}&(2**8) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA1p_DEPTH_AVE_AVE
    fi
    if (( ${SWITCH}&(2**9) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA1p_DEPTH_AVE_AVE_UP
    fi
    if (( ${SWITCH}&(2**10) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA1p_DEPTH_AVE_AVE_DOWN
    fi
    
    if (( ${SWITCH}&(2**12) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA1p_DEPTH_AVE_PER_IETA
    fi
    if (( ${SWITCH}&(2**13) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA1p_DEPTH_AVE_PER_IETA_UP
    fi
    if (( ${SWITCH}&(2**14) ))
    then
        python scripts/submitHcalTrigNtuple.py --dataset ${DATASET} --pfa PFA1p_DEPTH_AVE_PER_IETA_DOWN
    fi
fi
