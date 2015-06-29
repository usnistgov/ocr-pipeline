#!/bin/bash
### Test of the python installation
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
source $(dirname $0)/../env.sh

python2 --version

PYTHONPATH=${ROOT}/src python2 ${CURRENT_DIR}/packages.py
if [ $? -ne 0 ]
then
    echo "Packages inclusion failed"
    nok
fi

ok