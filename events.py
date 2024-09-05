import os
import logging
from .gpt import Chat
logger = logging.getLogger(__name__)

class Events():
    def __init__(self, bot):
        self.bot = bot
    
    def add(self):
        return self.__events(self.bot)
    
    def __events(self, bot):
        return bot

    def add_from_commands(self, CATEGORY_ID):
        return self.__events_from_commands(self.bot, CATEGORY_ID)

    def __events_from_commands(self, bot, CATEGORY_ID):
        @bot.event
        async def on_message(message):
            await bot.process_commands(message)     # commands 처리 후 on_message 처리
            if message.author == bot.user:      # bot의 메시지는 무시
                return
            try:
                if message.channel.parent.category_id!=CATEGORY_ID[0][0]:
                    return
            except AttributeError:
                return
            thread = message.channel
            msg = str(message.content)
            gpt_thread_id = [x async for x in thread.history(limit=2, oldest_first=True)][1].content
            logger.info(gpt_thread_id)
            mygpt = Chat(int(thread.id))
            stream = await mygpt.stream_msg(gpt_thread_id, msg)
            await mygpt.to_user(thread, stream)
        
        return bot