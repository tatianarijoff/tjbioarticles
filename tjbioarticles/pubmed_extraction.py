import pandas as pd
import numpy as np
from Bio import Entrez, Medline
import xml.etree.ElementTree as ET


class PubMedExtraction(object):
    '''The PubMedExtraction object finds the pubmed info based on
       keywords lists. It generates a DataFrame with all the useful
       information for article analysis'''
    def __init__(self, email):
        Entrez.email = email
        return

    def find_id_from_key(self, keywords):
        '''The find_id function finds the pubmed id based on
           keywords lists. The used keys are saved in an output excel '''
        idlist = []
        for ind, row in keywords.key_search.iterrows():
            mykey = keywords.key_search['Keywords'][ind]
            terms = mykey
            handle = Entrez.esearch(db='pubmed', term=mykey,
                                    sort='relevance',
                                    retmax=1000,
                                    usehistory="n")
            record = Entrez.read(handle)
            handle.close()
            print('Articles found with %s: %s' % (mykey,
                                                  record['Count']))
            keywords.key_search.loc[ind, 'articles'] = ', '\
                .join(record['IdList'])
            nbr = len(record['IdList'])
            keywords.key_search.loc[ind, 'nbr_articles'] = nbr
            idlist.extend(record["IdList"])
            for myid in record['IdList']:
                keywords.articles_found_add(myid, mykey)
        idlist = list(set(idlist))
        self.idlist = idlist

        return

    def find_id_from_title(self, titles_list):
        '''The find_id function finds the pubmed id based on
           keywords lists. The used keys are saved in an output excel '''
        idlist = []
        for title in titles_list:
            handle = Entrez.esearch(db='pubmed', term=title,
                                    field='title',
                                    sort='relevance',
                                    retmax=1000,
                                    usehistory="n")
            record = Entrez.read(handle)
            handle.close()

            idlist.extend(record["IdList"])
        # create the new dataframe with the list of articles
        idlist = list(set(idlist))
        self.idlist = idlist
        return

    def find_info_xml(self, article_id):
        '''The find_xml function finds the pubmed info based on the id.
           and return the data in the xml format '''
        fetch_handle = Entrez.efetch(db='pubmed', rettype='medline',
                                     id=article_id, retmode="xml")
        data = fetch_handle.read()
        fetch_handle.close()
        return data
