#!/bin/bash
# Testing ocropy
#
source $(dirname $0)/../env.sh
TMP_DIRNAME=`get_value_for_key dirs/temp` || nok
TMP_DIR="${ROOT}/${TMP_DIRNAME}"
OCROPY_DIR=`get_value_for_key commands/list#1/PNGReader/ocropy/location` || nok

ocropy_check_file="${OCROPY_DIR}/tests/testpage.png"

echo "[1/4] Checking directory existence..."
if [ ! -d "${OCROPY_DIR}" ]
then
    echo "Resource has not been downloaded"
    nok
fi

echo "[2/4] Checking ocropus-nlbin..."
python2 ${OCROPY_DIR}/ocropus-nlbin ${ocropy_check_file} -o ${TMP_DIR} 2>&1 >/dev/null
if [ $? -ne 0 ]
then
    echo "ocropus-nlbin command failed"
    nok
fi

echo "[3/4] Checking ocropus-gpageseg..."
python2 ${OCROPY_DIR}/ocropus-gpageseg ${TMP_DIR}/*.bin.png 2>&1 >/dev/null
if [ $? -ne 0 ]
then
    echo "ocropus-gpageseg command failed"
    nok
fi

echo "[4/4] Checking ocropus-rpred..."
python2 ${OCROPY_DIR}/ocropus-rpred -n ${TMP_DIR}/*/*.bin.png 2>&1 >/dev/null
if [ $? -ne 0 ]
then
    echo "ocropus-rpred command failed"
    nok
fi

ok