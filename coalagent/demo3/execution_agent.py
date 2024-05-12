from langchain import hub
from langchain.agents import create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter
from langchain_core.runnables import  RunnablePassthrough,RunnableBranch,RunnableLambda
from tools import search_tool

# Get the prompt to use - you can modify this!
prompt = hub.pull("hwchase17/openai-functions-agent")
# Choose the LLM that will drive the agent
llm = ChatOpenAI(model="glm-4",  temperature=0.01,openai_api_base="http://localhost:8778/v1",openai_api_key="123")
# Construct the OpenAI Functions agent
# agent_runnable = create_openai_functions_agent(llm, tools, prompt)

# from langgraph.prebuilt import create_agent_executor

# agent_executor = create_agent_executor(agent_runnable, tools)

# 判断是否需要使用搜索引擎提示词
# 判断是否需要使用搜索工具
use_tool_prompt =  ChatPromptTemplate.from_template(
    """
以下内容是一个待执行任务的描述，
1.请根据任务描述判断执行该任务是否需要使用搜索引擎工具执行搜索操作，
2.任务描述包含用于检索的关键字，
如果同时满足上述两点要求，请返回true，否则返回false，直接回复true或者false，不要解释。\n
任务描述:{input}
""")
choose_tool_chain = {"use_search_tool":itemgetter("input") |use_tool_prompt|llm|StrOutputParser(),
                     "task":itemgetter("input")
                     }


# 如果需要使用搜索工具，则通过模型提取搜索内容,然后使用搜索工具搜索结果
get_search_query_prompt = ChatPromptTemplate.from_template(
    """
以下内容是一个待执行搜索任务的描述，请根据任务描述提取出用于进行搜索的关键字，请直接返回关键字，不要解释。\n
任务描述:{task}
""")
def get_answer(search_result):
    if "answer_box" in search_result:
        return search_result["answer_box"]
    else:
        return search_result["organic_results"]
    
search_with_tool ={
    "result":itemgetter("task") |get_search_query_prompt|llm|StrOutputParser()|RunnableLambda(search_tool.results)|RunnableLambda(get_answer)
}
# 如果不需要使用搜索工具，则直接使用模型提取内容
excute_task_by_llm_prompt = ChatPromptTemplate.from_template(
    """
以下内容是一个待执行搜索任务的描述，请根据任务描述执行相关任务并返回执行结果。\n
任务描述:{task}
""")
answer_by_llm = {"result":itemgetter("task") |excute_task_by_llm_prompt|llm|StrOutputParser()}

branch = RunnableBranch(
        (lambda x:x["use_search_tool"] == 'true', search_with_tool),
        answer_by_llm
    )



# 创建chain
agent_executor = RunnablePassthrough()|choose_tool_chain|branch



