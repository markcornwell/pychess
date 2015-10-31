#!/bin/bash
#
# -size medium works best with  xwin -screen 0 548 660 &
#
export DISPLAY=localhost:0.0
xwin -screen 0 548 660 & sleep 2
./xboard -debug -size medium -tc 120 -fcp mediate.py -scp mediate.py &
