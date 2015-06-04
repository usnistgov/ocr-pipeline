#!/bin/bash
# Give the logged user regular rights on the ocr-pipeline folder
#
source $(dirname $0)/env.sh

AUTH_GROUP=`bash -c 'id -gn $SUDO_USER'`
AUTH_USER=`bash -c 'id -un $SUDO_USER'`

chown ${AUTH_USER}:${AUTH_GROUP} -R ${ROOT}
