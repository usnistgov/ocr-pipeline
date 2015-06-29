#!/bin/bash
### Wrap the pipeline in a terminal multiplexer (to avoid using nohup, which doesn't work with fabric)
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
if [ `tmux has-session -t pipeline 2>/dev/null; echo $?` -ne 0 ]
then
    tmux new -d -s pipeline
else
    tmux new-window -t pipeline
fi

# Send the pipeline command and ensure that it closes the tmux-window on exit
tmux send -t pipeline "bash -c '$(dirname $0)/run.sh $*'; exit" Enter
