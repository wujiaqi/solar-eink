#!/bin/bash

now=$(date)
source /home/wujiaqi/git/webepd/eink/bin/activate
echo "${now}: Starting cron run..."
cd "$(dirname "$0")"
python display_eink_image.py -u 'https://grafana.jiaqiwu.io/d/sPcihT2Vk/solar-e-ink?orgId=1&kiosk'
deactivate

