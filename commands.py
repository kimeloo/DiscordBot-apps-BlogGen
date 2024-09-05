import logging
import discord.errors as d_errors
from .gpt import Chat
from .events import Events as myevents
logger = logging.getLogger(__name__)

class Commands():
    def __init__(self, bot):
        self.bot = bot
        self.CATEGORY_ID = 0
        self.CATEGORY_NAME = ""
        self.category_id_list = [[0]]
    
    def add(self):
        return self.__commands(self.bot)
    
    def __commands(self, bot):
        @bot.command()
        async def gpt(ctx):
            send_message = 'Listening to category : [{}]\nUsage : !chat <Your Topic>'.format(ctx.channel.category)
            logger.info("[{:>8}] : [{}] FROM {}".format("Recieved", ctx.message.content, ctx.channel.name))
            self.CATEGORY_ID = int(ctx.channel.category_id)
            self.CATEGORY_NAME = str(ctx.channel.category)
            logger.debug("Saved Category name : [{}] / ID : [{}]".format(ctx.channel.category, ctx.channel.category_id))
            await ctx.channel.send(send_message)
            logger.info("[{:>8}] : [{}] TO {}".format("Sent", send_message, ctx.channel.name))
            self.category_id_list[0][0] = self.CATEGORY_ID
        
        bot = myevents(bot).add_from_commands(self.category_id_list)
        

        @bot.command()
        async def chat(ctx, *, msg):
            if int(ctx.channel.category_id) != self.CATEGORY_ID:
                logger.debug("[new_chat] from different channel")
                await ctx.channel.send("Try in {} category or type !gpt".format(self.CATEGORY_NAME))
                return
            new_msg = await ctx.channel.send(msg)
            await ctx.message.delete()
            try:
                new_thread = await new_msg.create_thread(name=msg, auto_archive_duration=10080)
            except d_errors.HTTPException:
                if 'Main idea' in msg:
                    try:
                        name = msg.split('Main idea')[1].split('}')[0].split("'")[2]
                    except:
                        name = msg[:99]
                else:
                    name = msg[:99]
                new_thread = await new_msg.create_thread(name=name, auto_archive_duration=10080)


            logger.info(f'Created [{msg}] thread.')
            mygpt = Chat(int(new_thread.id))
            gpt_thread_id = await mygpt.new(msg)
            await new_thread.send(f'{gpt_thread_id}')

            stream = await mygpt.stream_msg(gpt_thread_id, msg)

            await mygpt.to_user(new_thread, stream)


        
        @bot.command()
        async def profile(ctx):
            pass
        
        

        return bot