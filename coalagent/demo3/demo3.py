
import asyncio
from state import PlanExecute
from plan_agent import planner
from replan_agent import replanner,Response
from execution_agent import agent_executor
from check_result_agent import result_checker

async def execute_step(state: PlanExecute):
    objective = state["input"]
    task = state["plan"][0]
    agent_response = await agent_executor.ainvoke({"objective":objective,"input": task, "chat_history": []})
    return {
        "past_steps": (task,agent_response["result"])
    }


async def plan_step(state: PlanExecute):
    plan = await planner.ainvoke({"objective": state["input"]})
    return {"plan": plan.steps}


async def replan_step(state: PlanExecute):
    output = await replanner.ainvoke(state)
    return {"plan": output.steps}

async def check_result(state: PlanExecute):
    resp = await result_checker.ainvoke(state)
    if resp.end:
        return {"response": resp.response}
    else:
        return {}

def should_end(state: PlanExecute):
    if "response" in state and state["response"].strip():
        return True
    else:
        return False

   
    
from langgraph.graph import StateGraph, END


workflow = StateGraph(PlanExecute)

# Add the plan node
workflow.add_node("planner", plan_step)

# Add the execution step
workflow.add_node("agent", execute_step)

# check_result step
workflow.add_node("checker", check_result)

# Add a replan node
workflow.add_node("replan", replan_step)

workflow.set_entry_point("planner")

# From plan we go to agent
workflow.add_edge("planner", "agent")

workflow.add_edge("agent", "checker")

# From agent, we replan
workflow.add_edge("replan", "agent")

workflow.add_conditional_edges(
    "checker",
    # Next, we pass in the function that will determine which node is called next.
    should_end,
    {
        # If `tools`, then we call the tool node.
        True: END,
        False: "replan",
    },
)

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
# app = workflow.compile()

# import os
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_PROJECT"]="Plan-and-execute"
# from langchain_core.messages import HumanMessage
# #请列举陕西省申报绿色矿山的明细要求?
# #山西省煤税目原矿税率现在是多少？
# #内蒙古自治区有哪些煤矿达到了智能化建设的标准?
# config = {"recursion_limit": 50}
# inputs = {"input": "内蒙古自治区有哪些煤矿达到了智能化建设的标准?"}
# print()
# async def print_event():
#     async for event in app.astream(inputs, config=config):
#         for k, v in event.items():
#             if k != "__end__":
#                 print(v)

# asyncio.run(print_event())
    


