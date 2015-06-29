#!/bin/bash
### Test that the xvfb-run command is present
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
TMP_DIRNAME=`get_value_for_key dirs/temp` || nok
TMP_DIR="${ROOT}/${TMP_DIRNAME}"
XVFB_FILE=${TMP_DIR}/xvfb.test
XVFB_MSG="xvfb"

xvfb-run -a echo ${XVFB_MSG} > ${XVFB_FILE} 2>/dev/null
if [ `cat ${XVFB_FILE} | grep ${XVFB_MSG} | wc -l` -ne 0 ]
then
    rm ${XVFB_FILE}
    ok
else
    rm ${XVFB_FILE}
    nok
fi