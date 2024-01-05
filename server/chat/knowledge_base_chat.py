from fastapi import Body, Request
from fastapi.responses import StreamingResponse
from configs import (LLM_MODEL, VECTOR_SEARCH_TOP_K, SCORE_THRESHOLD, TEMPERATURE)
from server.utils import wrap_done, get_ChatOpenAI
from server.utils import BaseResponse, get_prompt_template
from langchain.chains import LLMChain
from langchain.callbacks import AsyncIteratorCallbackHandler
from typing import AsyncIterable, List, Optional
import asyncio
from langchain.prompts.chat import ChatPromptTemplate
from server.chat.utils import History
from server.knowledge_base.kb_service.base import KBService, KBServiceFactory
import json
import os
from urllib.parse import urlencode
from server.knowledge_base.kb_doc_api import search_docs
from langchain.prompts import PromptTemplate

async def knowledge_base_chat(query: str = Body(..., description="用户输入", examples=["你好"]),
                            knowledge_base_name: str = Body(..., description="知识库名称", examples=["samples"]),
                            top_k: int = Body(VECTOR_SEARCH_TOP_K, description="匹配向量数"),
                            score_threshold: float = Body(SCORE_THRESHOLD, description="知识库匹配相关度阈值，取值范围在0-1之间，SCORE越小，相关度越高，取到1相当于不筛选，建议设置在0.5左右", ge=0, le=2),
                            history: List[History] = Body([],
                                                      description="历史对话",
                                                      examples=[[
                                                          {"role": "user",
                                                           "content": "我们来玩成语接龙，我先来，生龙活虎"},
                                                          {"role": "assistant",
                                                           "content": "虎头虎脑"}]]
                                                      ),
                            stream: bool = Body(False, description="流式输出"),
                            model_name: str = Body(LLM_MODEL, description="LLM 模型名称。"),
                            temperature: float = Body(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=1.0),
                            max_tokens: int = Body(None, description="限制LLM生成Token数量，默认None代表模型最大值"),
                            prompt_name: str = Body("default", description="使用的prompt模板名称(在configs/prompt_config.py中配置)"),
                        ):
    kb = KBServiceFactory.get_service_by_name(knowledge_base_name)
    if kb is None:
        return BaseResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}")

    history = [History.from_data(h) for h in history]
    print(f"******server/chat/knowledge_base_chat function, history:{history}")
    async def knowledge_base_chat_iterator(query: str,
                                           top_k: int,
                                           history: Optional[List[History]],
                                           model_name: str = LLM_MODEL,
                                           prompt_name: str = prompt_name,
                                           ) -> AsyncIterable[str]:
        print(f"knowledge_base_chat_iterator,query:{query},model_name:{model_name},prompt_name:{prompt_name}")
        
        model1 = get_ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            callbacks=[],
        )

#        augment_prompt_template = get_prompt_template("data_augment", "default")
#        input_msg1 = History(role="user", content=augment_prompt_template).to_msg_template(False)
#        chat_prompt1 = ChatPromptTemplate.from_messages(
#             [i.to_msg_template() for i in history] + [input_msg1])
#        chain1 = LLMChain(prompt=chat_prompt1, llm=model1)
#        print(f"knowledge_base_chat_iterator,prompt_template:{chat_prompt1}")
#        result = chain1._call({ "question": query})
#        print(f"chain1._call, result:{result}")

        callback = AsyncIteratorCallbackHandler()
        model = get_ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            callbacks=[callback],
        )
        
        #augment_prompt_template = get_prompt_template("data_augment", "default")
        #input_msg = History(role="user", content=augment_prompt_template).to_msg_template(False)
        #chat_prompt = ChatPromptTemplate.from_messages(
        #     [i.to_msg_template() for i in history] + [input_msg])
        #chain = LLMChain(prompt=chat_prompt, llm=model)
        #print(f"knowledge_base_chat_iterator,prompt_template:{chat_prompt}")
        ##chain = LLMChain(prompt=PromptTemplate.from_template(augment_prompt_template), llm=model)
        ##print(f"knowledge_base_chat_iterator,prompt_template:{augment_prompt_template}")
        #task = asyncio.create_task(wrap_done(
        #    chain.acall({ "question": query}),
        #    callback.done),
        #)
        #prompt_template = "请找出和{question}最相似的一句话"
        #llm_chain = LLMChain(prompt=PromptTemplate.from_template(prompt_template), llm=model)
        #result = llm_chain(query)
        #print(f"请找出和question 最相似的一句话：{result}")

        docs = search_docs(query, knowledge_base_name, top_k, score_threshold)
        context = "\n".join([doc.page_content for doc in docs])

        #print(f"knowledge_base_chat_iterator,search docs context:{context}")

        prompt_template = get_prompt_template("knowledge_base_chat", prompt_name)
        input_msg = History(role="user", content=prompt_template).to_msg_template(False)
        print(f"knowledge_base_chat_iterator,input_msg:{input_msg}")
        chat_prompt = ChatPromptTemplate.from_messages(
            [i.to_msg_template() for i in history] + [input_msg])

        #print(f"knowledge_base_chat_iterator,chat_prompt:{chat_prompt}")
        chain = LLMChain(prompt=chat_prompt, llm=model)

        # Begin a task that runs in the background.
        task = asyncio.create_task(wrap_done(
            chain.acall({"context": context, "question": query}),
            callback.done),
        )
        
        print(f"task call end")
        source_documents = []
        for inum, doc in enumerate(docs):
            filename = os.path.split(doc.metadata["source"])[-1]
            parameters = urlencode({"knowledge_base_name": knowledge_base_name, "file_name":filename})
            url = f"/knowledge_base/download_doc?" + parameters
            text = f"""出处 [{inum + 1}] [{filename}]({url}) \n\n{doc.page_content}\n\n"""
            source_documents.append(text)

        print(f"knowledge_base_chat_iterator, stream:{stream}")
        if stream:
            async for token in callback.aiter():
                # Use server-sent-events to stream the response
                yield json.dumps({"answer": token}, ensure_ascii=False)
            yield json.dumps({"docs": source_documents}, ensure_ascii=False)
        else:
            answer = ""
            async for token in callback.aiter():
                answer += token
            yield json.dumps({"answer": answer,
                              "docs": source_documents},
                             ensure_ascii=False)

        await task

    return StreamingResponse(knowledge_base_chat_iterator(query=query,
                                                          top_k=top_k,
                                                          history=history,
                                                          model_name=model_name,
                                                          prompt_name=prompt_name),
                             media_type="text/event-stream")
