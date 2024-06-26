from zhipuai import ZhipuAI
import os
import chainlit as cl
client = ZhipuAI(api_key=os.getenv('OPENAI_API_KEY')) # 请填写您自己的APIKey


async def glm4_call(req):
    # 假设我们有一个生成器或者迭代器，它按顺序产生response的chunks
    response_chunks = client.chat.completions.create(**req)

    # 初始化一个变量来存储当前的类型
    current_type = None
    tool_calls = None
    msg = None
    code = ''
    for chunk in response_chunks:
        delta = chunk.choices[0].delta
        # 获取chunk中的类型和内容
        chunk_type = delta.role
        chunk_content = delta.content
        chunk_tool_calls = delta.tool_calls
        is_tool_calls = chunk_tool_calls is not None and len(chunk_tool_calls) > 0
        # 检查类型是否发生变化
        if chunk_type != current_type or is_tool_calls != tool_calls:
            #print()
            # 如果类型变化，先输出类型名称，并重置current_type变量
            #print(f"--- {chunk_type} ---")
            if chunk_type == "assistant" and not is_tool_calls:
                if msg:
                    await msg.update()
                msg = cl.Message(content="")
                await msg.send()
                # print()
            elif chunk_type == "assistant" and is_tool_calls:
                tool_type = chunk_tool_calls[0].type
                if msg:
                    await msg.update()
                msg = cl.Message(content="")
                await msg.send()
                await msg.stream_token(f"\n执行工具调用:{tool_type},请求入参: ")
                if tool_type == 'code_interpreter':
                    code = ''
                    await msg.stream_token(f"\n```python\n")
                # print(f"--- 执行工具调用:{tool_type} ---")
            # elif chunk_type == "tool" and is_tool_calls:
            #     # print(f"--- 完成工具调用 ---")
            #     tool_type = chunk_tool_calls[0].type
            #     async with cl.Step(name=tool_type,type='tool') as step:
            #         # Step is sent as soon as the context manager is entered
            #         step.input = step_input
            #         step.output = str(chunk_tool_calls[0].model_extra[tool_type]['outputs'])
            #         await step.update()
            current_type = chunk_type
            tool_calls = is_tool_calls
            
        if chunk_type == "assistant" and is_tool_calls:
            tool_type = chunk_tool_calls[0].type
            
            await msg.stream_token(chunk_tool_calls[0].model_extra[tool_type]['input'])
            if tool_type == 'code_interpreter' :
                code+=chunk_tool_calls[0].model_extra[tool_type]['input']
            if tool_type == 'code_interpreter' and chunk.choices[0].finish_reason == 'tool_calls':
                    await msg.stream_token(f"\n```\n")
                    # Sending an action button within a chatbot message
                    # actions = [
                    #     cl.Action(name="action_button", value="example_value", description="Click me!")
                    # ]

                    # await cl.Message(content="Interact with this action button:", actions=actions).send()
        
        if chunk_type == "tool" and is_tool_calls:
            tool_type = chunk_tool_calls[0].type
            # await msg.stream_token(f"\n--- 请求出参:---\n")
            await deal_tool_output(msg, chunk_tool_calls, tool_type)
        # 输出具体的内容
        if chunk_content is not None:
            await msg.stream_token(chunk_content)
            # print(chunk_content, end='', flush=True)
    if msg:
        await msg.update()

async def deal_tool_output(msg, chunk_tool_calls, tool_type):
    outputs = chunk_tool_calls[0].model_extra[tool_type]['outputs']
    if tool_type == 'web_browser':
        await msg.stream_token(f"\n执行检索,请求结果,查询到相关信息{len(outputs)}条")
    elif tool_type == 'drawing_tool':
        # await msg.stream_token(f"\n完成绘图！")
        # await msg.stream_token(f"\n![image]({outputs[0]['image']})")
        image = cl.Image(url=outputs[0]['image'], name="image", display="inline")
        # Attach the image to the message
        await cl.Message(
            content="完成绘图",
            elements=[image],
        ).send()