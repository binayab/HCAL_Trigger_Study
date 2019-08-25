#!/usr/bin/bash

HADDAREA=$1

cd $HADDAREA && rm histoCache.root && hadd histoCache.root histo* && cd - 
