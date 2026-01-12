#!/bin/bash

thisdir=$(dirname "$0")
cd $thisdir

# if ! pgrep -f gmenu.py; then
if ! pgrep -f "python3 ./gmenu.py"; then
    ./gmenu.sh &
fi

WINDOW_ID=$(xdotool search --name "Gmenu-1")

WINDOW_STATE=$(xprop -id "$WINDOW_ID" \
| grep "_NET_WM_STATE(ATOM)" \
| grep "_NET_WM_STATE_HIDDEN")

if [[ -z "$WINDOW_STATE" ]]; then
        xdotool windowminimize "$WINDOW_ID"
elif [[ -n "$WINDOW_STATE" ]]; then
        xdotool windowmap "$WINDOW_ID"
        # xdotool windowraise "$WINDOW_ID"
fi
