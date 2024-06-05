import chainlit as cl
from wolf_game import app


@cl.on_chat_start
def start():
    cl.user_session.set("agent", app)


@cl.on_message
async def main(message: cl.Message):
    agent = cl.user_session.get("agent")  # type
    config = {"recursion_limit": 1000,"callbacks":[cl.AsyncLangchainCallbackHandler()]}
    inputs = {"round":0,"end":False}
    res = await agent.ainvoke(inputs,config)

    # await cl.Message(content=res).send()