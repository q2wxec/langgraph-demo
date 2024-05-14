from langchain import hub
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter
from langchain_core.runnables import  RunnablePassthrough,RunnableBranch,RunnableLambda
from tools import search_tool
from load_prompt import load_prompt

# Choose the LLM that will drive the agent
llm = ChatOpenAI(model="glm-4",  temperature=0.01,openai_api_base="http://localhost:8778/v1",openai_api_key="123")

# 判断是否需要使用搜索引擎提示词
# 判断是否需要使用搜索工具
use_tool_prompt =  ChatPromptTemplate.from_template(load_prompt("demo3/prompt/tool_choose.prompt"))
choose_tool_chain = {"use_search_tool":itemgetter("input") |use_tool_prompt|llm|StrOutputParser(),
                     "task":itemgetter("input")
                     }


# 如果需要使用搜索工具，则通过模型提取搜索内容,然后使用搜索工具搜索结果
get_search_query_prompt = ChatPromptTemplate.from_template(load_prompt("demo3/prompt/search_query.prompt"))
def get_answer(search_result):
    if "answer_box" in search_result:
        return search_result["answer_box"]
    elif "organic_results" in search_result:
        return search_result["organic_results"]
    else:
        return search_result
    
def add_site(search_query):
    return search_query+' site:coalchina.org.cn'
    
search_with_tool ={
    "result":itemgetter("task") |get_search_query_prompt|llm|StrOutputParser()
    |RunnableLambda(add_site)|RunnableLambda(search_tool.results)|RunnableLambda(get_answer)
}
# 如果不需要使用搜索工具，则直接使用模型提取内容
excute_task_by_llm_prompt = ChatPromptTemplate.from_template(load_prompt("demo3/prompt/excute_by_llm.prompt"))
answer_by_llm = {"result":itemgetter("task") |excute_task_by_llm_prompt|llm|StrOutputParser()}

get_html_by_tool = {}

branch = RunnableBranch(
        (lambda x:x["use_search_tool"] == '1', search_with_tool),
        (lambda x:x["use_search_tool"] == '2', get_html_by_tool),
        answer_by_llm
    )


# 创建chain
agent_executor = RunnablePassthrough()|choose_tool_chain|branch



