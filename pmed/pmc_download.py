from ftplib import FTP
from tqdm import tqdm
import pubmed_parser as pp
import pandas as pd
import numpy as np
import tarfile
import os, time


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
    for chunk in chunks[:3]:
        # list to store data
        articles = []
        citations = []
        for id in tqdm(chunk[:10]):
            # article
            time.sleep(0.25)
            articles.append(pp.parse_xml_web(id, save_xml=False))

            # citations
            time.sleep(0.25)
            d_ = pp.parse_outgoing_citation_web(id, id_type='PMID')
            for bpmid in d_['pmid_cited']:
                citations.append({'apmid': d_['doc_id'], 'bpmid': bpmid})

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


# ftp download, parse xml
def download_xml(links, outfile, save_dir):

    # links
    ftp_link = 'ftp.ncbi.nlm.nih.gov'

    # if more than 1000 links, do batch
    if len(links) > 1000:
        chunks = np.array_split(links, len(links) / 1000)
    else:
        chunks = [links]

    # run in chunks
    print("Downloading from API in {:} chunks".format(len(chunks)))
    i = 1
    for chunk in chunks:
        # download
        data_list = []
        ref_list = []
        print("Downloading XML...")
        with FTP(ftp_link) as ftp:
            ftp.login()
            for link in tqdm(chunk):
                # download
                path_ = '/pub/pmc/' + link
                dir_ = '/'.join(path_.split('/')[:-1])
                filename = path_.split('/')[-1]
                ftp.cwd(dir_)
                filedata = open(filename, 'wb')
                ftp.retrbinary('RETR ' + filename, filedata.write)
                filedata.close()

                # extract only .nxml
                tf = tarfile.open(filename)
                for tarinfo in tf:
                    if os.path.splitext(tarinfo.name)[1] == ".nxml":
                        tf.extract(member=tarinfo, path=save_dir)
                        xml_path = os.path.join(save_dir, tarinfo.name)
                        break
                tf.close()

                # delete tar
                os.remove(filename)

                # parse xml
                data_list.append(pp.parse_pubmed_xml(xml_path, nxml=True))

                # parse reference xml
                ref = pp.parse_pubmed_references(xml_path)
                if ref:
                    ref_list.extend(ref)

                # delete xml
                dirname = os.path.dirname(xml_path)
                os.remove(xml_path)
                os.rmdir(dirname)
            ftp.quit()
        
        # write to SQL
        df_data = pd.DataFrame(data_list)
        df_data.to_pickle(os.path.join(save_dir, 'df_data_' + str(i) + '.pkl'))
        df_ref = pd.DataFrame(ref_list)
        df_ref = df_ref[df_ref['pmid_cited'] != ''][['pmc', 'pmid', 'pmid_cited']]
        df_ref.to_pickle(os.path.join(save_dir, 'df_ref_' + str(i) + '.pkl'))

        # write to log
        for id in df_data['pmid'].tolist():
            outfile.write(id + '\n')
        i += 1
    print("All done!")
