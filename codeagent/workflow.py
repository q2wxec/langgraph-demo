from langgraph.graph import END, StateGraph
from graph import generate,code_mentor,decide_to_finish
from state import GraphState

workflow = StateGraph(GraphState)

# Define the nodes
workflow.add_node("generate", generate)  # generation solution
workflow.add_node("code_mentor", code_mentor)  # check imports

# Build graph
workflow.set_entry_point("generate")
workflow.add_edge("generate", "code_mentor")
workflow.add_conditional_edges(
    "code_mentor",
    decide_to_finish,
    {
        "end": END,
        "generate": "generate",
    },
)

# Compile
app = workflow.compile()

app.invoke({"keys":{"question":"如何实现归并排序算法？","iterations":0}})