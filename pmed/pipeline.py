import luigi
import pandas as pd
from datetime import date, timedelta
from pmc_address import get_pmc_links
from pmc_download import download_api, download_xml


# task to get links to new articles from PubMed OA
# output is links to PubMed
class GetLinksTask(luigi.Task):
    # output
    def output(self):
        return luigi.LocalTarget('./output_getlink.txt')

    # run task
    def run(self):
        # outfile
        with self.output().open('w') as outfile:
            get_pmc_links(outfile)


# task to get data from eutil API
# input is links to PubMed, output is path to file
class GetDataTask(luigi.Task):
    # require GetLinksTask to complete
    def requires(self):
        return GetLinksTask()
    
    # output
    def output(self):
        return luigi.LocalTarget('./output_getdata.txt')

    # run task
    def run(self):
        # read pmid from infile
        with self.input().open('r') as infile:
            df_links = pd.read_csv(infile, sep='\t')
            ids = df_links['id']
        
        # download data, write log to outfile
        with self.output().open('w') as outfile:
            download_api(ids, outfile, save_dir='./tmp')
        print('Saved {:} new PMIDs'.format(len(ids)))
    

# task to download XML file from FTP
# input is links to PubMed, output is path to file
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
            df_links = pd.read_csv(infile, sep='\t')
            links = df_links['addr']
        
        # download XML, write log to outfile
        with self.output().open('w') as outfile:
            download_xml(links, outfile, save_dir='./tmp')
        print('Saved {:} new XML files'.format(len(links)))
        

if __name__ == '__main__':
    luigi.run()
