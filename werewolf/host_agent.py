from state import GameState
import random
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from load_prompt import load_prompt
from langchain_core.output_parsers import StrOutputParser
import json

def gen_and_dispatch_role(state: GameState):
    roles = state['roles']
    round = state['round']
    first_init = not roles
    # 初始化角色
    if first_init:
        roles = {"亚里士多德","莫扎特","达芬奇","成吉思汗","克利奥帕特拉七世"}  
        state['roles'] = roles.copy()
        # 从roles中随机选取一个确定人类玩家角色
        human_role = random.choice(list(roles))
        state['human_role'] = human_role
        state['chat_history'] = []
        roles_str = ','.join(roles)
        print(f"主持人：欢迎大家参加今天的AI狼人杀游戏，今天参加游戏的角色有： {roles_str}")
    # 初始化待发言池
    state['waiting'] = roles.copy()
    # 选取下一个发言的角色，并从待发言池移除
    next = random.choice(list(state['waiting']))
    state['next_speaker'] = next
    state['waiting'].discard(next)
    # 修改游戏状态
    state['stage'] = 'speak'
    # 初始化聊天记录及投票
    # state['chat_history'] = []
    state['vote_store'] = []
    print(f"主持人：接下来我们开始游戏的第{round}轮发言，请{next}首先发言。")
    
    print("---------------------------")
    round+=1
    state['round'] = round
    return state

def ask_for_speak(state: GameState):
    # 如果待发言池为空，则进入投票阶段
    if len(state['waiting']) == 0:
        state['waiting'] = state['roles'].copy()
        state['stage'] = 'vote'
        print(f"主持人：游戏结束，请进行投票。请大家耐心等待投票结果！")
        return ask_for_vote(state)
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
        next = random.choice(list(state['waiting']))
        state['next_speaker'] = next
        state['waiting'].discard(next)
    return state
def ask_for_vote(state: GameState):
    if len(state['waiting']) == 0:
        human_role = state['human_role']
        round = state['round']
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
            print("投票详情如下："+json.dumps(vote_store))
        elif round == 3:
            state['stage'] = 'end'
            print("Human存活超过3轮，Human win!")
        else:
            print("Human存活,游戏继续！")
            state = gen_and_dispatch_role(state)
        return state
    next = random.choice(list(state['waiting']))
    state['next_speaker'] = next
    state['waiting'].discard(next)
    return state

def host(state: GameState):
    stage = state['stage']
    if stage == 'start':
        return gen_and_dispatch_role(state)
    elif stage == 'speak':
        return ask_for_speak(state)
    elif stage == 'vote':
        return ask_for_vote(state)
    