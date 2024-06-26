import chainlit as cl
import agent


@cl.on_chat_start
def start():
    cl.user_session.set("agent", agent)


@cl.on_message
async def main(message: cl.Message):
    agent = cl.user_session.get("agent")  # type
    content = message.content
    req["messages"][0]["content"][0]["text"] = content
    res = await agent.glm4_call(req)

    # await cl.Message(content=res).send()
    
    
req={
    "model": "glm-4-alltools",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "给我查询上海本周日的天气情况，根据天气情况和上海的著名地标，画一张高质量的城市风景海报。"
                }
            ]
        }
    ],
    "stream": True,
    "tools": [
        {
            "type": "web_browser"
        },
        {
            "type": "code_interpreter",
            "code_interpreter":{
                "sandbox":"auto"
            }
        },
        {
            "type": "drawing_tool"
        },
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "查询城市指定日期的天气信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "description": "城市",
                            "type": "string"
                        },
                        "date": {
                            "description": "日期",
                            "type": "string"
                        }
                    },
                    "required": [
                        "city",
                        "date"
                    ]
                }
            }
        }
    ]
}