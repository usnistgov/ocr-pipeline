#!/bin/bash
# Start a slave or a master on the local machine
#
source $(dirname $0)/env.sh

xvfb-run -a python2 ${ROOT}/utils/run.py $* 2>&1
