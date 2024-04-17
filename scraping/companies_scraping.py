# Scrap the website for company information
import requests
from bs4 import BeautifulSoup
import pandas as pd

all_companies = ['mindfactory', 'alternate', 'saturn', 'cyberport', 'mediamarkt','coolblue']
title, total_reviews, trust_score, percentage = [],[],[],[]

for company in all_companies:
  url = f'https://www.trustpilot.com/review/www.{company}.de'
  res = requests.get(url)
  soup = BeautifulSoup(res.content, "lxml")

  # Extract Company Information
  find_title = soup.find('span', class_ ="typography_display-s__qOjh6 typography_appearance-default__AAY17 title_displayName__TtDDM")
  title.append(find_title.text.capitalize())

  find_total_reviews = soup.find('span', class_="typography_body-l__KUYFJ typography_appearance-subtle__8_H2l styles_text__W4hWi")
  total_reviews.append(find_total_reviews.text.split()[0])

  find_trust_score = soup.find('p', class_= "typography_body-l__KUYFJ typography_appearance-subtle__8_H2l")
  trust_score.append(find_trust_score.text)

  find_percentage = soup.find_all('p', class_= "typography_body-m__xgxZ_ typography_appearance-default__AAY17 styles_cell__qnPHy styles_percentageCell__cHAnb")
  for i in find_percentage:
    percentage.append(i.text)

#Convert to dataframe
dict_companies = {'Name': [title.capitalize() for title in all_companies],
                  'total_reviews': total_reviews,
                  'Trust_score' : trust_score,
                  'Percentage_5' : percentage[0::5],
                  'Percentage_4' : percentage[1::5],
                  'Percentage_3' : percentage[2::5],
                  'Percentage_2' : percentage[3::5],
                  'Percentage_1' : percentage[4::5]}

df_com = pd.DataFrame(dict_companies)

df_com.to_csv('Companies.csv', index=False)
