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
