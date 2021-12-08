# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import pickle
import random
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

df = pd.read_csv('/Users/yanivamir/Documents/Machine Learning/GVI Kobi Kalderon/2021 Techstars Venture Connect -- Companies.csv')
keywords = []
company_by_keywords = {}
for row in range(len(df)):
    new_keywords = df['Industry Categories'][row].split(",")
    keywords += list(set(new_keywords) - set(keywords))
    for keyword in new_keywords:
        if keyword not in company_by_keywords.keys():
            company_by_keywords[keyword] = []
        company_by_keywords[keyword].append(df['Company Name'][row])
print(len(keywords))
print(keywords)

companies_per_keyword = {}
for keyword in keywords:
    companies_per_keyword[keyword] = len(company_by_keywords[keyword])

companies_per_keyword = pd.DataFrame(companies_per_keyword, index = ['# of companies'], columns=companies_per_keyword.keys())
companies_per_keyword = companies_per_keyword.T.sort_values(by = ['# of companies'], axis=0,ascending = False)
print(companies_per_keyword)
# print(companies_per_keyword.index)

plt.figure(figsize = (12,8))
sns.set_theme(style="whitegrid")
ax = sns.barplot(x =companies_per_keyword.index , y = '# of companies', data = companies_per_keyword)
ax.set(xlabel='Sector')
plt.xticks(rotation=90, size = 8)
plt.title('Companies by Sector')
plt.tight_layout()
plt.show()








# Press the green button in the gutter to run the script.
#if __name__ == '__main__':



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
