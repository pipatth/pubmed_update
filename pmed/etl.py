from ftplib import FTP
from tqdm import tqdm
import pubmed_parser as pp
import pandas as pd
import numpy as np
import sqlalchemy
import os, time
from config import Config
from datautils import get_jid, get_ids, get_cnt, update_cnt, write_tables, list_tables, create_tables


# prep database
def prep_database():

    # connection to db
    conn = sqlalchemy.create_engine(
        Config.SQLALCHEMY_DATABASE_URI, pool_recycle=Config.DB_CONFIG['pool_recycle'])

    # create table if necessary
    tables = list_tables(conn)

    # if no tables, create them
    if not tables:
        create_tables(conn)


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
    df = pd.read_csv(filename, sep='\t', skiprows=1, names=[
                     'addr', 'journal', 'pmc', 'id', 'cc'])
    df = df[['id', 'pmc', 'addr']]
    df = df[(~df['id'].isna()) & (~df['pmc'].isna())]
    df['id'] = df['id'].str.replace('PMID:', '').fillna(0).astype(int)
    df['pmc'] = df['pmc'].str.replace('PMC', '').fillna(0).astype(int)
    print('There are {:} files in OA File List'.format(len(df)))

    # get latest PMC on DB
    conn = sqlalchemy.create_engine(
        Config.SQLALCHEMY_DATABASE_URI, pool_recycle=Config.DB_CONFIG['pool_recycle'])
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


# eutil API download, parse xml
def download_api(ids, outfile, save_dir):

    # if more than 1000 ids, do batch
    if len(ids) > 1000:
        chunks = np.array_split(ids, len(ids) / 1000)
    else:
        chunks = [ids]

    # run in chunks
    print("Downloading from API in {:} chunks".format(len(chunks)))
    i = 1
    for chunk in chunks:
        # list to store data
        articles = []
        citations = []
        for id in tqdm(chunk):
            try:
                # article
                time.sleep(0.25)
                articles.append(pp.parse_xml_web(id, save_xml=False))

                # citations
                time.sleep(0.25)
                d_ = pp.parse_outgoing_citation_web(id, id_type='PMID')
                if d_:
                    for bpmid in d_['pmid_cited']:
                        citations.append({'apmid': d_['doc_id'], 'bpmid': bpmid})
            except TypeError:
                pass

        # write to SQL
        df_data = pd.DataFrame(articles)
        df_data.to_pickle(os.path.join(save_dir, 'df_data_' + str(i) + '.pkl'))
        df_ref = pd.DataFrame(citations)
        df_ref.to_pickle(os.path.join(save_dir, 'df_ref_' + str(i) + '.pkl'))

        # write to log
        for id in df_data['pmid'].tolist():
            outfile.write(id + '\n')
        i += 1
    print("All done!")


# load to database
def load_data(pmc_file, outfile, data_dir, include_nodata=0):

    # connection to db
    conn = sqlalchemy.create_engine(
        Config.SQLALCHEMY_DATABASE_URI, pool_recycle=Config.DB_CONFIG['pool_recycle'])

    # pmc lookup file
    df_pmc = pd.read_csv(pmc_file, sep='\t')

    # open .pkl files
    filenames = os.listdir(data_dir)

    # article
    articles = []
    data_files = [f for f in filenames if f.startswith('df_data') and f.endswith('.pkl')]
    for f in data_files:
        articles.append(pd.read_pickle(os.path.join(data_dir, f)))
    df_article = pd.concat(articles, ignore_index=True)
    df_article = df_article[df_article['year'] != '']
    df_article['id'] = df_article['pmid'].astype(int)
    df_article['pubyear'] = df_article['year'].astype(int)
    df_article = df_article.merge(df_pmc, on='id', copy=False)
    df_article['jid'] = 0

    # filter out articles already in db
    ids_indb = get_ids(conn)
    print("There are {:} articles to load".format(len(df_article)))
    print("There are {:} articles already in the database".format(len(df_article[df_article['id'].isin(ids_indb)])))
    df_article = df_article[~df_article['id'].isin(ids_indb)]

    # get jid and format article
    for i,v in df_article.iterrows():
        df_article.loc[i, 'jid'] = get_jid(conn, v['journal'])
    df_article = df_article[['id', 'title', 'abstract', 'pubyear', 'jid', 'keywords', 'pmc']]
    write_tables(conn, df_article, 'article')
    print("Loaded {:} articles to database".format(len(df_article)))

    # citations
    citations = []
    data_files = [f for f in filenames if f.startswith('df_ref') and f.endswith('.pkl')]
    for f in data_files:
        citations.append(pd.read_pickle(os.path.join(data_dir, f)))
    df_citations = pd.concat(citations, ignore_index=True)
    df_citations = df_citations[df_citations['bpmid'] != '']
    df_citations = df_citations.astype(int)
    df_citations = df_citations[df_citations['apmid'].isin(df_article['id'].tolist())]

    # include or exclude citations that don't have data
    if include_nodata == 0:
        df_citations = df_citations[df_citations['bpmid'].isin(get_ids(conn))]
    write_tables(conn, df_citations, 'citation')
    print("Loading {:} citations to database".format(len(df_citations)))

    # write citation count to log
    df_cites = df_citations.groupby('bpmid', as_index=False).count()
    df_cites.columns = ['id', 'n']
    df_cites.to_csv(outfile, sep='\t', index=False)

    return df_article


# update citecount table 
def update_citecount(df_cites):

    # connection to db
    conn = sqlalchemy.create_engine(
        Config.SQLALCHEMY_DATABASE_URI, pool_recycle=Config.DB_CONFIG['pool_recycle'])

    # add citation to the count in database table
    for i,v in df_cites.iterrows():
        total_cnt = get_cnt(conn, v['id']) + v['cnt']
        update_cnt(conn, v['id'], total_cnt)
    return


# update citecount table using GROUP BY SQL 
def update_citecount_sql():

    # connection to db
    conn = sqlalchemy.create_engine(
        Config.SQLALCHEMY_DATABASE_URI, pool_recycle=Config.DB_CONFIG['pool_recycle'])

    # truncate
    stmt = '''TRUNCATE TABLE citecount'''
    conn.execute(stmt)

    # update 
    stmt = '''
        INSERT INTO citecount
        SELECT
        bpmid AS id
        , COUNT(1) AS citations
        , CASE WHEN a.id IS NULL THEN 1 ELSE 0 END AS has_data
        FROM citation c
        LEFT OUTER JOIN article a
        ON c.bpmid = a.id
        GROUP BY bpmid, title
        '''
    conn.execute(stmt)
    return
