from zhipuai import ZhipuAI
import os
client = ZhipuAI(api_key=os.getenv('OPENAI_API_KEY')) # 请填写您自己的APIKey

with open('C:/Users/fxx/Downloads/glm4-long/integrated_code.txt', "r", encoding='utf-8') as f:
     text =f.read()

history = [
    {"role": "system", 
     "content": f"""你是资深AI开发架构师，对Langchain项目源码有着深度的理解，并具备深度的逻辑推理能力，请你基于我提供的langchain-core包的源码进行分析总结，获取关键内容，回答我的问题。
                现在，我会将需要阅读的源码以文字的形式提供给你，具体内容如下:
                {text}
                """},
]
 
def chat(question, history):
    history.append({
        "role": "user", 
        "content": question
    })
    completion = client.chat.completions.create(
        model = "glm-4-long",
        messages = history,
        top_p = 0.7,
        temperature = 0.2,
        tools = [{"type": "web_search", 
                  "web_search": {"search_result": False}}]
    )
    result = completion.choices[0].message.content
    history.append({
        "role": "assistant",
        "content": result
    })
    return result

print(chat("请通过Multi Query构建一个RAG案例，要求合并输出文档里的连续片段", history))