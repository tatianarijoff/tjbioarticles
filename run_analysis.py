import tjbioarticles
from tjbioarticles.articles_data import ArticlesData
from tjbioarticles.keywords import Keywords
from tjbioarticles.pubmed_extraction import PubMedExtraction


input_dir = 'input_data/'
output_dir = 'output_data/'
keys_dir = output_dir + 'keys/'
xml_dir = output_dir + 'xml/'
latex_dir = output_dir + 'pdf/'
img_dir = output_dir + 'img/'

email = ""
analysis = ArticlesData(output_dir, xml_dir, latex_dir, email)

key_list = Keywords()
key_list.find_keys_from_excel(input_dir + 'keywords.xlsx', 'TwoCombinations')

analysis.insert_values_from_PubMed_keywords(key_list,
                                            keys_dir + 'key_combination.xlsx',
                                            keys_dir + 'key_articles.xlsx')
analysis.export_data(output_dir + 'info_extraction.xlsx')
key_list.plot_keys_articles(keys_dir + 'articles_per_key.png')
key_list.plot_keys_group(keys_dir + 'articles_per_group0.png', 'Groups0')
key_list.plot_keys_group(keys_dir + 'articles_per_group1.png', 'Groups1')

analysis.plot_countries(img_dir + 'articles_per_country.png',
                        img_dir + 'articles_per_country_collab.png')
analysis.plot_years(img_dir + 'articles_per_year.png')
analysis.plot_keys(img_dir + 'keysearch.png')
analysis.plot_pubkeys(img_dir + 'Pubmedkeywords.png')
 
