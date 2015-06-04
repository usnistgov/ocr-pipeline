#!/bin/bash
# Wrap the pipeline in a terminal multiplexer (to avoid using nohup, which doesn't work with fabric)
#
if [ `tmux has-session -t pipeline 2>/dev/null; echo $?` -ne 0 ]
then
    tmux new -d -s pipeline
else
    tmux new-window -t pipeline
fi

# Send the pipeline command and ensure that it closes the tmux-window on exit
tmux send -t pipeline "bash -c '$(dirname $0)/run.sh $*'; exit" Enter
