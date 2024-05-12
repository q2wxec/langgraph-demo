from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser

class Plan(BaseModel):
    """Plan to follow in future"""

    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )
    
from langchain_core.prompts import ChatPromptTemplate

parser = PydanticOutputParser(pydantic_object=Plan)

planner_prompt = ChatPromptTemplate.from_template(
        """对于给定的目标，提出一个简单的循序渐进的计划\
            这个计划应该包括单独的任务，如果执行得当，就会得到正确的答案。不要添加任何多余的步骤\
            最后一步的结果应该是最终的答案。确保每个步骤都包含所需的所有信息，不要跳过步骤。在执行具体操作时，你能使用的工具只有搜索引擎，请将其考虑在内。
            将计划以Json格式输出如下，key为steps，value是一个str的数组，不要更改格式：

    {{"steps":["1.敲门","2.开门"]}}

    {objective}"""
)

llm = ChatOpenAI(model="glm-4",  temperature=0.01,openai_api_base="http://localhost:8778/v1",openai_api_key="123")

planner= planner_prompt|llm|parser
