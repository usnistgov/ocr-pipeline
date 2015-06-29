#!/bin/bash
### Script interacting w/ the pipeline. Same script work for remote and local access.
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
source $(dirname $0)/utils/env.sh

contains() {
    local element

    for element in "${@:2}"
    do
        if [ "$element" == "$1" ]
        then
            echo 0
            return
        fi
    done

    echo 1
}

local_opts=("-l" "--local")
remote_opts=("-r" "--remote")

# Store arguments in another variable to manipulate them easily
args=($*)

if [ `contains "$1" "${local_opts[@]}"` -eq 0 ]
then
    # Local execution
    args=("${args[@]:1}")
    python2 ui.py ${args[@]} 2>&1
elif [ `contains "$1" "${remote_opts[@]}"` -eq 0 ]
then
    # Remote execution
    args=("${args[@]:1}")

    command=${args[0]}
    args=("${args[@]:1}")

    # Building argument string
    arg_count=${#args[@]}
    args_str=""

    if [ ${arg_count} -ne 0 ]
    then
        arg_index=1
        args_str=":"

        for arg in ${args[@]}
        do
            args_str=${args_str}${arg}

            if [ ${arg_index} -ne ${arg_count} ]
            then
                args_str=${args_str}","
            fi

            (( arg_index++ ))
        done
    fi

    # Deployment command
    fab -f ui.py ${command}${args_str} 2>&1
else
    # By default, app is executed locally
    python2 ui.py ${args[@]} 2>&1
fi