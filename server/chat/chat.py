from fastapi import Body
from fastapi.responses import StreamingResponse
from configs import LLM_MODEL, TEMPERATURE
from server.utils import wrap_done, get_ChatOpenAI
from langchain.chains import LLMChain
from langchain.callbacks import AsyncIteratorCallbackHandler
from typing import AsyncIterable
import asyncio
from langchain.prompts.chat import ChatPromptTemplate
from typing import List
from server.chat.utils import History
from server.utils import get_prompt_template
from langchain.prompts import PromptTemplate

async def chat(query: str = Body(..., description="用户输入", examples=["恼羞成怒"]),
                history: List[History] = Body([],
                                       description="历史对话",
                                       examples=[[
                                           {"role": "user", "content": "我们来玩成语接龙，我先来，生龙活虎"},
                                           {"role": "assistant", "content": "虎头虎脑"}]]
                                       ),
                stream: bool = Body(False, description="流式输出"),
                model_name: str = Body(LLM_MODEL, description="LLM 模型名称。"),
                temperature: float = Body(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=1.0),
                max_tokens: int = Body(None, description="限制LLM生成Token数量，默认None代表模型最大值"),
                # top_p: float = Body(TOP_P, description="LLM 核采样。勿与temperature同时设置", gt=0.0, lt=1.0),
                prompt_name: str = Body("default", description="使用的prompt模板名称(在configs/prompt_config.py中配置)"),
         ):
    history = [History.from_data(h) for h in history]

    async def chat_iterator(query: str,
                            history: List[History] = [],
                            model_name: str = LLM_MODEL,
                            prompt_name: str = prompt_name,
                            ) -> AsyncIterable[str]:
        callback = AsyncIteratorCallbackHandler()
        model = get_ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            callbacks=[callback],
        )

        # augment_prompt_template = get_prompt_template("data_augment", "default")
        # input_msg = History(role="user", content=augment_prompt_template).to_msg_template(False)
        # chat_prompt = ChatPromptTemplate.from_messages(
        #      [i.to_msg_template() for i in history] + [input_msg])
        # chain = LLMChain(prompt=chat_prompt, llm=model)
        # print(f"knowledge_base_chat_iterator,prompt_template:{chat_prompt}")

        # # Begin a task that runs in the background.
        # task = asyncio.create_task(wrap_done(
        #     chain.acall({ "question": query}),
        #     callback.done),
        # )

       
        prompt = ChatPromptTemplate.from_template(" 你是一个非常聪明的语义转换专家总能找到同一个语义不同的表达方式，请简洁生成一个与三单引号里的原句子语气语调完全一致，并且语义最相似的新句子，注意不是回答三单引号里的原句子，同时新句子直接使用简体中文给出，而不用重三单引号里的原句子。如果无法给出满足条件的新句子，直接给出三单引号里的原句子，而不是给出三单引号里的原句子的答案 '''{{input}}''' ")

        # prompt_template = get_prompt_template("llm_chat", prompt_name)
        # input_msg = History(role="user", content=prompt_template).to_msg_template(False)
        # chat_prompt = ChatPromptTemplate.from_messages(
        #     [i.to_msg_template() for i in history] + [input_msg])
        chain = LLMChain(prompt=prompt, llm=model)

        name = "John"
        age = 30
        text = "你是一个非常聪明的语义转换专家总能找到同一个语义不同的表达方式，请简洁生成一个与三单引号里的原句子语气语调完全一致，并且语义最相似的新句子，注意不是回答三单引号里的原句子，同时新句子直接使用简体中文给出，而不用重三单引号里的原句子。如果无法给出满足条件的新句子，直接给出三单引号里的原句子，而不是给出三单引号里的原句子的答案\n ''' "
        text = text + query
        text = text + " ''' "
        result = ", ".join(["Name: ", name, ", Age: ", str(age)])

        # Begin a task that runs in the background.
        task = asyncio.create_task(wrap_done(
            chain.acall({"input": query}),
            callback.done),
        )

        if stream:
            async for token in callback.aiter():
                # Use server-sent-events to stream the response
                yield token
        else:
            answer = ""
            async for token in callback.aiter():
                answer += token
            yield answer

        await task

    return StreamingResponse(chat_iterator(query=query,
                                           history=history,
                                           model_name=model_name,
                                           prompt_name=prompt_name),
                             media_type="text/event-stream")
