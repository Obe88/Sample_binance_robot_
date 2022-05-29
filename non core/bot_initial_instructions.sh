#!/bin/sh
# A Bash script
# screen -S bot sudo -u python3 $1 run
sudo python3 -u $1 run
exec "$@"