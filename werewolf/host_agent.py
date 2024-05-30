from state import GameState
import random
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from load_prompt import load_prompt
from langchain_core.output_parsers import StrOutputParser

def gen_and_dispatch_role(state: GameState):
    roles = state['roles']
    first_init = not roles
    # 初始化角色
    if first_init:
        roles = {"亚里士多德","莫扎特","达芬奇","成吉思汗","克利奥帕特拉七世"}  
        state['roles'] = roles
        # 从roles中随机选取一个确定人类玩家角色
        human_role = random.choice(roles)
        state['human_role'] = human_role
    # 初始化待发言池
    state['waiting'] = roles
    # 选取下一个发言的角色，并从待发言池移除
    next = random.choice(state['waiting'])
    state['next_speaker'] = next
    state['waiting'].discard(next)
    # 修改游戏状态
    state['stage'] = 'speak'
    # 初始化聊天记录及投票
    # state['chat_history'] = []
    state['vote_store'] = []
    return

def ask_for_speak(state: GameState):
    # 如果待发言池为空，则进入投票阶段
    if len(state['waiting']) == 0:
        state['waiting'] = state['roles']
        state['stage'] = 'vote'
        return
    chat_history = state['chat_history']
    last_chat = chat_history[-1]
    last_chat_str = last_chat[0]+': '+last_chat[1]
    waiting_roles_str = ','.join(state['waiting'])
    llm = ChatOpenAI(model="glm-4",  temperature=0.01)
    choose_prompt = ChatPromptTemplate.from_template(load_prompt("prompt/choose_speaker.prompt"))
    chain = choose_prompt|llm|StrOutputParser()
    role_chosen = chain.invoke({"history": last_chat_str, "waitings": waiting_roles_str})
    if role_chosen in state['waiting']:
        state['waiting'].discard(role_chosen)
        state['next_speaker'] = role_chosen
    else:
        next = random.choice(state['waiting'])
        state['next_speaker'] = next
        state['waiting'].discard(next)
    return

def ask_for_vote(state: GameState):
    if len(state['waiting']) == 0:
        human_role = state['human_role']
        # 统计票数决定是否结束游戏
        vote_store = state['vote_store']
        human_vote_count = 0
        for vote in vote_store:
            vote_role = vote[1]['vote']
            if vote_role == human_role:
                human_vote_count += 1
        totle_votes = len(state['roles'])
        # 如果人类角色票数超过一半，结束游戏
        if human_vote_count > totle_votes / 2:
            state['stage'] = 'end'
            print("AI win!")
            print("投票详情如下："+vote_store)
        else:
            gen_and_dispatch_role(state)
        return
    next = random.choice(state['waiting'])
    state['next_speaker'] = next
    state['waiting'].discard(next)

def host(state: GameState):
    stage = state['stage']
    if stage == 'start':
        gen_and_dispatch_role(state)
    elif stage == 'speak':
        ask_for_speak(state)
    elif stage == 'vote':
        ask_for_vote(state)
    return