#!/bin/bash
### Test the Redis installation
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
redis_check_file=${TMP_DIR}/redis.check

which redis-server > ${redis_check_file} 2>/dev/null
if [ `cat ${redis_check_file} | wc -l` -ne 1 ] || [ ! -e `cat ${redis_check_file}` ]
then
    rm ${redis_check_file}
    nok
fi

redis-cli --version | cut -d' ' -f2 > ${redis_check_file} 2>/dev/null

if [ `cat ${redis_check_file} | cut -d'.' -f1` -eq 2 ]
then
    if [ `cat ${redis_check_file} | cut -d'.' -f2` -lt 6 ]
    then
        rm ${redis_check_file}
        nok
    fi
else
    rm ${redis_check_file}
    nok
fi

#REDIS_SERVER=`get_value_for_key machines/master#0` || nok
REDIS_SERVER=`get_value_for_key redis/host` || nok
REDIS_PORT=`get_value_for_key redis/port` || nok

redis-cli -h ${REDIS_SERVER} -p ${REDIS_PORT} ping > ${redis_check_file}
if [ `cat ${redis_check_file}` != "PONG" ]
then
    rm ${redis_check_file}
    nok
else
    rm ${redis_check_file}
    ok
fi