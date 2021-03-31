import numpy as np
import pandas as pd
import os
import re
import xml.etree.ElementTree as ET
from pylatex import Document, Section, Subsection, Command, LargeText
from pylatex.utils import italic, NoEscape, bold
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import seaborn as sns
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

from tjbioarticles.keywords import Keywords
from tjbioarticles.pubmed_extraction import PubMedExtraction

class ArticlesData(object):
    '''The ArticlesData object collects the articles informations in a useful
       DataFrame and allows some output analysis'''
    def __init__(self, output_dir, xml_dir, latex_dir, email):
        self.output_dir = output_dir
        self.xml_dir = xml_dir
        self.latex_dir = latex_dir
        self.country_dict = pd.read_excel(r'input_data/country_dict.xlsx')
        self.email = email
        
        self.data_analysis = pd.DataFrame()
        self.create_data_structs()
        return

    def load_data(self, data_excel):
        self.data_analysis = pd.read_excel(data_excel)
        return

    def load_xml(self, filename):
        mytree = ET.parse(filename)
        self.xml_data = mytree.getroot()

        return

    def export_data(self, output_excel):
        final_data = self.data_analysis.drop('abstract', axis=1)
        final_data.to_excel(output_excel, index=False)
        return

    def insert_values_from_excel(self, input_excel):
        data = pd.read_excel(r'input_data/country_dict.xlsx')
        self.data_analysis = self.data_analysis.append(data,
                                                       ignore_index=True)
        return

    def insert_values_from_PubMed_keywords(self, keywords, file_keysearch,
                                           file_articles_found):
        pub_data = PubMedExtraction(self.email)
        pub_data.find_id_from_key(keywords)
        self.collect_pubmed_data(pub_data, keywords)
        keywords.save_keys_output(file_keysearch, file_articles_found)
        return

    def insert_values_from_PubMed_title(self, title):
        pub_data = PubMedExtraction()
        pub_data.find_id_from_title(title)
        self.collect_pubmed_data(pub_data)
        return

    def create_data_structs(self):
        '''The create_data_columns function generates the analysis_data
            columns.'''
        self.data_analysis['id'] = ''
        self.data_analysis['filename'] = ''
        self.data_analysis['year'] = ''
        self.data_analysis['first_author'] = ''
        self.data_analysis['title'] = ''
        self.data_analysis['journal'] = ''
        self.data_analysis['pub_status'] = ''
        self.data_analysis['authors'] = ''
        self.data_analysis['authors_info'] = ''
        self.data_analysis['country'] = ''
        self.data_analysis['keywords_major'] = ''
        self.data_analysis['keywords_minor'] = ''
        self.data_analysis['search_key'] = ''
        self.data_analysis['abstract'] = ''

        self.abstract = {}

        return

    def collect_pubmed_data(self, pub_data, keywords):
        for article_id in pub_data.idlist:
            xml_data = pub_data.find_info_xml(article_id)
            f = open(self.xml_dir + 'tmp.xml', "wb")
            f.write(xml_data)
            f.close()
            mytree = ET.parse(self.xml_dir + 'tmp.xml')
            self.xml_data = mytree.getroot()
            data = pd.DataFrame([article_id], columns=['id'])
            self.data_analysis = self.data_analysis.append(data,
                                                           ignore_index=True)
            ind = self.data_analysis.index[self.data_analysis['id'] ==
                                           article_id].tolist()
            ind = ind[0]
            self.insert_title(ind, self.data_analysis)
            print("collecting info for ")
            print(self.data_analysis['title'][ind])
            self.insert_year(ind, self.data_analysis)
            self.insert_journal(ind, self.data_analysis)
            self.insert_publication_status(ind, self.data_analysis)
            self.insert_authors_countries(ind, self.data_analysis)
            self.insert_keywords(ind, self.data_analysis)
            self.insert_abstract(ind, self.data_analysis)
            self.data_analysis.loc[ind, 'search_key'] = keywords\
                                                       .find_keys_str(
                                                       article_id)
            filename = (str(ind + 1) + '_' +
                        self.data_analysis['first_author'][ind] + '_' +
                        self.data_analysis['year'][ind])

            self.data_analysis['filename'][ind] = filename
            self.create_pdf(filename, ind)
            os.rename(self.xml_dir+'tmp.xml', self.xml_dir+filename+'.xml')
        return

    def insert_title(self, ind, data):
        for tmp_title in self.xml_data.iter('ArticleTitle'):
            title = tmp_title.text
        data.loc[ind, 'title'] = title
        return

    def insert_journal(self, ind, data):
        for jou in self.xml_data.iter('Title'):
            journal = jou.text
        data.loc[ind, 'journal'] = journal
        return

    def insert_publication_status(self, ind, data):
        for el in self.xml_data.iter('PublicationStatus'):
            pub_status = el.text
        data.loc[ind, 'pub_status'] = pub_status
        return

    def insert_year(self, ind, data):
        for pubdate in self.xml_data.iter('PubDate'):
            for el in pubdate.iter():
                if (el.tag == 'Year'):
                    data.loc[ind, 'year'] = el.text
                    return
                if (el.tag == 'MedlineDate'):
                    twodates = el.text.split('-')
                    year = twodates[0][:4]
                    data.loc[ind, 'year'] = year
                    return

    def insert_authors_countries(self, ind, data):
        authors_list = []
        authors_info = []
        country_list = []
        country_final_list = []
        count_line = 0
        for author in self.xml_data.iter('Author'):
            for el in author.iter():
                if (el.tag == 'LastName'):
                    author_name = el.text
                    author_info = author_name
                    authors_list.append(author_name)
                    if count_line == 5:
                        authors_list.append("\\")
                        count_line = 0
                if(el.tag == 'Affiliation'):
                    affil = el.text
                    country = self.find_country(affil)
                    if country:
                        country_list.append(country)
                        author_info += "(" + country +")"
                        if ('@' in affil):
                            country_final_list.append(country)
                            match_mail = re.search(r'[\w\.-]+@[\w\.-]+',
                                                   affil)
                            email = match_mail.group(0)
                            author_info += "Email:  " + email
            authors_info.append(author_info)
            count_line +=1


        country_list = list(set(country_list))
        country_final_list = list(set(country_final_list))
        # if all the author has the same country this is the country of the
        # article
        if (len(country_list) == 1):
            country_final_list = country_list
        data.loc[ind, 'first_author'] = authors_list[0]
        data.loc[ind, 'authors'] = ', '.join(authors_list)
        data.loc[ind, 'authors_info'] = ', '.join(authors_info)
        data.loc[ind, 'country'] = ', '.join(country_final_list)
        return

    def insert_abstract(self, ind, data):
        abstract_analysis = []
        for abstract_list in self.xml_data.iter('AbstractText'):
            for el in abstract_list.iter():
                if el.text == None:
                    continue
                abstract = self.adjust_abstract(el.text)
                try:
                    label = self.adjust_abstract(el.attrib['Label'])
                    abstract_analysis.append(label + ':')
                    abstract_analysis.append(abstract)
                except KeyError:
                    abstract_analysis.append(abstract)
                if el.tail != None:
                    abstract = self.adjust_abstract(el.tail)
                    abstract_analysis.append(abstract)

        data.loc[ind, 'abstract'] = '\n'.join(abstract_analysis)
        return

    def insert_keywords(self, ind, data):

        key_major = []
        key_minor = []
        for keylist in self.xml_data.iter('KeywordList'):
            for el in keylist.iter():
                if(el.tag == 'Keyword'):
                    key = el.text
                    if (el.attrib['MajorTopicYN'] == 'Y'):
                        key_major.append(key)
                    else:
                        key_minor.append(key)
        for keylist in self.xml_data.iter('Keyword'):
            for el in keylist.iter():
                if(el.tag == 'DescriptorName'):
                    key = el.text
                    if (el.attrib['MajorTopicYN'] == 'Y'):
                        key_major.append(key)
                    else:
                        key_minor.append(key)
        for keylist in self.xml_data.iter('MeshHeading'):
            for el in keylist.iter():
                if(el.tag == 'DescriptorName'):
                    key = el.text
                    if (el.attrib['MajorTopicYN'] == 'Y'):
                        key_major.append(key)
                    else:
                        key_minor.append(key)

        data.loc[ind, 'keywords_major'] = ', '.join(key_major)
        data.loc[ind, 'keywords_minor'] = ', '.join(key_minor)
        return

    def adjust_abstract(self, abstract):
        abstract = abstract.replace(u'U2009', '')
        abstract = abstract.replace(u'\u0391', 'Alpha')
        abstract = abstract.replace(u'\u0392', 'Beta')
        abstract = abstract.replace(u'\u0393', 'Gamma')
        abstract = abstract.replace(u'\u0394', 'Delta')
        abstract = abstract.replace(u'\u03B1', 'alpha')
        abstract = abstract.replace(u'\u03B2', 'beta')
        abstract = abstract.replace(u'\u03B3', 'gamma')
        abstract = abstract.replace(u'\u03B4', 'delta')
        abstract = abstract.replace(u'\u2265', '>=')
        abstract = abstract.replace(u'U+2264', '<=')
        abstract = abstract.replace(u'\u2005', ' ')
        abstract = abstract.replace(u'U+2009', ' ')
        return abstract

    def find_country(self, string):
        for ind in self.country_dict.index:
            country = self.country_dict['List1'][ind]
            if (country in string):
                return self.country_dict['List2'][ind]

        return ''

    def create_pdf(self, filename, ind):
        print("+"*10)
        print("Generating Pdf %s" % (filename))

        doc = Document()

        doc.preamble.append(Command('title',
                            self.data_analysis['title'][ind]))
        doc.preamble.append(Command('author',
                            self.data_analysis['authors'][ind]))
        doc.preamble.append(Command('date',
                            self.data_analysis['year'][ind]))
        doc.append(NoEscape(r'\maketitle'))
        doc.append(LargeText(bold('Abstract\n\n')))
        doc.append('\n')
        doc.append(self.data_analysis['abstract'][ind])
        doc.append('\n\n\n\n')
        doc.append('Keywords Major Topic: \n')
        doc.append(self.data_analysis['keywords_major'][ind])
        doc.append('\nOther keywords: \n')
        doc.append(self.data_analysis['keywords_minor'][ind])
        try:
            doc.generate_pdf(self.latex_dir + filename)
        except:
            fd = open(self.latex_dir + filename + '.error','w')
            fd.write('Error creating pdf')
            fd.close()
        return

    def plot_years(self, img_name):
        articles_per_year = self.data_analysis['year'].value_counts()\
                           .sort_index()
        fig, ax = plt.subplots(figsize=(12, 5))
        sns.set(style='whitegrid')
        articles_per_year.plot(kind='bar', facecolor='#00b359', width=0.7)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(axis='x', linestyle='dashed', alpha=0.5)
        plt.ylabel('')
        plt.xlabel('Year', size=12, color='#4f4e4e')
        plt.title('Number of articles per year', size=16, color='#4f4e4e',
                  fontweight='bold')
        plt.xticks(size=12, color='#4f4e4e')
        plt.yticks(size=12, color='#4f4e4e')
        sns.despine(left=True)
        plt.savefig(img_name, bbox_inches='tight')

        return

    def plot_keys(self, img_name):
        text = ' '.join(self.data_analysis['search_key'])
        fig, ax = plt.subplots(figsize=(12, 5))
        wordcloud = WordCloud(background_color="white").generate(text)

        # Display the generated image:
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.savefig(img_name, bbox_inches='tight')

        return

    def plot_pubkeys(self, img_name):
        list1 = self.data_analysis['keywords_major']
        list2 = self.data_analysis['keywords_minor']
        fin_list = list1 + list2
        text = ' '.join(fin_list)
        fig, ax = plt.subplots(figsize=(12, 5))
        wordcloud = WordCloud(background_color="white").generate(text)

        # Display the generated image:
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.savefig(img_name, bbox_inches='tight')

        return

    def plot_countries(self, img_name, img_name_collab):
        countries = pd.DataFrame(columns=['Country', 'Collaboration'])
        self.data_analysis['country'] = self.data_analysis['country']\
                                      .str.rstrip()
        # Create the list of countries
        for index, row in self.data_analysis.iterrows():
            country = self.data_analysis['country'][index]
            list_country = country.split(', ')
            if (len(list_country) == 1):
                countries = countries.append({'Country': list_country[0],
                                             'Collaboration': False},
                                             ignore_index=True)
            elif (len(list_country) > 1):
                for country in list_country:
                    countries = countries.append({'Country': country,
                                                 'Collaboration': True},
                                                 ignore_index=True)
            else:
                continue
        art_per_country = countries['Country'].value_counts()\
                                              .sort_values(ascending=True)
        # Plot articles per country ignoring collaborations
        fig, ax = plt.subplots(figsize=(12, 5))
        sns.set(style='whitegrid')
        art_per_country.plot(kind='barh', facecolor='#00b359', width=0.8)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(axis='y', linestyle='dashed', alpha=0.5)
        plt.xlabel('Nbr. of pubblication', size=14, color='#4f4e4e')
        plt.title('Number of articles per country', size=16, color='#4f4e4e',
                  fontweight='bold')
        plt.xticks(size=12, color='#4f4e4e')
        plt.yticks(size=12, color='#4f4e4e')
        sns.despine(left=True)
        plt.savefig(img_name, bbox_inches='tight')

        fig.clf()
        # ~ print(countries['Collaboration'])
        # ~ print(countries['Country'][countries['Collaboration'] == False])
        # Emphasize the collaboration
        art_nocoll = countries['Country'][countries['Collaboration'] == False]\
                              .value_counts()
        art_nocoll = pd.DataFrame(art_nocoll)
        art_nocoll.columns = ['no_coll']
        art_nocoll['Country'] = art_nocoll.index

        art_coll = countries['Country'][countries['Collaboration']]\
                            .value_counts()
        art_coll = pd.DataFrame(art_coll)
        art_coll.columns = ['coll']
        art_coll['Country'] = art_coll.index

        art_per_country = pd.DataFrame(art_per_country)
        art_per_country.columns = ['tot']
        art_per_country['Country'] = art_per_country.index
        art_per_country = art_per_country.join(art_nocoll.set_index('Country'),
                                               on='Country').fillna(0)
        art_per_country = art_per_country.join(art_coll.set_index('Country'),
                                               on='Country').fillna(0)
        # the column tot has bees used for obtaining the dataframe ordered,
        # now can be removed
        art_per_country = art_per_country.drop(['Country', 'tot'], axis=1)
        ax = art_per_country.plot(kind='barh', stacked=True, width=0.8,
                             color={'no_coll': '#00b359', 'coll': '#00e673'},
                             figsize=(12, 5))
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(axis='y', linestyle='dashed', alpha=0.5)
        plt.ylabel('')
        plt.xlabel('Nbr. of pubblication', size=14, color='#4f4e4e')
        plt.title('Number of articles per country', size=16, color='#4f4e4e',
                  fontweight='bold')
        plt.xticks(size=12, color='#4f4e4e')
        plt.yticks(size=12, color='#4f4e4e')
        plt.legend(['Without collaboration', 'International Collaboration'],
                   fontsize=14)
        sns.despine(left=True)
        plt.savefig(img_name_collab, bbox_inches='tight')

        return
