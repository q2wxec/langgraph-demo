from state import GameState
import chainlit as cl

async def speak(state: GameState):
    role = state['next_speaker']
    #print("你当前的角色是："+role)
    res = await cl.AskUserMessage(content="你当前的角色是："+role+"\n请输入你的对话内容: \n").send()
    #user_input = input("请输入你的对话内容: ")
    return {'chat_history':[(role, res['output'])]}

async def vote(state: GameState):
    role = state['next_speaker']
    roles_str = ','.join(state['roles'])
    # print("你当前的角色是："+role)
    # print("可供投票的选项有："+roles_str)
    # user_vote = input("请输入你的投票选择: ")
    # user_reason = input("请输入你的投票原因: ")
    vote_role = await cl.AskUserMessage(
        content=f"""你当前的角色是：{role}\n
        可供投票的选项有：{roles_str}\n
        请输入你的投票选择: \n
        """).send()
    vote_reason = await cl.AskUserMessage(
        content=f"""请输入你的投票原因:""").send()
    vote_store = state['vote_store']
    vote_store.append((role, {"vote":vote_role['output'],"reason":vote_reason['output']}))
    return {'vote_store': vote_store}



# def human_play(state: GameState):
#     stage = state['stage']
#     if stage == 'speak':
#         return speak(state)
#     elif stage == 'vote':
#         return vote(state)
    