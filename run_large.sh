#!/bin/bash

cd "$(dirname "$0")"
source /home/wujiaqi/eink2/bin/activate
python display_image_it8951.py -m -w 1872 -t 1404 -u "https://grafana.jiaqiwu.io/d/b9e923c7-27e4-47b4-a4ec-9ffde2002cab/solar-e-ink-large?orgId=1&kiosk"
deactivate

