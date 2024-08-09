import chainlit as cl
import agent


@cl.on_chat_start
def start():
    cl.user_session.set("agent", agent)


@cl.on_message
async def main(msg: cl.Message):
    agent = cl.user_session.get("agent")  # type
    content = msg.content
    docs = []
    if msg.elements:
        # 筛选.txt类型的文本文件
        texts = [file for file in msg.elements if "text" in file.mime]
        # 读取所有texts文件
        for text in texts:
            # 读取text文件并添加到docs中
            with open(text.path, "r", encoding='utf-8') as f:
                docs.append(f.read())
    prompt = f"""你是擅长文档阅读的好帮手，请你基于我提供的文档进行分析总结，获取关键内容，回答我的问题。
                现在，我会将需要阅读的文档以文字的形式提供给你，具体内容如下:
                {docs}
                =========
                我的问题是：
                {content}
                """
    req["messages"][0]["content"][0]["text"] = prompt    
    res = await agent.glm4_async_call(req)

    # await cl.Message(content=res).send()
    
    
req={
    "model": "glm-4-long",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": ""
                }
            ]
        }
    ],
    "tools": [
        {
            "type": "web_browser"
        }
    ]
}