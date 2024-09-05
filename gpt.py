import os
import logging
from openai import OpenAI, AsyncOpenAI
logger = logging.getLogger(__name__)

class Chat():
    def __init__(self, thread_id):
        self.OPENAI_KEY = os.getenv('OPENAI_API_KEY')
        self.discord_thr_id = thread_id
        self.assistant_id = os.getenv('OPENAI_ASSISTANT_ID')
        self.client_norm = OpenAI()
        self.client = AsyncOpenAI()
    
    async def new(self, msg):
        thread = await self.client.beta.threads.create()
        return thread.id
    
    async def stream_msg(self, thread_id, msg):
        message = await self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=msg,
        )
        stream = await self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant_id,
            max_completion_tokens=16383,
            max_prompt_tokens=16383,
            stream=True
        )
        return stream

    async def to_user(self, discord_thd, stream):
        response_msg = ""
        async for event in stream:
            if event.event == "thread.message.delta" and event.data.delta.content:
                gpt_response = event.data.delta.content[0].text.value
                response_msg += str(gpt_response)
                if response_msg == str(gpt_response):
                    response = await discord_thd.send(response_msg)
                else:
                    response = await response.edit(content=response_msg)
                    if len(response_msg) > 1900:
                        response_msg = ""
        response = await response.edit(content=response_msg+"\n\n(end)")
