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
    return p.parse_args()

def create_job(width, height, virtual, mirror, rotate):
    newspaper = NewspaperUrl(PAPERS)
    def jobfunc():
        logging.info("running job...")
        url = newspaper.getNextNewspaperUrl()
        logging.info("Newspaper url {}".format(url))
        display_image_it8951.do_imgurl_display(newspaper.getNextNewspaperUrl(),width, height, virtual, rotate, mirror)
        
    return jobfunc
    
def main():
    args = parse_args()
    job = create_job(args.width, args.height, args.virtual, True, "CCW")
    job()
    # schedule.every(2).minutes.do(create_job(args.width, args.height, args.virtual, True, "CCW"))

    # logging.info("Starting job runs")
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

if __name__ == '__main__':
    main()
