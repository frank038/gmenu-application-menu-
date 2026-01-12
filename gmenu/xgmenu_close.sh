#!/bin/bash

thisdir=$(dirname "$0")
cd $thisdir

WINDOW_ID=$(xdotool search --name "Gmenu-1")
# xdotool windowclose "$WINDOW_ID"
xdotool windowkill "$WINDOW_ID"
