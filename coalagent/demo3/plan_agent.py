from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from load_prompt import load_prompt

class Plan(BaseModel):
    """Plan to follow in future"""

    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )
    
from langchain_core.prompts import ChatPromptTemplate

parser = PydanticOutputParser(pydantic_object=Plan)

planner_prompt = ChatPromptTemplate.from_template(load_prompt("demo3/prompt/plan.prompt"))

llm = ChatOpenAI(model="glm-4",  temperature=0.01,openai_api_base="http://localhost:8778/v1",openai_api_key="123")

planner= planner_prompt|llm|parser
