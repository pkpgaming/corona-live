
import requests, json, re, urllib.request, time

import pandas as pd
from bs4 import BeautifulSoup

from django.http import HttpResponse, JsonResponse
from django.utils.safestring import mark_safe
from django.shortcuts import render
from django.utils import timezone

from corona.models import Cache

#route functions
def home(req):
    t1 = time.time()
    cache_key = 'homepage'
    expiry = 5 
    cached_data = get_cache(cache_key, expiry)
    from_cache= 'true'

    if not cached_data:

        soup=get_mohfw()
        statewise=get_statewise(soup)
        info=get_info(soup)
        wiki=get_wiki()
        days=get_daily(wiki)
        tests=get_tests(wiki)

        cached_data = {
            'statewise': statewise,
            'info': info,
            'days': days,
            'tests': tests
        }

        save_cache(cache_key, cached_data)
        from_cache= 'false'
        
    t2 = time.time()
    compute = t2-t1
    return render(req,'home.html',{
        'data': mark_safe(json.dumps(cached_data)),
        'compute': compute,
        'from_cache': from_cache
    })

def ping(req):
    return HttpResponse('<h1>pong</h1>')

#services
def get_mohfw():
    url = "https://www.mohfw.gov.in/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def get_statewise(soup):
    tab=soup.find_all('tr')
    state=list()
    indian=list()
    foreign=list()
    discharged=list()
    death=list()
    for row in tab:
        lst=row.find_all('td')
        if(len(lst)==6):
            try:
                state.append((remove_html_tags(lst[1])))
                indian.append(get_count(remove_html_tags(lst[2])))
                foreign.append(get_count(remove_html_tags(lst[3])))
                discharged.append(get_count(remove_html_tags(lst[4])))
                death.append(get_count(remove_html_tags(lst[5])))
            except:
                pass

    data=pd.DataFrame(list(zip(state,indian,foreign,discharged,death)),columns=['state','indian','foreign','discharged','death'])
    data['total']=data['indian']+data['foreign']+data['discharged']+data['death']
    data.sort_values(by='total',axis=0,ascending=False,inplace=True)
    statewise = data.to_dict()
    info=dict()

    for ke in statewise:
        statewise[ke]=list(statewise[ke].values())

    return statewise

def get_info(soup):
    counts=soup.findAll("span", {"class": "icount"})
    info_labels=['passengers','infected','cured','death','migrated']
    info_counts=[remove_html_tags(x) for x in counts]
    info=dict(zip(info_labels,info_counts))
    return info

def get_wiki():
    wiki_url="https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_India"
    wiki_response=requests.get(wiki_url)
    wiki = BeautifulSoup(wiki_response.text, "html.parser")
    return wiki

def get_daily(wiki):
    counts=wiki.findAll("span", {"style":"width:2.45em; padding:0 0.3em 0 0; text-align:right; display:inline-block"})
    dates=wiki.findAll("td",{"colspan":"2","style":"padding-left:0.4em; padding-right:0.4em; text-align:center"})

    counts=[get_count(remove_html_tags(x)) for x in counts]
    dates=[remove_html_tags(x) for x in dates]

    daily=dict(zip(dates,counts))

    del daily['⋮']
    del daily['2020-01-30']
    del daily['2020-02-02']
    del daily['2020-02-03']
    daily['2020-03-01']=3
    daily['2020-03-11']=65
    days=dict()
    days["date"]=sorted(daily)
    days["infected"]=sorted(daily.values())

    return days

def get_tests(wiki):
    table = wiki.find("table",{"class":"wikitable plainrowheaders"})
    rows = table.find_all('td')

    tests = {
        "perm":rows[1].text.replace('\n', ''),
        "inds":rows[2].text.replace('\n', '').replace(",","")
    }

    return tests


def remove_html_tags(text):
    """Remove html tags from a string"""
    text=str(text)
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def get_count(text):
    text=str(text)
    num=int(re.findall(r'\d+', text)[0])
    return num

def save_cache(key,data):
    try:
        cache = Cache.objects.get(cache_key = key)
        cache.data = json.dumps(data)
    except Cache.DoesNotExist:
        cache = Cache(cache_key = key, data = json.dumps(data))
    cache.save()


def get_cache(key, expiry_time = None):
    try:
        cache = Cache.objects.get(cache_key = key)
        if not expiry_time or cache.updated_at + timezone.timedelta(minutes= expiry_time) > timezone.now():
            return json.loads(cache.data)
    except Cache.DoesNotExist:
        pass