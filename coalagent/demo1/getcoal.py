import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# import pandas as pd

# 文章列表页面
default_url_dict = {
    '头版新闻': 'https://www.coalchina.org.cn/list-10-1.html',
    '经济运行':'https://www.coalchina.org.cn/list-20-1.html',
    '信息化':'https://www.coalchina.org.cn/index.php?m=content&c=index&a=lists&catid=286',
    '行业新闻':'https://www.coalchina.org.cn/index.php?m=content&c=index&a=lists&catid=12',
}



def get_article_content(day_range=2,url_dict=default_url_dict):
    
    dates = [datetime.now().date() - timedelta(days=i) for i in range(day_range)][::-1]

    date_list =  [d.strftime("%Y-%m-%d") for d in dates]

    # 保存所有的文章信息，包括标题，链接，时间和内容
    articles = []

    # 循环遍历url_dict
    for url_type, base_url in url_dict.items():
        # 发送请求并解析页面
        res = requests.get(base_url)
        soup = BeautifulSoup(res.text, 'html.parser')

        # 找到所有的文章条目
        # 找到class为main的div标签，再找到ul标签，再找到li标签

        items = soup.select('div.main > div > ul > li')

        # 遍历所有的文章
        for item in items:
            # 提取出日期，链接和标题
            ditem = item.select_one('span.rt')
            if not ditem:
                continue
            date = ditem.get_text()
            # 过滤出指定日期的文章
            if date in date_list:
                title = item.select_one('a').get_text()
                link = item.select_one('a')['href']

                # 访问每一个链接，提取文章内容
                r = requests.get(link)
                s = BeautifulSoup(r.text, 'html.parser')
                content = s.select_one('div.content').get_text().strip()
                
                # 存储每一个文章的信息
                articles.append({
                    'Title': title,
                    'Link': link,
                    'Date': date,
                    'Content': content,
                    'Type': url_type
                })
    return articles
    # # 输出为DataFrame格式
    # df = pd.DataFrame(articles)
    # # 保存为csv文件
    # df.to_csv('coalchina.csv', index=False)

