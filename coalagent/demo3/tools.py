
from langchain_community.utilities import SearchApiAPIWrapper
import requests
from bs4 import BeautifulSoup
search_tool = SearchApiAPIWrapper()

def get_html(url):
    # 保存所有的文章信息，包括标题，链接，时间和内容
    # 发送请求并解析页面

    # 访问每一个链接，提取文章内容
    r = requests.get(url)
    s = BeautifulSoup(r.text, 'html.parser')
    content = s.get_text().strip()
    
    # 存储每一个文章的信息
    return {
        'Link': url,
        'content': content,
        # 'Content': content,
    }
    