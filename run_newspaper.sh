#!/bin/bash

cd "$(dirname "$0")"
source /home/wujiaqi/git/eink/bin/activate
python newspaper.py --min 60 --scale 1.25
deactivate

