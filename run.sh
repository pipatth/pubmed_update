#!/bin/bash
source /home/pi/proj/pubmed_update/.direnv/python-3.7.2/bin/activate
cd /home/pi/proj/pubmed_update
rm output*.txt
python pmed/pipeline.py UpdateCiteCountTask --LoadDataTask-include-nodata 0
