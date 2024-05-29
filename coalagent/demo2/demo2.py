from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import requests
import os
import asyncio
from bs4 import BeautifulSoup

from state import GraphState

from getcoal import get_coal_data

BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, os.pardir)))

def load_prompt(path):
    path =os.path.join(BASE_DIR,path)
    with open( path, 'r', encoding='utf-8') as f:
        return f.read()

# 数据采集
def collect_title_list(state: GraphState):
    print("---collect_title_list---")
    return {'keys':{'article_list' : get_coal_data(max_page=5)}}

# 数据去重与过滤
def data_filter(state: GraphState):
    # 分批处理，每50个标题提交一次
    print("---data_filter---")
    article_list = state['keys']["article_list"]
    filtered_title_list = []
    filtered_article_list  = []
    for i in range(0, len(article_list), 50):
        batch = [title['Title'] for title in article_list[i:i+50]]
        filtered_titles = filter_title(batch)
        filtered_title_list.extend(filtered_titles)
    # filtered_title_list = filter_title(filtered_title_list)
    for articl in article_list:
        if articl['Title'] in filtered_title_list:
            filtered_article_list.append(articl)
    return {'keys':{'filtered_article_list' : filtered_article_list}}

def group_data(state: GraphState):
    print("---group_data---")
    article_list = state['keys']["filtered_article_list"]
    grouped_data = group_data_by_keyword(article_list)
    return {'keys':{'grouped_data' : grouped_data}}

# 汇总分组数据
def summarize_group_data(state: GraphState):
    print("---summarize_group_data---")
    grouped_data = state['keys']["grouped_data"]
    summarized_data = summarize_group_data_by_keyword(grouped_data)
    return {'keys':{'summarized_data' : summarized_data}}

# 将汇总数据可视化
def visualize_summarized_data(state: GraphState):
    print("---visualize_summarized_data---")
    summarized_data = state['keys']["summarized_data"]
    for data in summarized_data:
        data_visualize(data)
        
    

def summarize_group_data_by_keyword(grouped_data):
    chat = ChatOpenAI(model="glm-4",  temperature=0,openai_api_base="http://localhost:8778/v1",openai_api_key="123")
    prompt_str = load_prompt('demo2/prompt/summarize_group_data.prompt')
    summarize_group_data = []
    for group in grouped_data:
        articles = group['articles']
        set_content(articles)
        content_list = [article['Content'] for article in articles]
        content_list_str = '\n'.join(content_list)
        prompt_tmp = prompt_str.replace("{input}", content_list_str)
        chain = chat | JsonOutputParser()
        group_csv = chain.invoke(prompt_tmp)
        summarize_group_data.append(group_csv)
    return summarize_group_data
    


def group_data_by_keyword(article_list):
    # 将文章列表转换为以文章名为key的字典 键为文章标题，值为文章内容
    article_dict = {article['Title']: article for article in article_list}
    title_list = [title['Title'] for title in article_list]
    title_list_str = '\n'.join(title_list)
    prompt_str = load_prompt('demo2/prompt/group_tilte.prompt')
    prompt_str = prompt_str.replace("{input}", title_list_str)
    chat = ChatOpenAI(model="glm-4",  temperature=0,openai_api_base="http://localhost:8778/v1",openai_api_key="123")
    chain =  chat | JsonOutputParser() 
    grouped_titles = chain.invoke(prompt_str)
    for group in grouped_titles:
        titles = group['titles']
        articles = []
        for title in titles:
            if title in article_dict:
                articles.append(article_dict[title])
        group['articles'] = articles
    return grouped_titles

def filter_title(batch):
    result_str = '\n'.join(batch) 
    prompt = PromptTemplate.from_template(load_prompt('demo2/prompt/data_filter.prompt'))
    chat = ChatOpenAI(model="glm-4",  temperature=0,openai_api_base="http://localhost:8778/v1",openai_api_key="123")
    chain = prompt | chat | JsonOutputParser()
    filtered_titles = chain.invoke({'input': result_str})
    return filtered_titles

def set_content(articles):
    for article in articles:
        link = article['Link']
        # 访问每一个链接，提取文章内容
        r = requests.get(link)
        s = BeautifulSoup(r.text, 'html.parser')
        content = s.select_one('div.content').get_text().strip()
        article['Content'] =  content
        
def data_visualize(raw_data):
    title = raw_data['title']
    content = raw_data['content']
    # 将content写入文件
    with open(f'{title}.csv', 'w', encoding='utf-8') as f:
        f.write(content)
    # import pandas as pd
    # import matplotlib.pyplot as plt
    # import io
    # title = raw_data['title']
    # content = raw_data['content']
    # data = pd.read_csv(io.StringIO(content), sep=",")
    
    # # 计算柱状图的宽度和间距
    # width = 0.35  # 每个柱状图的宽度
    # x_pos = range(len(data['Year-Month']))  # x 轴位置

    # fig, ax1 = plt.subplots()
    # ax2 = ax1.twinx()  # 创建共享 x 轴的第二个 y 轴

    # # 绘制“当月止累计”，“同比增加”的柱状图
    # ax1.bar([x - width/2 for x in x_pos], data['当月止累计'], width, label='当月止累计')
    # ax1.bar([x + width/2 for x in x_pos], data['同比增加'], width, label='同比增加')

    # # 绘制折线图 (growthRate)
    # ax2.plot(x_pos, data['增长率%'], color='red', marker='o', label='增长率')

    # # 设置坐标轴标签和标题
    # ax1.set_xlabel('Year-Month')
    # ax1.set_ylabel('数量', color='blue')
    # ax2.set_ylabel('增长率 (%)', color='red')
    # plt.title(title)

    # # 设置 x 轴刻度标签
    # ax1.set_xticks(x_pos)
    # ax1.set_xticklabels(data['Year-Month'])

    # # 添加图例
    # ax1.legend(loc='upper left')
    # ax2.legend(loc='upper right')

    # # 显示网格
    # ax1.grid(True)

    # plt.show()
    

        
from langgraph.graph import END, StateGraph
from state import GraphState 
    
def demo2():    
    workflow = StateGraph(GraphState)

    # Define the nodes
    workflow.add_node("collect_title_list", collect_title_list)  
    workflow.add_node("data_filter", data_filter) 
    workflow.add_node("group_data", group_data)  
    workflow.add_node("summarize_group_data", summarize_group_data)
    workflow.add_node("visualize_summarized_data", visualize_summarized_data)    

    # Build graph
    workflow.set_entry_point("collect_title_list")
    workflow.add_edge("collect_title_list", "data_filter")
    workflow.add_edge("data_filter", "group_data")
    workflow.add_edge("group_data", "summarize_group_data")
    workflow.add_edge("summarize_group_data", "visualize_summarized_data")
    workflow.add_edge("visualize_summarized_data", END)

    # Compile
    app = workflow.compile()

    #print(app.invoke({'keys':{}}))

    async def print_event():
        async for event in app.astream({'keys':{}}):
            for k, v in event.items():
                if k != "__end__":
                    print(v)

    asyncio.run(print_event())

# import os
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_PROJECT"]="coal-agent" 
demo2()
