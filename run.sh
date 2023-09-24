#!/bin/bash

now=$(date)
echo "${now}: Starting cron run..."
cd "$(dirname "$0")"
/usr/bin/node capture_solar_grafana.js -w 800 -h 600 -u "https://grafana.jiaqiwu.io/d/sPcihT2Vk/solar-e-ink?orgId=1&kiosk"
/usr/bin/python display_eink_image.py
rm screenshot.png

