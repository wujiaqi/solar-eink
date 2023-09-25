import argparse
import logging
import time
from datetime import date, datetime

import display_image_it8951
import schedule

logging.basicConfig(level=logging.INFO)

FREEDOMFORUM_URL = 'https://cdn.freedomforum.org/dfp/jpg{date}/lg/{paper}.jpg'
PAPERS = [
    'CA_SFC',
    'CA_EBT',
    'CA_LAT',
    'NY_NYT',
    'MN_ST',
    'WI_PC',
    'MA_BG',
    'IL_CT'
]
DEFAULT_PAPER = 'NY_NYT'

class NewspaperUrl:
    def __init__(self, papers):
        self.papers = papers
        self.paper = iter(self.papers)

    def getNextNewspaperUrl(self):
        now = datetime.now()
        # paper = PAPERS[now.hour] if now.hour in PAPERS else DEFAULT_PAPER
        try:
            paper_selection = next(self.paper)
        except StopIteration:
            self.paper = iter(self.papers)
            paper_selection = next(self.paper)
            
        return FREEDOMFORUM_URL.format(date=now.day, paper=paper_selection)
        

def parse_args():
    p = argparse.ArgumentParser(description='Display a list of newspaper front pages from freedom forum')
    p.add_argument('-v', '--virtual', action='store_true',
                   help='display using a Tkinter window instead of the '
                        'actual e-paper device (for testing without a '
                        'physical device)')
    p.add_argument('-w', '--width', type=int, required=True)
    p.add_argument('-t', '--height', type=int, required=True)
    p.add_argument('-f', '--fill', action='store_true', help='if set, fills entire frame with image with cropping')
    group = p.add_mutually_exclusive_group()
    group.add_argument('--sec', type=int, help="set period for update in seconds")
    group.add_argument('--min', type=int, help="set period for update in minutes")
    return p.parse_args()

def create_job(width, height, virtual, mirror, rotate, fill):
    newspaper = NewspaperUrl(PAPERS)
    def jobfunc():
        logging.info("running job...")
        url = newspaper.getNextNewspaperUrl()
        logging.info("Newspaper url {}".format(url))
        display_image_it8951.do_imgurl_display(url,width, height, virtual, rotate, mirror, fill)
        
    return jobfunc
    
def main():
    args = parse_args()

    if not args.min and not args.sec:
        create_job(args.width, args.height, args.virtual, True, "CCW", args.fill)()
    else:
        if args.min:
            schedule.every(args.min).minutes.do(create_job(args.width, args.height, args.virtual, True, "CCW", args.fill))
        elif args.sec:
            schedule.every(args.sec).seconds.do(create_job(args.width, args.height, args.virtual, True, "CCW", args.fill))

        logging.info("Starting job runs")
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Ctrl + c, exiting...")
            schedule.clear()
            exit()

if __name__ == '__main__':
    main()

