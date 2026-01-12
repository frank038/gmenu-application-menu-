#!/bin/bash

thisdir=$(dirname "$0")
cd $thisdir

if ! pgrep -f gmenu.py; then
    ./gmenu.sh &
fi

if wlrctl toplevel find title:Gmenu-1 state:unminimized; then
    wlrctl toplevel minimize title:Gmenu-1 state:unminimized
elif wlrctl toplevel find title:Gmenu-1 state:minimized; then
    wlrctl toplevel focus title:Gmenu-1 state:minimized
fi
