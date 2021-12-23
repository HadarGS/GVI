from bs4 import BeautifulSoup
import pandas as pd
import requests
from rake_nltk import Rake, Metric
import yake
from time import sleep
from random import randint
import re
import numpy as np
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver


def get_company_name(homepage):
    company = homepage.split('.')[-2].split('/')[-1]
    names = [company[1:i] for i in range(4,len(company)+1)]
    names.append(company)
    return(company,names)

def get_text(homepage):
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
    if rake:
        edited_kws = replace_delete(kws,kw_black_list,edited_kws,number_of_kws,1)
    else:
        edited_kws = replace_delete(kws,kw_black_list,edited_kws,number_of_kws,0)
    return (edited_kws)

def replace_delete(kws,kw_black_list,edited_kws,number_of_kws,bool):
    for kw in kws:
        if not any(word in kw[bool] for word in kw_black_list) and len(edited_kws)<=number_of_kws:
            edited_kw = re.sub(r'[^A-Za-z0-9 ]+', '', kw[bool])     #replace("/[^A-Za-z0-9 ]/", "")
            edited_kws.append(edited_kw)
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

def combine_kws(rake_kws,yake_kws,number_of_keywords):
    combined_kws = []
    for i in range(number_of_keywords):
        try:
            combined_kws.append(rake_kws[i])
        except:
            continue
        try:
            combined_kws.append(yake_kws[i])
        except:
            continue
    return(combined_kws)


'''Parameters'''
text_black_list = ['witter', 'nstagram', 'inkedin', 'html', 'oogle', '@','=','px']
sentences_to_join = 7
number_of_keywords = 40
'''Rake Parameters'''
rake_min_length = 2
rake_max_length = 4
'''Yake Parameters'''
max_ngram_size = 4
deduplication_thresold = 0.9
deduplication_algo = 'seqm'
windowSize = 1


"""Main"""
homepages =[]
texts=[]
rake_kws=[]
yake_kws=[]
combined_kws=[]

df = pd.read_csv('/Users/yanivamir/Documents/Machine Learning/GVI Kobi Kalderon/2021 Techstars Venture Connect -- Companies.csv')

for i,homepage in enumerate(df['Website']):
    sleep(randint(5, 15))
    print(homepage)
    company,names = get_company_name(homepage)
    keywords_black_list = [company,'http','www','website','ceo','CEO', 'com','find related','employees','links','Links','seed','round','usd','USD']
    text = get_text(homepage)
    text_sorted = sort_text(text,names,text_black_list)
    company_text = join_text(text_sorted,sentences_to_join)
    company_text = df['Description and Metrics'][i] + '\n' + company_text
    rake_keywords = run_rake(company_text,rake_min_length,rake_max_length,number_of_keywords,keywords_black_list+text_black_list)
    yake_keywords = run_yake(company_text,max_ngram_size,deduplication_thresold,deduplication_algo,windowSize,number_of_keywords,keywords_black_list+text_black_list)
    # print(company_text)
    print(rake_keywords)
    print(yake_keywords)
    combined_keywords = list(set(combine_kws(rake_keywords,yake_keywords,number_of_keywords)))
    print(combined_keywords)
    homepages.append(homepage)
    texts.append(text)
    rake_kws.append(rake_keywords)
    yake_kws.append(yake_keywords)
    combined_kws.append(combined_keywords)
    print('*****')

data = {'Homepage':homepages,'Text':texts,'Rake Keywords':rake_kws,'Yake Keywords':yake_kws,'Combined Keyword':combined_kws}
summary_df = pd.DataFrame.from_dict(data)
summary_df.columns = ['Company Name','Homepage', 'Text', 'Rake Keywords', 'Yake Keywords','Combined Keyword']
summary_df['Company Name'] = df['Company Name']
print(summary_df)
summary_df.to_csv('keywords from startups df v3.csv')




# homepage = df['Website'][np.random.randint(len(df))]    # Randomly picked company from csv for demonstration
# homepage_indices = random.choices(np.arange(len(df)), k=1)   # For extracting multiple companies: database needs to be established
# homepage = 'www.adopets.com'   # non-random example
# homepage = 'www.archfinance.io'   # non-random example
# homepage = 'kintaro.io'
# homepage = 'https://migrations.ml'