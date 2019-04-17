import luigi
import pandas as pd
import os, glob
from etl import prep_database, get_pmc_links, download_api, load_data, update_citecount, update_citecount_sql


# task to start every task
class PrepTask(luigi.Task):
    # output
    def output(self):
        return luigi.LocalTarget('./prep.txt')

    # run task
    def run(self):
        # prep database
        prep_database()

        # create tmp directory if necessary
        if not os.path.exists('./tmp'):
            os.makedirs('./tmp')

        # cleanup temp files and log files
        for f in glob.glob("./tmp/*.pkl"):
            os.remove(f)
        for f in glob.glob("output*.txt"):
            os.remove(f)
        
        # write to log
        with self.output().open('w') as outfile:
            outfile.write('Prep task ran successfully' + '\n')


# task to get links to new articles from PubMed OA
# output is links to PubMed
class GetLinksTask(luigi.Task):
    # require PrepTask to complete
    def requires(self):
        return PrepTask()
    
    # output
    def output(self):
        return luigi.LocalTarget('./output_getlink.txt')

    # run task
    def run(self):
        # outfile
        with self.output().open('w') as outfile:
            get_pmc_links(outfile)


# task to get data from eutil API
# input is links to PubMed, output is list of PMIDs
class ExtractDataTask(luigi.Task):
    # require GetLinksTask to complete
    def requires(self):
        return GetLinksTask()
    
    # output
    def output(self):
        return luigi.LocalTarget('./output_extractdata.txt')

    # run task
    def run(self):
        # read pmid from infile
        with self.input().open('r') as infile:
            df_links = pd.read_csv(infile, sep='\t')
            ids = df_links['id']
        
        # download data, write log to outfile
        with self.output().open('w') as outfile:
            download_api(ids, outfile, save_dir='./tmp')
        print('Saved {:} new PMIDs to ./tmp'.format(len(ids)))    


# task to insert new data to database
# output is list of citation count
class LoadDataTask(luigi.Task):
    # parameter specify whether to include citations that don't have data on PubMed OA. Exclude = 0, Include = 1
    include_nodata = luigi.IntParameter()

    # require ExtractDataTask to complete
    def requires(self):
        return ExtractDataTask()

    # output
    def output(self):
        return luigi.LocalTarget('./output_loaddata.txt')

    # run task
    def run(self):
        # load data to DB, write log to outfile
        pmc_file = './output_getlink.txt'
        with self.output().open('w') as outfile:
            df_article = load_data(pmc_file, outfile, data_dir='./tmp', include_nodata=self.include_nodata)
        print('Saved {:} new PMIDs to database'.format(len(df_article)))    


# task to update citecount table on the database
# input is citation count, output is a logfile
class UpdateCiteCountTask(luigi.Task):
    # require LoadDataTask to complete
    def requires(self):
        return LoadDataTask()

    # output
    def output(self):
        return luigi.LocalTarget('./output_updatecount.txt')

    # run task
    def run(self):
        # read citecount from infile
        with self.input().open('r') as infile:
            df_cites = pd.read_csv(infile, sep='\t')

        # run SQL script to update citecount table
        # write to log
        with self.output().open('w') as outfile:
            try:
                update_citecount(df_cites)
                outfile.write('citecount table updated successfully' + '\n')
            except:
                outfile.write('citecount table update failed' + '\n')


if __name__ == '__main__':
    luigi.run()
