from operator import itemgetter

from langchain_core.output_parsers import StrOutputParser,JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from state import GraphState


def generate(state: GraphState):
    """
    Generate a code solution based on LCEL docs and the input question
    with optional feedback from code execution tests

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """

    ## State
    state_dict = state["keys"]
    question = state_dict["question"]
    iter = state_dict["iterations"]

    ## LLM
    model = ChatOpenAI(temperature=0, model="spark-3.1", streaming=True,openai_api_base="http://localhost:8778/v1",openai_api_key="123")

    ## Prompt
    template = """You are a coding assistant with expertise in Python\n 
        Answer the user question with Python code. \n
        Ensure any code you provide can be executed with all required imports and variables defined. \n
        Structure your answer with a description of the code solution. \n
        Then list the imports. And finally list the functioning code block. \n
        Here is the user question: \n --- --- --- \n {question}"""

    ## Generation
    if "correct" in state_dict and state_dict["correct"] == False:
        print("---RE-GENERATE SOLUTION w/ ERROR FEEDBACK---")

        feedback = state_dict["feedback"]
        code_solution = state_dict["generation"]

        # Udpate prompt
        addendum = """  \n --- --- --- \n You previously tried to solve this problem. \n Here is your solution:  
                    \n --- --- --- \n {generation}  \n --- --- --- \n  Here is the instruction from the code mentor
                    :  \n --- --- --- \n {feedback}  \n --- --- --- \n Please re-try to answer this. 
                    Structure your answer with a description of the code solution. \n Then list the imports. 
                    And finally list the functioning code block. Structure your answer with a description of 
                    the code solution. \n Then list the imports. And finally list the functioning code block. 
                    \n Here is the user question: \n --- --- --- \n {question}"""
        template = template + addendum

        # Prompt
        prompt = PromptTemplate(
            template=template,
            input_variables=["question", "generation", "feedback"],
        )

        # Chain
        chain = (
            {
                "question": itemgetter("question"),
                "generation": itemgetter("generation"),
                "feedback": itemgetter("feedback"),
            }
            | prompt
            | model
            | StrOutputParser()
        )

        code_solution = chain.invoke(
            {"question": question, "generation": code_solution, "feedback": feedback}
        )

    else:
        print("---GENERATE SOLUTION---")

        # Prompt
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"],
        )

        # Chain
        chain = (
            {
                "question": itemgetter("question"),
            }
            | prompt
            | model
            | StrOutputParser()
        )

        code_solution = chain.invoke({"question": question})

    iter = iter + 1
    print("code_solution:"+code_solution)
    return {
        "keys": {"generation": code_solution, "question": question, "iterations": iter}
    }





def code_mentor(state: GraphState):
    """
    Check code block execution

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, error
    """

    ## State
    print("---CHECKING CODE ---")
    state_dict = state["keys"]
    question = state_dict["question"]
    code_solution = state_dict["generation"]
    
    ## Prompt
    template = """You are a coding mentor with expertise in Python\n 
        Your student previously tried to solve user code problem.
        Here is the user question: \n --- --- --- \n {question}\n
        Here is your student solution: \n --- --- --- \n {generation}\n
        Please identify if your student solution is right or wrong. \n
        If wrong, please provide feedback on how to improve your student solution. \n
        If right, please provide feedback that the code is correct. \n
        Please provide feedback in JSON format  with 'correct' and 'feedback' keys.. \n
        Here is the output format example: \n --- --- --- \n
        If right:\n
            "correct": true,
        \n
        If wrong:\n
            "correct": false,
            "feedback": "Your have to fix the following error to make the code work...."
        \n
        """
    ## LLM
    model = ChatOpenAI(temperature=0, model="spark-3.1", streaming=True,openai_api_base="http://localhost:8778/v1",openai_api_key="123")
    # Prompt
    prompt = PromptTemplate(
            template=template,
            input_variables=["question", "generation"],
        )
    
    # Chain
    chain = (
            {
                "question": itemgetter("question"),
                "generation": itemgetter("generation"),
            }
            | prompt
            | model
            | JsonOutputParser()
        )
    mentor = chain.invoke(
            {"question": question, "generation": code_solution}
        )
    print("mentor:"+str(mentor))
    return {
        "keys": {
            "generation": code_solution,
            "question": question,
            "feedback": mentor['feedback'],
            "correct": mentor['correct'],
            "iterations": iter,
        }
    }




def decide_to_finish(state: GraphState):
    """
    Determines whether to finish (re-try code 3 times.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---DECIDE TO FINISH ---")
    state_dict = state["keys"]
    correct = state_dict["correct"]
    iter = state_dict["iterations"]

    if correct or iter == 3:
        # All documents have been filtered check_relevance
        # We will re-generate a new query
        print("---DECISION: FINISH---")
        return "end"
    else:
        # We have relevant documents, so generate answer
        print("---DECISION: RE-TRY SOLUTION---")
        return "generate"