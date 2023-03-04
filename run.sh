#!/bin/bash

cd "$(dirname "$0")"
/usr/bin/node capture_solar_grafana.js
/usr/bin/python display_eink_image.py
rm screenshot.png

