from ftplib import FTP
from config import Config
import pandas as pd
import sqlalchemy
import os


# find PubMed articles to add to database
def get_pmc_links(outfile):
    # links
    ftp_link = 'ftp.ncbi.nlm.nih.gov'
    dir_ = '/pub/pmc'
    filename = 'oa_file_list.txt'

    # download
    print("Downloading PubMed OA File List...")    
    with FTP(ftp_link) as ftp:
        ftp.login()
        ftp.cwd(dir_)
        filedata = open(filename, 'wb')
        ftp.retrbinary('RETR ' + filename, filedata.write)
        filedata.close()
        ftp.quit()

    # read oa_file_list.txt
    df = pd.read_csv(filename, sep='\t', skiprows=1, names=['addr', 'journal', 'pmc', 'id', 'cc'])
    df = df[['id', 'pmc', 'addr']]
    df = df[(~df['id'].isna()) & (~df['pmc'].isna())]
    df['id'] = df['id'].str.replace('PMID:', '').fillna(0).astype(int)
    df['pmc'] = df['pmc'].str.replace('PMC', '').fillna(0).astype(int)
    print('There are {:} files in OA File List'.format(len(df)))

    # get latest PMC on DB
    conn = sqlalchemy.create_engine(Config.SQLALCHEMY_DATABASE_URI)
    stmt = '''SELECT MAX(pmc) AS pmc FROM article'''
    d_last_pmc = pd.read_sql(stmt, conn).fillna(0)
    last_pmc = d_last_pmc['pmc'].values[0]
    print('Last PMC load is', last_pmc)

    # filter only new PMC
    df = df[df['pmc'] > last_pmc]
    df.to_csv(outfile, sep='\t', index=False)    
    print('There are {:} files to load'.format(len(df)))
    os.remove(filename)
    return
