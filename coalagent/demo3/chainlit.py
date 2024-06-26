import chainlit as cl
from demo3 import workflow



@cl.on_chat_start
def start():
    app = workflow.compile()
    cl.user_session.set("agent", app)


@cl.on_message
async def main(message: cl.Message):
    agent = cl.user_session.get("agent")  # type
    content = message.content
    config = {"recursion_limit": 1000,"callbacks":[cl.AsyncLangchainCallbackHandler()]}
    inputs = {"input": content}
    res = await agent.ainvoke(inputs,config)

    # await cl.Message(content=res).send()