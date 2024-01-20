# -*- coding: UTF-8 -*- 
import requests
from bs4 import BeautifulSoup

def search_article(artName):
    url = 'https://www.sci-hub.ren/'
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding':'gzip, deflate, br',
    'Content-Type':'application/x-www-form-urlencoded',
    'Content-Length':'123',
    'Origin':'https://www.sci-hub.ren',
    'Connection':'keep-alive',
    'Upgrade-Insecure-Requests':'1'}
    data = {'sci-hub-plugin-check':'',
    'request':artName}
    res = requests.post(url, headers=headers, data=data)
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')
    iframe = soup.find(id='pdf')
    if iframe == None:
        return ''
    else:
        downUrl = iframe['src']
        if 'http' not in downUrl:
            downUrl = 'https:'+downUrl
        return downUrl

def download_article(downUrl):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding':'gzip, deflate, br',
    'Connection':'keep-alive',
    'Upgrade-Insecure-Requests':'1'}
    res = requests.get(downUrl, headers=headers)
    return res.content

def scihub_download(art_url, dst_path):
    downUrl = search_article(art_url)
    if downUrl == '':
        return 0
    else:
        print("url:", downUrl)
        pdf = download_article(downUrl)
        with open(dst_path, 'wb') as f:
            f.write(pdf)
        return 1
