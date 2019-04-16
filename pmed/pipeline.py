# import sqlalchemy
# import multiprocessing
# import pandas as pd
# import numpy as np
# import requests

# from lxml import etree
# from ftplib import FTP
# from tqdm import tqdm
# from time import time, sleep

# start_date = '2019-01-01'
# url =
# r = requests.get(url)
# print(r.status_code)
# tree = etree.fromstring(r.content)
# print(xd.parse(r.content))

import luigi
import pandas as pd
from datetime import date, timedelta
from pmc_address import save_pmc_links, build_pmc_links
from pmc_download import download_xml


# task to get links to new articles from PubMed OA
# output is FTP links to PubMed
class GetLinksTask(luigi.Task):
    # put in start date and end date
    start_date = luigi.DateParameter(default=date.today() - timedelta(days=1))
    end_date = luigi.DateParameter(default=date.today())

    # output
    def output(self):
        return luigi.LocalTarget('./output_getlink.txt')

    # run task
    def run(self):
        # read from API
        url = 'https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?format=tgz'
        url = url + '&from=' + self.start_date.strftime(
            "%Y-%m-%d") + '&until' + self.end_date.strftime("%Y-%m-%d")
        links, next_url = build_pmc_links(url)
        
        # write to file
        with self.output().open('w') as outfile:
            for l in links[:3]:
                outfile.write(l + '\n')
        print('Saved {:} new links'.format(len(links)))


# task to download XML file from FTP
# input is links to FTP, output is path to XML file
class GetXMLTask(luigi.Task):
    # require GetLinksTask to complete
    def requires(self):
        return GetLinksTask()
    
    # output
    def output(self):
        return luigi.LocalTarget('./output_getxml.txt')
    
    # run task
    def run(self):
        # read links from infile
        with self.input().open('r') as infile:
            links = infile.read().splitlines()
        
        # download XML, write log to outfile
        with self.output().open('w') as outfile:
            download_xml(links, outfile, save_dir='./tmp')
        print('Saved {:} new XML files'.format(len(links)))
        

if __name__ == '__main__':
    luigi.run()
