from typing import Dict,List,Tuple, Set, Annotated, TypedDict
import operator


class GameState(TypedDict):
    roles: List[str] #角色列表
    human_role: str #人类玩家角色
    
    chat_history: Annotated[List[Tuple], operator.add] #聊天记录
    waiting:List[str] #待发言玩家
    # stage:str = 'start' #游戏阶段，start,speak,vote,sum,end
    vote_store:List[Tuple] #投票记录
    
    next_speaker:str = "" #下一位发言者
    round:int = 0 #游戏回合数
    
    end:bool = False
    
    