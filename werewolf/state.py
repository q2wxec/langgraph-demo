from typing import Dict,List,Tuple, Set, Annotated, TypedDict
import operator


class GameState(TypedDict):
    roles: Set #角色列表
    human_role: str #人类玩家角色
    chat_history: Annotated[List[Tuple], operator.add] #聊天记录
    waiting:Set #待发言玩家
    stage:str = 'start' #游戏阶段，start,speak,vote,end
    vote_store:Annotated[List[Tuple], operator.add] #投票记录
    next_speaker:str = "" #下一位发言者
    
    