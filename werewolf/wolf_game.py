
from state import GameState
from host_agent import host
from role_agent import role_play
from human_agent import human_play

from langgraph.graph import StateGraph, END

def route_condition(state: GameState):
    if state["stage"] == "end":
        return END
    role = state['next_speaker']
    human = state["human_role"]
    if role == human:
        return "human_play"
    else:
        return "role_play"

workflow = StateGraph(GameState)

workflow.add_node("host", host)

# role_play step
workflow.add_node("role_play", role_play)

# human_play step
workflow.add_node("human_play", human_play)

workflow.set_entry_point("host")

# From plan we go to agent
workflow.add_edge("role_play", "host")

workflow.add_edge("human_play", "host")

workflow.add_conditional_edges(
    "host",
    route_condition,
     {"human_play": "human_play","role_play": "role_play", END: END},
)

app = workflow.compile()

# import asyncio
# async def start():
#     await app.ainvoke({"stage":"start","round":1})

# asyncio.run(start())
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"]="wolf-game"
app.invoke({"stage":"start","round":1})