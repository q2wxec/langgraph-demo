
from state import GameState
from host_agent import gen_and_dispatch_role,ask_for_speak,ask_for_vote,count_vote
from role_agent import speak as role_speak,vote as role_vote
from human_agent import speak as human_speak,vote as human_vote

from langgraph.graph import StateGraph, END

# def route_condition(state: GameState):
#     if state["stage"] == "end":
#         return END
#     role = state['next_speaker']
#     human = state["human_role"]
#     if role == human:
#         return "human_play"
#     else:
#         return "role_play"

def speak_route(state: GameState):
    role = state['next_speaker']
    human = state["human_role"]
    if not role:
        return "host_vote"
    elif role == human:
        return "human_speak"
    else:
        return "role_speak"

def vote_route(state: GameState):
    role = state['next_speaker']
    human = state["human_role"]
    if not role:
        return "count_vote"
    elif role == human:
        return "human_vote"
    else:
        return "role_vote"

def end_route(state: GameState):
    end = state["end"]
    if end:
        return END
    else:
        return "start"

workflow = StateGraph(GameState)

# host step

workflow.add_node("start", gen_and_dispatch_role)

workflow.add_node("host_speak", ask_for_speak)

workflow.add_node("host_vote", ask_for_vote)

workflow.add_node("count_vote", count_vote)

# role_play step
workflow.add_node("role_speak", role_speak)

workflow.add_node("role_vote", role_vote)

# human_play step
workflow.add_node("human_speak", human_speak)

workflow.add_node("human_vote", human_vote)

# workflow
workflow.set_entry_point("start")

workflow.add_edge("start", "host_speak")

workflow.add_edge("role_speak", "host_speak")

workflow.add_edge("human_speak", "host_speak")

workflow.add_edge("role_vote", "host_vote")

workflow.add_edge("human_vote", "host_vote")

workflow.add_conditional_edges(
    "host_speak",
    speak_route,
     {"human_speak": "human_speak","role_speak": "role_speak", "host_vote": "host_vote"},
)

workflow.add_conditional_edges(
    "host_vote",
    vote_route,
     {"role_vote": "role_vote","human_vote": "human_vote", "count_vote": "count_vote"},
)

workflow.add_conditional_edges(
    "count_vote",
    end_route,
     {"start": "start", END: END},
)

# app = workflow.compile()

config = {"recursion_limit": 1000}
inputs = {"round":0,"end":False}

# import asyncio
# async def start():
#     await app.ainvoke(inputs,config)

# asyncio.run(start())

# import os
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_PROJECT"]="wolf-game"
#app.invoke(inputs,config)

# 流程图片打印
# from langchain_core.runnables.graph import MermaidDrawMethod
# from PIL import Image
# from io import BytesIO

# image_stream = BytesIO(
#     app.get_graph().draw_mermaid_png(
#         draw_method=MermaidDrawMethod.API,
#     )
# )
# img = Image.open(image_stream)
# img.show()

# import asyncio
# async def print_event():
#     async for event in app.astream_events(inputs, config=config, version="v1"):
#         kind = event["event"]
#         if kind == "on_chat_model_stream":
#             content = event["data"]["chunk"].content
#             if content:
#                 # Empty content in the context of OpenAI or Anthropic usually means
#                 # that the model is asking for a tool to be invoked.
#                 # So we only print non-empty content
#                 print(content, end="|")
#         else:
#             print("-")

# asyncio.run(print_event())