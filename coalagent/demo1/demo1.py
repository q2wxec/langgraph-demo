from getcoal import get_article_content



from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import os
# import pandas as pd
BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, os.pardir)))

def load_prompt(path):
    path =os.path.join(BASE_DIR,path)
    with open( path, 'r', encoding='utf-8') as f:
        return f.read()
    
def demo1(day_range):
    print("---开始采集文章---")
    articles = get_article_content(day_range = day_range)
    
    prompt = PromptTemplate.from_template(load_prompt('demo1/prompt/summarize.prompt'))
    chat = ChatOpenAI(model="qwen-plus",  temperature=0,openai_api_base="http://localhost:8778/v1",openai_api_key="123")
    chain = prompt | chat | StrOutputParser()

    print("---开始文章总结---")
    for article in articles:
        try:
            title = article['Title']
            content = article['Content']
            summarize = chain.invoke({"title": title,"content":content})
            article['Summary'] = summarize
        except Exception as e:
            continue

    # # 输出为DataFrame格式
    # df = pd.DataFrame(articles)
    # # 保存为csv文件
    # df.to_csv('coalchina.csv', index=False)
    # 将article 按Type分类，转化为字典
    articles_dict = {}
    for article in articles:
        type = article['Type']
        if type not in articles_dict:
            articles_dict[type] = []
        articles_dict[type].append(article)
    # 输出总结到文件
    print("---开始输出总结---")
    output = '## 以下为今日咨询\n'
    for type, articles in articles_dict.items():
        output+=f'### {type}：\n'
        i = 1
        for article in articles:
            if 'Summary' in article:
                summary = article['Summary']
            else:
                summary = "触发敏感词无法总结！"
            link = article['Link']
            title = article['Title']
            output+=f'- {i}.{summary},[{title}]({link})\n'
            i += 1  # 记得递增计数器i

    # 将output内容写入文件
    with open('daily_summary.md', 'a', encoding='utf-8') as file:
        file.write(output)

demo1(2)




