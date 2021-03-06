#import django models
import sys, os, django
sys.path.append('/system/coronaproj/coronaliveapp/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coronaliveapp.settings")
django.setup()

import pandas as pd
from bs4 import BeautifulSoup
import re, requests
from django.utils.dateparse import parse_date

from corona.models import Daily

def remove_html_tags(text):
    """Remove html tags from a string"""
    text=str(text)
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

url="https://en.wikipedia.org/wiki/Timeline_of_the_2020_coronavirus_pandemic_in_India"
response = requests.get(url)

soup=BeautifulSoup(response.text,"html.parser")
dates=soup.findAll('td',{'colspan':'2','style':'padding-left:0.4em; padding-right:0.4em; text-align:center'})
table=soup.findAll('td',{'style':'border-left:1px solid silver; border-right:1px solid silver'})

dates=[remove_html_tags(x) for x in dates]

active=list()
death=list()
recovered=list()

for rows in table:
    row=rows.findAll('div')
    active.append(row[2].get('title').replace(",",""))
    death.append(row[0].get('title').replace(",",''))
    recovered.append(row[1].get('title').replace(",",""))

active=list(map(int,active))
death=list(map(int,death))
recovered=list(map(int,recovered))

daily=pd.DataFrame(zip(dates,active,recovered,death),columns=['dates','active','recovered','death'])

daily.loc[14,['dates']]='2020-03-11'
daily.loc[4,['dates']]='2020-03-01'

daily=daily.iloc[4:]
daily=daily.reset_index().drop('index',axis=1)

daily['confirmed']=daily['active']+daily['recovered']+daily['death']

daily['dates'] = daily['dates'].apply(parse_date)

daily_records = daily.to_dict('records')

daily_instances = [Daily(
    date = record['dates'],
    confirmed = record['confirmed'],
    active = record['active'],
    recovered = record['recovered'],
    death = record['death'],
    source = 'wikipedia',
) for record in daily_records]

print('script suppressed!')

#Daily.objects.bulk_create(daily_instances)

#print('success!')