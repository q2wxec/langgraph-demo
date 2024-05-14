from langchain_core.pydantic_v1 import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from plan_agent import Plan
from langchain_core.output_parsers import PydanticOutputParser
from load_prompt import load_prompt

class Response(BaseModel):
    """Response to user."""

    response: str
        
parser = PydanticOutputParser(pydantic_object=Plan)    

replanner_prompt = ChatPromptTemplate.from_template(load_prompt('demo3/prompt/replan.prompt'))


llm = ChatOpenAI(model="glm-4",  temperature=0.01,openai_api_base="http://localhost:8778/v1",openai_api_key="123")

replanner = replanner_prompt|llm|parser

