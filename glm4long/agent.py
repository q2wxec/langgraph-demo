from zhipuai import ZhipuAI
import os
import chainlit as cl
import time
client = ZhipuAI(api_key=os.getenv('OPENAI_API_KEY')) # 请填写您自己的APIKey


async def glm4_async_call(req):
    response = client.chat.asyncCompletions.create(**req)
    task_id = response.id
    task_status = ''
    get_cnt = 0
    
    while task_status != 'SUCCESS' and task_status != 'FAILED' and get_cnt <= 100:
        result_response = client.chat.asyncCompletions.retrieve_completion_result(id=task_id)
        print(result_response)
        task_status = result_response.task_status
        
        time.sleep(2)
        get_cnt += 1
    
    if task_status == 'SUCCESS':
        result_response = client.chat.asyncCompletions.retrieve_completion_result(id=task_id)
        msg = cl.Message(content=result_response.choices[0].message.content)
        await msg.send()


async def glm4_call(req):
    # 假设我们有一个生成器或者迭代器，它按顺序产生response的chunks
    response_chunks = client.chat.completions.create(**req)

    # 初始化一个变量来存储当前的类型
    msg = None
    for chunk in response_chunks:
        delta = chunk.choices[0].delta
        # 获取chunk中的类型和内容
        chunk_content = delta.content
        msg = cl.Message(content="")
        await msg.send()
        if chunk_content is not None:
            await msg.stream_token(chunk_content)