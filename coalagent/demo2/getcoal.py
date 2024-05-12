import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# import pandas as pd

# 文章列表页面

base_url =  'https://www.coalchina.org.cn/index.php?m=content&c=index&a=lists&catid=69&page='

def get_coal_data(base_url = base_url,max_page=None):

    # 保存所有的文章信息，包括标题，链接，时间和内容
    articles = []

    page = 1
    # 循环遍历url_dict
    while True:
        if max_page and page > max_page:
            break
        url = base_url + str(page)
        page += 1
        # 发送请求并解析页面
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')

        # 找到所有的文章条目
        # 找到class为main的div标签，再找到ul标签，再找到li标签

        items = soup.select('div.main > div > ul > li')
        
        if not items:
            break
            
        # 遍历所有的文章
        for item in items:
            # 提取出日期，链接和标题
            ditem = item.select_one('span.rt')
            if not ditem:
                continue
            date = ditem.get_text()
            
            title = item.select_one('a').get_text()
            link = item.select_one('a')['href']

            # 访问每一个链接，提取文章内容
            # r = requests.get(link)
            # s = BeautifulSoup(r.text, 'html.parser')
            # content = s.select_one('div.content').get_text().strip()
            
            # 存储每一个文章的信息
            articles.append({
                'Title': title,
                'Link': link,
                'Date': date,
                # 'Content': content,
            })
    return articles
    