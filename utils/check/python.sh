#!/bin/bash
# Test of the python installation
#
source $(dirname $0)/../env.sh

python2 --version

PYTHONPATH=${ROOT}/src python2 ${CURRENT_DIR}/packages.py
if [ $? -ne 0 ]
then
    echo "Packages inclusion failed"
    nok
fi

ok