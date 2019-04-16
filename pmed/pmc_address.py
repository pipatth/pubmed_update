import pandas as pd
import requests
from lxml import etree
from ftplib import FTP
from tqdm import tqdm
import os


# save links to temporary path
def save_pmc_links(url, save_dir='.'):
    # iterate until no more new links
    i = 1
    while True:
        links, url = build_pmc_links(url)
        filename = os.path.join(save_dir, str(i) + '.txt')
        pd.Series(links).to_csv(filename, index=False, header=False)
        print('Saved {:} new links'.format(len(links)))
        if url != '':
            break


# find newly added articles
def build_pmc_links(url):
    # request
    r = requests.get(url)
    if r.status_code != 200:
        print('Error!')
    tree = etree.fromstring(r.content)

    # response summary
    r_dict = {}
    try:
        r_dict['request'] = tree.find('request').text
        r_dict['format'] = tree.find('request').get('format')
        r_dict['total-count'] = int(tree.find('records').get('total-count'))
        r_dict['returned-count'] = int(tree.find('records').get('returned-count'))
    except AttributeError:
        print('No element')
    
    # links
    links = []
    for r_ in tree.findall('records/record'):
        links.append(r_.find('link').get('href'))
    assert len(links) == r_dict['returned-count']

    # next url
    try:
        next_url = tree.find('records/resumption/link').get('href')
    except AttributeError:
        next_url = ''
        
    return links, next_url


