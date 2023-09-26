import argparse
import logging
import random
import time
import re
from abc import ABC, abstractmethod
from datetime import date, datetime

import display_image_it8951
import requests
import schedule

logging.basicConfig(level=logging.INFO)

class AbstractTodaysNewspaper(ABC):

    def getNewspaperUrl(self):
        pass

class FreedomForumPaper(AbstractTodaysNewspaper):
    FREEDOMFORUM_URL = 'https://cdn.freedomforum.org/dfp/jpg{date}/lg/{paper}.jpg'

    def __init__(self, paper_key):
        super().__init__()
        self.paper = paper_key

    def getNewspaperUrl(self):
        return self.FREEDOMFORUM_URL.format(date=datetime.now().day, paper=self.paper)


class FrontPagesPaper(AbstractTodaysNewspaper):
    BASE_URL = "https://www.frontpages.com/{paper}"

    def __init__(self, paper_key) -> None:
        super().__init__()
        self.paper = paper_key

    def getNewspaperUrl(self):
        url = FrontPagesPaper.BASE_URL.format(paper=self.paper)
        logging.info("fetching todays paper from url {}".format(FrontPagesPaper.BASE_URL.format(paper=self.paper)))
        response = requests.get(url)
        response.raise_for_status()
        x = re.search(r'https:\/\/www\.frontpages\.com\/g\/\d{4}\/\d{2}\/\d{2}\/.+\.webp\.jpg', response.content)
        if x is None:
            raise Exception("no jpg found for this paper")

        return x.group()
    

class NewspaperUrl:
    PAPERS = {
        FreedomForumPaper: [
            # 'CA_SFC',
            # 'CA_EBT',
            # 'CA_LAT',
            # 'NY_NYT',
            # 'MN_ST',
            # 'WI_PC',
            # 'MA_BG',
            # 'IL_CT',
            # 'CHI_PD',
            # 'TX_DMN',
        ],
        FrontPagesPaper: [
            'the-washington-post',
            'the-wall-street-journal',
            'south-china-morning-post',
        ]   
    }

    def __init__(self):
        self.papers = []
        for paper_source in NewspaperUrl.PAPERS.items():
            for paper_name in paper_source[1]:
                self.papers.append(paper_source[0](paper_name))

        random.shuffle(self.papers)
        self.paper = iter(self.papers)

    def getNextNewspaperUrl(self):
        try:
            paper_selection = next(self.paper)
        except StopIteration:
            self.paper = iter(self.papers)
            paper_selection = next(self.paper)
            
        return paper_selection.getNewspaperUrl()
        

def parse_args():
    p = argparse.ArgumentParser(description='Display a list of newspaper front pages from freedom forum')
    p.add_argument('-v', '--virtual', action='store_true',
                   help='display using a Tkinter window instead of the '
                        'actual e-paper device (for testing without a '
                        'physical device)')
    p.add_argument('-w', '--width', type=int, required=True)
    p.add_argument('-t', '--height', type=int, required=True)
    period_group = p.add_mutually_exclusive_group()
    period_group.add_argument('--sec', type=int, help="set period for update in seconds")
    period_group.add_argument('--min', type=int, help="set period for update in minutes")
    scale_group = p.add_mutually_exclusive_group()
    scale_group.add_argument('--fill', action='store_true', help='if set, fills entire frame with image with cropping')
    scale_group.add_argument('--scale', type=float, default=1.0, help='if set, starst with fit and scales up image by this factor. The larger dimension will be cropped')
    return p.parse_args()

def create_job(width, height, virtual, mirror, rotate, fill, scale):
    newspaper = NewspaperUrl()
    def jobfunc():
        logging.info("running job...")
        url = newspaper.getNextNewspaperUrl()
        logging.info("Newspaper url {}".format(url))
        display_image_it8951.do_imgurl_display(url,width, height, virtual, rotate, mirror, fill, scale)
        
    return jobfunc
    
def main():
    args = parse_args()

    if not args.min and not args.sec:
        create_job(args.width, args.height, args.virtual, True, "CCW", args.fill, args.scale)()
    else:
        if args.min:
            schedule.every(args.min).minutes.do(create_job(args.width, args.height, args.virtual, True, "CCW", args.fill, args.scale))
        elif args.sec:
            schedule.every(args.sec).seconds.do(create_job(args.width, args.height, args.virtual, True, "CCW", args.fill, args.scale))

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

