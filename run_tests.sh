#!/bin/sh
echo "running RollerTest"
python3 -m unittest test.RollerTest
echo "running HandlerTest"
python3 -m unittest test.HandlerTest