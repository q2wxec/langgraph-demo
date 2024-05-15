from langchain_core.pydantic_v1 import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from plan_agent import Plan
from langchain_core.output_parsers import PydanticOutputParser,StrOutputParser
from langchain_core.runnables import RunnableLambda
from load_prompt import load_prompt

class Response(BaseModel):
    """Response to user."""

    response: str
        
parser = PydanticOutputParser(pydantic_object=Plan)    

replanner_prompt = ChatPromptTemplate.from_template(load_prompt('demo3/prompt/replan.prompt'))


llm = ChatOpenAI(model="glm-4",  temperature=0.01,openai_api_base="http://localhost:8778/v1",openai_api_key="123")

import json

def is_json(result_str):
    try:
        json.loads(result_str)
        return True
    except (json.JSONDecodeError, ValueError):
        return False
def check_json(result_str):
    # 将result转换为字符串
    # 判断result_str是否满足json格式
    if is_json(result_str):
        return result_str
    else:
        fix_json_prompt = ChatPromptTemplate.from_template(load_prompt('demo3/prompt/json_fix.prompt'))
        chain = fix_json_prompt|llm
        return chain.invoke({"input":result_str})
replanner = replanner_prompt|llm|StrOutputParser()|RunnableLambda(check_json)|parser

