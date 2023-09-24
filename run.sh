#!/bin/bash

now=$(date)
echo "${now}: Starting cron run..."
cd "$(dirname "$0")"
/usr/bin/python display_eink_image.py -u 'https://grafana.jiaqiwu.io/d/sPcihT2Vk/solar-e-ink?orgId=1&kiosk' -w 800 -t 480

