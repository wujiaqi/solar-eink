#!/bin/bash

cd "$(dirname "$0")"
source /home/wujiaqi/git/webepd/eink/bin/activate
python newspaper.py --min 60 --scale 1.25 -d 16
deactivate

