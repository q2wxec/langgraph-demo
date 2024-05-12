from langchain_core.pydantic_v1 import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

class Response(BaseModel):
    """Response to user."""
    end: bool
    response: str
        
    
parser = PydanticOutputParser(pydantic_object=Response)

replanner_prompt = ChatPromptTemplate.from_template(
"""
目标如下:
{input}

你的原计划如下:

{plan}

你已经执行了以下步骤:
{past_steps}


如果不需要更多的步骤，并且您可以返回给用户，则将end设置为true并使用该值进行响应，否则设置end为false
将计划以Json格式输出如下，不要更改格式：
{{"end":true,"response":"the answer for user's question"}}

"""
)


llm = ChatOpenAI(model="glm-4",  temperature=0.01,openai_api_base="http://localhost:8778/v1",openai_api_key="123")

result_checker = replanner_prompt|llm|parser

