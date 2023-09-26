# Web EPD

webepd - Web E-Paper Display is a utility that allows capturing images or screenshots of web pages and displaying them on E-Paper displays. The tool can perform the following:
- browse to a web page, take a screenshot, and display it on e-paper
- browse to a URL that points directly to an image file (e.g. jpg), download it, and display it on an e-paper
- display a local image file on an e-paper display

Also included is a utility which displays today's newspaper covers on E-paper displays. Only IT8951 based displays are supported at this time.

## Supported displays
- IT8951 driven displays
- Waveshare EPD 7.5 in V2

## Installation
```SHELL
pip install -r requirements.txt
sudo apt install chromium-browser chromium-codecs-ffmpeg
```

## Examples
```SHELL
# display the New York Times front page on an IT8951 display
python display_image_it8951.py -r CCW -w 1404 -t 1872 -url 'https://cdn.freedomforum.org/dfp/jpg26/lg/NY_NYT.jpg'
```

