from state import GameState
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from load_prompt import load_prompt
from langchain_core.output_parsers import StrOutputParser,JsonOutputParser

def speak(state: GameState):
    role = state['next_speaker']
    roles_str = ','.join(state['roles'])
    chat_history = state['chat_history']
    history = ""
    for chat in chat_history:
        history += f"{chat[0]}: {chat[1]}\n"
    llm = ChatOpenAI(model="glm-4",  temperature=0.8)
    role_prompt = ChatPromptTemplate.from_template(load_prompt("prompt/role.prompt"))
    chain = role_prompt|llm|StrOutputParser()
    rsp = chain.stream({"role": role, "roles": roles_str, "history": history})
    output = ''
    print(role+':', end='', flush=True)
    for token in rsp:
        output += token
        print(token, end='', flush=True)
    print()
    print("---------------------------")
    state['chat_history'].append((role, output))
    return state

def vote(state: GameState):
    role = state['next_speaker']
    roles_str = ','.join(state['roles'])
    chat_history = state['chat_history']
    history = ""
    for chat in chat_history:
        history += f"{chat[0]}: {chat[1]}\n"
    llm = ChatOpenAI(model="glm-4",  temperature=0.01)
    vote_prompt = ChatPromptTemplate.from_template(load_prompt("prompt/vote.prompt"))
    chain = vote_prompt|llm|JsonOutputParser()
    output = chain.invoke({"role": role, "roles": roles_str, "history": history})
    state['vote_store'].append((role, output))
    return state

def role_play(state: GameState):
    stage = state['stage']
    if stage == 'speak':
        return speak(state)
    elif stage == 'vote':
        return vote(state)
    