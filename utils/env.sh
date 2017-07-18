#!/bin/bash
### Store basic information about the environment
#
# Can be called from any script using:
#   >   source path/to/env.sh
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

# Defining fonctions
function parse_yaml {
    local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @|tr @ '\034')

    sed -ne "s|^\($s\)\($w\)$s:$s\"\(.*\)\"$s\$|\1$fs\2$fs\3|p" \
    -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p" $1 |
    awk -F$fs '{
        indent = length($1)/4;
        vname[indent] = $2;

        for (i in vname) {if (i > indent) {delete vname[i]}}
            if (length($3) > 0) {
            vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
            printf("%s%s=\"%s\"\n", vn, $2, $3);
        }
    }'
}

function get_value_for_key {
    local file=${CONF_FILE} key=$1
    python2 ${DIR}/config.py ${file} ${key}
}

function nok {
    echo "NOK"
    exit 1
}

function ok {
    echo "OK"
    exit 0
}

# Setting up main variables
DIR=`echo $(cd -P $(dirname ${BASH_SOURCE[0]}) && pwd)`
export ROOT="${DIR}/.."
CONF_FILE="${ROOT}/conf/app.yaml"
ENV_CONF_FILE="${ROOT}/conf/env.yaml"
TMP_CONF_FILE="/tmp/env.conf"

# Turning on the python environment
parse_yaml ${ENV_CONF_FILE} > ${TMP_CONF_FILE}
source ${TMP_CONF_FILE}
rm ${TMP_CONF_FILE}

# If a python path has been setup and is a directory
#if [ -d "${python_path}" ]
#then
#    export PATH=${python_path}/bin:$PATH
#else
#    if [ -n "${python_path}" ]
#    then
#        echo "${python_path} is not a valid directory"
#        nok
#    fi
#fi
#
## If a python environment has been setup and is a directory
#if [ -d "${python_virtualenv}" ]
#then
#    current_python_env=`python ${ROOT}/utils/prefix.py`
#
#    if [ ${current_python_env} != ${python_virtualenv} ]
#    then
#        source activate ${python_virtualenv} &>/dev/null
#    fi
#else
#    if [ -n "${python_virtualenv}" ]
#    then
#        echo "${python_virtualenv} is not a valid directory"
#        nok
#    fi
#fi

# Useful variables
CURRENT_DIR=`echo $(cd -P $(dirname $0) && pwd)`

#TMP_DIRNAME=`get_value_for_key dirs/temp` || nok
#TMP_DIR="${ROOT}/${TMP_DIRNAME}"

