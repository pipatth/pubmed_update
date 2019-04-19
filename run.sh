#!/bin/bash
export PUBMED_UPDATE_PATH=/home/pi/proj/pubmed_update
export PUBMED_VENV_PATH=/home/pi/proj/pubmed_update/.direnv/python-3.7.2/bin/activate
source $PUBMED_VENV_PATH
cd $PUBMED_UPDATE_PATH
rm output*.txt
python pmed/pipeline.py UpdateCiteCountTask
