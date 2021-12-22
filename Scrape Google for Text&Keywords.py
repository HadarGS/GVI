from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import requests
from rake_nltk import Rake, Metric
import yake


def get_company_name(homepage):
    company = homepage.split('.')[-2].split('/')[-1]
    return(company,[company[1:i] for i in range(4,len(company)+1)])

def get_text(company,homepage):
    result = requests.get('https://www.google.com/search?q='+homepage)
    html_page = result.content
    soup = BeautifulSoup(html_page, 'html.parser')
    # [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
    return(soup.findAll(text=True))

def sort_text(text,names,black_list):
    text_dict = {}
    text_dict['word #'],text_dict['text'] = [],[]
    positive_index,positive_text = [],[]
    for i, snipett in enumerate(text):
        if any(word in snipett for word in names) and not any(word in snipett for word in black_list):
            positive_index.append(i)
            positive_text.append(snipett)
            text_dict['text'].append(snipett)
            text_dict['word #'].append(len(snipett))
    text_sorted = pd.DataFrame.from_dict(text_dict).sort_values(by='word #', axis=0, ascending=False)
    return(text_sorted)

def join_text(text_sorted,sentences_to_join):
    return('\n '.join(text_sorted['text'][:sentences_to_join]))

def edit_kw(kws,number_of_kws,kw_black_list,rake):
    edited_kws = []
    for kw in kws[:number_of_kws]:
        if rake and not any(word in kw[1] for word in kw_black_list):
            edited_kws.append(kw)
        if not rake and not any(word in kw[0] for word in kw_black_list):
            edited_kws.append(kw)
    return(edited_kws)

def run_rake(text,min_length,max_length,number_of_kws,kw_black_list):
    rake = Rake(min_length=min_length, max_length=max_length)
    rake.extract_keywords_from_text(text)
    kws = rake.get_ranked_phrases_with_scores()
    return(edit_kw(kws,number_of_kws,kw_black_list,rake=True))

def run_yake(text,max_ngram_size,deduplication_thresold,deduplication_algo,windowSize,number_of_kws,kw_black_list):
    Yake = yake.KeywordExtractor(lan='en', n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=number_of_kws, features=None)
    kws = Yake.extract_keywords(text)
    return(edit_kw(kws,number_of_kws,kw_black_list,rake=False))


'''Parameters'''
text_black_list = ['witter', 'nstagram', 'inkedin', 'html', 'oogle', '@','=','px']
sentences_to_join = 7
number_of_keywords = 10
'''Rake Parameters'''
rake_min_length = 1
rake_max_length = 3
'''Yake Parameters'''
max_ngram_size = 3
deduplication_thresold = 0.9
deduplication_algo = 'seqm'
windowSize = 1


"""Main"""
df = pd.read_csv('/Users/yanivamir/Documents/Machine Learning/GVI Kobi Kalderon/2021 Techstars Venture Connect -- Companies.csv')
homepage = df['Website'][np.random.randint(len(df))]    # Randomly picked company from csv for demonstration
# homepage_indices = random.choices(np.arange(len(df)), k=1)   # For extracting multiple companies: database needs to be established
# homepage = 'www.adopets.com'   # non-random example
# homepage = 'www.archfinance.io'   # non-random example
# homepage = 'kintaro.io'
print(homepage)
company,names = get_company_name(homepage)
print(names)
keywords_black_list = [company,'http','www','website','ceo','CEO']

text = get_text(company,homepage)
text_sorted = sort_text(text,names,text_black_list)
company_text = join_text(text_sorted,sentences_to_join)
rake_keywords = run_rake(company_text,rake_min_length,rake_max_length,number_of_keywords,keywords_black_list)
yake_keywords = run_yake(company_text,max_ngram_size,deduplication_thresold,deduplication_algo,windowSize,number_of_keywords,keywords_black_list)

print(company_text)
print(rake_keywords)
print(yake_keywords)