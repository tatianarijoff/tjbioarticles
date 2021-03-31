import pandas as pd
import numpy as np
import itertools
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import seaborn as sns

max_key_cols = 6


class Keywords(object):
    '''The Keywords object extracts the keywords from a file
       and convert in a list of dictionary with keywords groups'''
    def __init__(self):
        self.key_search = pd.DataFrame(columns=['Keywords', 'articles',
                                                'nbr_articles'])
        self.articles_found = pd.DataFrame(columns=['id_article', 'key'])
        self.key_nbr = 0
        self.grp_colname = []
        return

    def load_founded_keys(self, keysearch_excel, articlesfound_excel):
        key_search = pd.read_excel(keysearch_excel)
        articles_found = pd.read_excel(articlesfound_excel)
        self.merge_key_search(key_search)
        self.merge_articles_found(articles_found)
        return

    def find_keys_from_excel(self, excel_file, sheet):
        excel_df = pd.read_excel(excel_file, sheet_name=sheet)
        excel_df = excel_df.replace(np.nan, '', regex=True)

        key_list = []
        group_list = []

        for i in range(0, len(excel_df.columns), 2):
            # Extract the column name for the keywords column and group column
            key_col = excel_df.columns[i]
            group_col = excel_df.columns[i+1]
            key_list.append(excel_df[key_col].tolist())
            group_list.append(excel_df[group_col].tolist())
        if (len(self.grp_colname) < len(group_list)):
            for i in range(len(self.grp_colname), len(group_list)):
                self.grp_colname.append('Groups'+str(i))
                self.key_search['Groups'+str(i)] = ''

        combin_key = key_list[0]
        combin_grp = group_list[0]
        tmp_key = []
        tmp_grp = []
        for i in range(1, len(key_list)):
            for ind1 in range(len(combin_key)):
                for ind2 in range(len(key_list[i])):
                    if key_list[i][ind2] != '':
                        tmp_key.append(combin_key[ind1] + ' AND '
                                       + key_list[i][ind2] )
                        tmp_grp.append(combin_grp[ind1] + ' AND '
                                       + group_list[i][ind2])
            combin_key = tmp_key
            tmp_key = []
            combin_grp = tmp_grp
            tmp_grp = []
        for i in range(len(combin_key)):
            mydic = {'Keywords': combin_key[i]}
            grp = combin_grp[i].split('AND')
            for i in range(len(grp)):
                mydic['Groups'+str(i)] = grp[i]
            self.key_search = self.key_search.append(mydic, ignore_index=True)

        self.key_nbr = self.key_search['Keywords'].count()
        return

    def articles_found_add(self, myid, mykey):
        tmp_dic = {'id_article': myid, 'key': mykey}
        ind = self.key_search[self.key_search['Keywords'] == mykey]\
                  .index.tolist()
        for group in self.grp_colname:
            tmp_dic[group] = self.key_search.loc[ind[0], group]
        self.articles_found = self.articles_found.append(tmp_dic,
                                                         ignore_index=True)
        return

    def find_keys_str(self, article_id):
        key_list = self.articles_found[self.articles_found['id_article'] ==
                                       article_id]['key'].values
        key_string = '; '.join(key_list)
        return key_string

    def merge_key_search(self, key_search):
        for ind, row in key_search.iterrows():
            curr_key = key_search['Keywords'][ind].str.strip()
            ind2 = self.key_search[self.key_search['Keywords'] == curr_key]\
                       .index.tolist()
            if (len(ind2) > 0):
                key_list.key_search.loc[ind2, 'Keywords'] = key_search\
                      ['Keywords'][ind]
                key_list.key_search.loc[ind2, 'articles'] = key_search\
                      ['articles'][ind]
                key_list.key_search.loc[ind2, 'nbr_articles'] = key_search\
                      ['nbr_articles'][ind]
                for group in self.grp_colname:
                    self.key_search.loc[ind2, group] = key_search[group][ind]
            else:
                tmp_dic = {'Keywords': curr_key,
                           'articles': key_search['articles'][ind],
                           'nbr_articles': key_search['nbr_articles'][ind],
                           }
                for group in self.grp_colname:
                    tmp_dic[group] = key_search[group][ind]
                self.key_search = self.key_search.append(tmp_dic,
                                                         ignore_index=True)
        self.key_search.replace(np.nan, '', regex=True)
        return

    def merge_articles_found(self, articles_found):
        for ind, row in articles_found.iterrows():
            curr_art = articles_found['id_article'][ind]
            curr_key = articles_found['key'][ind]
            ind2 = self.articles_found[
                       self.articles_found['id_article'] == curr_art]\
                       .index.tolist()
            if (len(ind2) > 0):
                for col in articles_found.columns:
                    self.articles_found.loc[ind2, col] =\
                         articles_found[col][ind]
            else:
                self.articles_found_add(curr_art, curr_key)
        self.articles_found.replace(np.nan, '', regex=True)
        return

    def save_keys_output(self, file_keysearch, file_articles_found):
        self.key_search.to_excel(file_keysearch, index=False)
        self.articles_found.to_excel(file_articles_found, index=False)

    def plot_keys_articles(self, img_name):
        key_art = self.key_search[self.key_search['nbr_articles'] > 0]\
                  .sort_values(['nbr_articles'], ascending=False)
        fig, ax = plt.subplots(figsize=(12, 12))
        sns.set(style='whitegrid')
        sns.barplot(data=key_art, y='Keywords', x='nbr_articles',
                    color='#00b359')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.ylabel('')
        plt.xlabel('Number of articles', size=18, color='#4f4e4e')
        plt.title('Number of Articles by key', size=18, color='#4f4e4e')
        plt.xticks(size=14, color='#4f4e4e')
        plt.yticks(size=14, color='#4f4e4e')
        sns.despine(left=True)
        plt.savefig(img_name, bbox_inches='tight')

    def plot_keys_group_subgroup(self, img_name, group_column,
                                 subcol, subgroup):
        '''The plot_keys_group plot the number of articles for each group in a
           group column, fixed a value for another group column'''
        key_art = self.articles_found[self.articles_found[subcol] == subgroup]\
            .drop_duplicates(subset=['id_article'])\
            .groupby([group_column])['id_article']\
            .count().reset_index(name='count') \
            .sort_values(['count'], ascending=False)

        fig, ax = plt.subplots(figsize=(12, 4))
        sns.set(style='whitegrid')
        sns.barplot(data=key_art, y=group_column, x='count',
                    color='#00b359')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.ylabel('')
        plt.xlabel('Number of articles', size=18, color='#4f4e4e')
        plt.title('Number of Articles by key for ' + subgroup,
                  size=18, color='#4f4e4e')
        plt.xticks(size=14, color='#4f4e4e')
        plt.yticks(size=14, color='#4f4e4e')
        sns.despine(left=True)
        plt.savefig(img_name, bbox_inches='tight')

    def plot_keys_group(self, img_name, group_column):
        '''The plot_keys_group plot the number of articles for each group in a
           group column, indipendently of the others group column'''
        key_art = self.articles_found.drop_duplicates(subset=['id_article'])\
            .groupby([group_column])['id_article']\
            .count().reset_index(name='count') \
            .sort_values(['count'], ascending=False)
        fig, ax = plt.subplots(figsize=(12, 4))
        sns.set(style='whitegrid')
        sns.barplot(data=key_art, y=group_column, x='count',
                    color='#00b359')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.ylabel('')
        plt.xlabel('Number of articles', size=18, color='#4f4e4e')
        plt.title('Number of Articles by key', size=18, color='#4f4e4e')
        plt.xticks(size=14, color='#4f4e4e')
        plt.yticks(size=14, color='#4f4e4e')
        sns.despine(left=True)
        plt.savefig(img_name, bbox_inches='tight')
