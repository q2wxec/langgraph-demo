from state import GameState
from langgraph.graph import  END
import random
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from load_prompt import load_prompt
from langchain_core.output_parsers import StrOutputParser
import json

def gen_and_dispatch_role(state: GameState):
    roles = state['roles']
    round = state['round'] + 1
    human_role = state['human_role']
    first_init = not roles
    # 初始化角色
    if first_init:
        roles = ["亚里士多德","莫扎特","达芬奇","成吉思汗","克利奥帕特拉七世"]  
        # 从roles中随机选取一个确定人类玩家角色
        human_role = random.choice(roles)
        roles_str = ','.join(roles)
        print(f"主持人：欢迎大家参加今天的AI狼人杀游戏，今天参加游戏的角色有： {roles_str}")
    # 初始化待发言池
    waiting = roles.copy()
    # 选取下一个发言的角色，并从待发言池移除
    # next = random.choice(waiting)
    # state['waiting'].remove(next)
    # 修改游戏状态
    # state['stage'] = 'speak'
    # 初始化聊天记录及投票
    # print(f"主持人：接下来我们开始游戏的第{round}轮发言，请{next}首先发言。")
    print(f"主持人：接下来我们开始游戏的第{round}轮发言")
    print("---------------------------")
    return {'roles':roles,'human_role':human_role,'waiting':waiting,'vote_store':[],'round':round}

def ask_for_speak(state: GameState):
    # 如果待发言池为空，则进入投票阶段
    # if len(state['waiting']) == 0:
    #     state['waiting'] = state['roles'].copy()
    #     state['stage'] = 'vote'
    #     print(f"主持人：游戏结束，请进行投票。请大家耐心等待投票结果！")
    #     return ask_for_vote(state)
    waiting = state['waiting']
    if len(waiting) == 0:
        waiting = state['roles'].copy()
        return {'waiting':waiting,'next_speaker':''}
    next = random.choice(waiting)
    chat_history = state['chat_history']
    if chat_history:
        last_chat = chat_history[-1]
        last_chat_str = last_chat[0]+': '+last_chat[1]
        waiting_roles_str = ','.join(waiting)
        llm = ChatOpenAI(model="glm-4",  temperature=0.01)
        choose_prompt = ChatPromptTemplate.from_template(load_prompt("prompt/choose_speaker.prompt"))
        chain = choose_prompt|llm|StrOutputParser()
        role_chosen = chain.invoke({"history": last_chat_str, "waitings": waiting_roles_str})
        if role_chosen in waiting:
            next = role_chosen
    next_speaker = next
    waiting.remove(next_speaker)
    return {'waiting':waiting,'next_speaker':next_speaker}

def ask_for_vote(state: GameState):
    # if len(state['waiting']) == 0:
    #     human_role = state['human_role']
    #     round = state['round']
    #     # 统计票数决定是否结束游戏
    #     vote_store = state['vote_store']
    #     human_vote_count = 0
    #     for vote in vote_store:
    #         vote_role = vote[1]['vote']
    #         if vote_role == human_role:
    #             human_vote_count += 1
    #     totle_votes = len(state['roles'])
    #     # 如果人类角色票数超过一半，结束游戏
    #     if human_vote_count > totle_votes / 2:
    #         state['stage'] = 'end'
    #         print("AI win!")
    #         print("投票详情如下："+json.dumps(vote_store, ensure_ascii=False))
    #     elif round == 3:
    #         state['stage'] = 'end'
    #         print("Human存活超过3轮，Human win!")
    #     else:
    #         print("Human存活,游戏继续！")
    #         print("上轮投票详情如下："+json.dumps(vote_store, ensure_ascii=False))
    #         state = gen_and_dispatch_role(state)
    #     return state
    waiting = state['waiting']
    if len(waiting) == 0:
        return {'next_speaker':''}
    next = random.choice(state['waiting'])
    next_speaker = next
    waiting.remove(next)
    return {'waiting':waiting,'next_speaker':next_speaker}

def count_vote(state: GameState):
    # 统计票数决定是否结束游戏
    vote_store = state['vote_store']
    human_role = state['human_role']
    human_vote_count = 0
    for vote in vote_store:
        vote_role = vote[1]['vote']
        if vote_role == human_role:
            human_vote_count +=1
        totle_votes = len(state['roles'])
        # 如果人类角色票数超过一半，结束游戏
        if human_vote_count > totle_votes / 2:
            print("AI win!")
            print("投票详情如下："+json.dumps(vote_store, ensure_ascii=False))
            return {'end':True}
        elif round == 3:
            print("Human存活超过3轮，Human win!")
            return {'end':True}
        else:
            print("Human存活,游戏继续！")
            print("上轮投票详情如下："+json.dumps(vote_store, ensure_ascii=False))
            return {'end':False}

# def host(state: GameState):
#     stage = state['stage']
#     if stage == 'start':
#         return gen_and_dispatch_role(state)
#     elif stage == 'speak':
#         return ask_for_speak(state)
#     elif stage == 'vote':
#         return ask_for_vote(state)
    