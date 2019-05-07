#!/bin/bash
export PUBMED_UPDATE_PATH=/home/pi/test_rvcap/pubmed_update
export PUBMED_VENV_PATH=/home/pi/test_rvcap/pubmed_update/env/bin/activate
source $PUBMED_VENV_PATH
cd $PUBMED_UPDATE_PATH
rm output*.txt
python pmed/pipeline.py UpdateCiteCountTask --GetLinksTask-only-sample 1 --LoadDataTask-include-nodata 1
