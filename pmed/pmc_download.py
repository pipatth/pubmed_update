from ftplib import FTP
from tqdm import tqdm
import pubmed_parser as pp
import pandas as pd
import tarfile
import os


# ftp download, parse xml
def download_xml(links, outfile, save_dir='.'):

    # reject if file is larger than 1200 rows
    assert len(links) <= 1200
    
    # links
    ftp_link = 'ftp.ncbi.nlm.nih.gov'

    # download
    data_list = []
    ref_list = []
    print("Downloading XML...")
    with FTP(ftp_link) as ftp:
        ftp.login()
        for link in tqdm(links):
            # download
            path_ = '/'.join(['/pub/pmc'] + link.split('/pub/pmc/')[1:])
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
            ref_list.extend(pp.parse_pubmed_references(xml_path))

            # delete xml
            dirname = os.path.dirname(xml_path)
            os.remove(xml_path)
            os.rmdir(dirname)

        ftp.quit()
    
    # write to SQL
    df_data = pd.DataFrame(data_list)
    df_data.to_pickle('df_data.pkl')
    df_ref = pd.DataFrame(ref_list)
    df_ref = df_ref[df_ref['pmid_cited'] != ''][['pmc', 'pmid', 'pmid_cited']]
    df_ref.to_pickle('df_ref.pkl')

    # write to log
    for id in df_data['pmc'].tolist():
        outfile.write(id + '\n')

    print("All done!")
