from state import GameState


def speak(state: GameState):
    role = state['next_speaker']
    print("你当前的角色是："+role)
    user_input = input("请输入你的对话内容: ")
    state['chat_history'].append((role, user_input))
    return state

def vote(state: GameState):
    role = state['next_speaker']
    roles_str = ','.join(state['roles'])
    print("你当前的角色是："+role)
    print("可供投票的选项有："+roles_str)
    user_vote = input("请输入你的投票选择: ")
    user_reason = input("请输入你的投票原因: ")
    state['vote_store'].append((role, {"vote":user_vote,"reason":user_reason}))
    return state



def human_play(state: GameState):
    stage = state['stage']
    if stage == 'speak':
        return speak(state)
    elif stage == 'vote':
        return vote(state)
    