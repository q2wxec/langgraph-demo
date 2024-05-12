from langchain_core.pydantic_v1 import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from plan_agent import Plan
from langchain_core.output_parsers import PydanticOutputParser

class Response(BaseModel):
    """Response to user."""

    response: str
        
parser = PydanticOutputParser(pydantic_object=Plan)    

replanner_prompt = ChatPromptTemplate.from_template(
    """对于给定的目标，提出一个简单的循序渐进的计划\
    这个计划应该包括单独的任务，如果执行得当，就会得到正确的答案。不要添加任何多余的步骤\
    最后一步的结果应该是最终的答案。确保每个步骤都包含所需的所有信息，不要跳过步骤。在执行具体操作时，你能使用的工具只有搜索引擎，请将其考虑在内。
目标如下:
{input}

你的原计划如下:

{plan}

你已经执行了以下步骤:
{past_steps}

请基于以上内容更新你的计划。只在计划中添加仍然需要完成的步骤。不要将以前完成的步骤作为计划的一部分返回。
 将计划以Json格式输出如下，key为steps，value是一个str的数组，不要更改格式：
{{"steps":["1.敲门","2.开门"]}}

"""
)


llm = ChatOpenAI(model="glm-4",  temperature=0.01,openai_api_base="http://localhost:8778/v1",openai_api_key="123")

replanner = replanner_prompt|llm|parser

