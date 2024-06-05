from state import GameState
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from load_prompt import load_prompt
from langchain_core.output_parsers import StrOutputParser,JsonOutputParser
import chainlit as cl

async def speak(state: GameState):
    role = state['next_speaker']
    roles_str = ','.join(state['roles'])
    chat_history = state['chat_history']
    history = ""
    if chat_history:
        for chat in chat_history:
            history += f"{chat[0]}: {chat[1]}\n"
    llm = ChatOpenAI(model="glm-4",  temperature=0.8, streaming=True)
    role_prompt = ChatPromptTemplate.from_template(load_prompt("prompt/role.prompt"))
    chain = role_prompt|llm|StrOutputParser()
    rsp = chain.stream({"role": role, "roles": roles_str, "history": history})
    output = ''
    msg = cl.Message(content="")
    await msg.send()
    await msg.stream_token(role+':')
    for token in rsp:
        output += token
        await msg.stream_token(token)
    # print()
    # print("---------------------------")
    await msg.update()
    return {'chat_history':[(role, output)]}


async def vote(state: GameState):
    role = state['next_speaker']
    roles_str = ','.join(state['roles'])
    chat_history = state['chat_history']
    history = ""
    for chat in chat_history:
        history += f"{chat[0]}: {chat[1]}\n"
    llm = ChatOpenAI(model="glm-4",  temperature=0.01, streaming=True)
    vote_prompt = ChatPromptTemplate.from_template(load_prompt("prompt/vote.prompt"))
    chain = vote_prompt|llm|JsonOutputParser()
    output = await chain.ainvoke({"role": role, "roles": roles_str, "history": history})
    vote_store = state['vote_store']
    vote_store.append((role, output))
    return {'vote_store': vote_store}

# def role_play(state: GameState):
#     stage = state['stage']
#     if stage == 'speak':
#         return speak(state)
#     elif stage == 'vote':
#         return vote(state)
    