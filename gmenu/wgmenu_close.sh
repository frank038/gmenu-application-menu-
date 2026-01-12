#!/bin/bash

thisdir=$(dirname "$0")
cd $thisdir

# the program must be launched by gmenu.sh for the following to work
kill -9 `pgrep -f "python3 ./gmenu.py"`

# wlrctl toplevel close title:Gmenu-1
