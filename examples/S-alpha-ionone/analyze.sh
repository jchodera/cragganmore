#!/bin/tcsh

#setenv YANKHOME ${HOME}/yank/yank.choderalab
setenv YANKHOME ${HOME}/anaconda/lib/python2.7/site-packages

# Run in serial mode.
python ${YANKHOME}/yank/analyze.py
