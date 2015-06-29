#!/bin/bash
### Start a slave or a master on the local machine
#
# Authors:
#   Philippe Dessauw
#   philippe.dessauw@nist.gov
#
# Sponsor:
#   Alden Dima
#   alden.dima@nist.gov
#   Information Systems Group
#   Software and Systems Division
#   Information Technology Laboratory
#   National Institute of Standards and Technology
#   http://www.nist.gov/itl/ssd/is
###
source $(dirname $0)/env.sh

xvfb-run -a python2 ${ROOT}/utils/run.py $* 2>&1
