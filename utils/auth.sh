#!/bin/bash
### Give the logged user regular rights on the ocr-pipeline folder
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

AUTH_GROUP=`bash -c 'id -gn $SUDO_USER'`
AUTH_USER=`bash -c 'id -un $SUDO_USER'`

chown ${AUTH_USER}:${AUTH_GROUP} -R ${ROOT}
