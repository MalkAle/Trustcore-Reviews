
#%%
from bs4 import BeautifulSoup as bs
import requests 
import pandas as pd
from time import time 

#%%
#Creating empty dictionary for review data
#companies = ['mindfactory.de']
t0 = time()

companies = ['cyberport', 'mediamarkt', 'coolblue', 'mindfactory', 'alternate', 'saturn']
attributes = ['Rating','Title','Review','Response','ReviewDate', 'ExperienceDate']

results = {}
temp_date = []
for company in companies:
    results[company] = {}
    for attribute in attributes:
        results[company][attribute] = []


#%%
#Iteration over list of companies. No iteration over attributes since each attribute needs a separate statment to
#retieve data

#All the attributes are inside one loop to ensure that the lists for different attributes are indexed correctly,
#that is, if for example a review text is missing, the list is filled "NaN" at the correct index, the "try-except"
#statement does exactly that.  
for company in companies: 
    page = 1
    while True:
        #Generating url for scraping
        url = f"https://www.trustpilot.com/review/www.{company}.de?page={page}&sort=recency"
        page_ = requests.get(url)  
        soup = bs(page_.content, "lxml")
        #print(f"Currently scraping following url: {url}")
        
        #Contains all elements for current page
        elems = soup.find_all('div',class_ = 'styles_cardWrapper__LcCPA styles_show__HUXRb styles_reviewCard__9HxJJ')
        
        #When all reviews scrapped, an find_all returns an empty list. Here the scraping is stopped. 
        if elems == []:
            break
        else:
            for review in elems:
                #review core is mandatory for every review, the rest of the attributes are optional
                rating = review.find_all('div',class_ = "styles_reviewHeader__iU9Px")[0]['data-service-review-rating']
                results[company][attributes[0]].append(rating)

                try:
                    title = review.find('h2',class_='typography_heading-s__f7029 typography_appearance-default__AAY17').text
                    results[company][attributes[1]].append(title)
                except:
                    results[company][attributes[1]].append('NaN')

                try:
                    text = review.find('p',class_='typography_body-l__KUYFJ typography_appearance-default__AAY17 typography_color-black__5LYEn').text
                    results[company][attributes[2]].append(text.replace('\r',''))
                except:
                    results[company][attributes[2]].append('NaN')
        
                try:
                    response = review.find('p',class_='typography_body-m__xgxZ_ typography_appearance-default__AAY17 styles_message__shHhX').text
                    results[company][attributes[3]].append(response)
                except:
                    results[company][attributes[3]].append('NaN')

                try:
                    review_date = review.find_all('time')[0]['datetime']
                    results[company][attributes[4]].append(review_date.split('T')[0])
                except:
                    results[company][attributes[4]].append('NaN')
                
                try:
                    experience_date = review.find('p', class_="typography_body-m__xgxZ_ typography_appearance-default__AAY17")
                    results[company][attributes[5]].append(str(experience_date).split('-->')[-1].split('<')[0])
                except:
                    results[company][attributes[5]].append('NaN')

        page += 1
# %% 
#The "explode" method allows to unpack the lists for the attributes, so that
#an entry in a row becomes a single element. 
columns = ['Company'] + attributes #otherwise the first columns would be "index"     
# %%
df = pd.DataFrame.from_dict(results, orient="index").explode(attributes).reset_index()
df.columns = columns #otherwise the first columns would be "index"
df['Company'] = df['Company'].str.capitalize()
df['ExperienceDate'] = pd.to_datetime(df['ExperienceDate'], format= '%B %d, %Y').dt.strftime('%Y-%m-%d')

company_id_map = {'Cyberport': 4, 
                  'Mediamarkt': 5, 
                  'Coolblue': 6, 
                  'Mindfactory': 1, 
                  'Alternate': 2, 
                  'Saturn': 3}

df['CompanyID'] = df['Company'].map(company_id_map) 

new_order = ['CompanyID', 'Company', 'Rating', 'Title', 'Review', 'Response', 'ReviewDate', 'ExperienceDate']

df = df[new_order]

print(f"\nScraping finished, shape of dataframe is {df.shape}")
#print("\n",100*'-',"\n")
 
#df.head()
# %%
df.to_csv('Reviews.csv', index = False)

t1 = time() - t0
print("Done in {} seconds".format(round(t1,3)))
# %%
