import interactions
import asyncio
from interactions import Client, Intents
from interactions.ext import molter
from interactions.ext.molter.utils import Typing

bot = Client(token="".join(["ODU3MDYwNzM0OTM2Mjg1MjQ0.GLW7JO.", "4tRMk5ITlFHiWgabLBKdK8q9qbNvSYk9qi3i3E"]),
intents=Intents.DEFAULT | Intents.GUILD_MESSAGE_CONTENT,
presence=interactions.ClientPresence(
     status=interactions.StatusType.DND,
     activities=[
          interactions.PresenceActivity(name="",type=interactions.PresenceActivityType.GAME)
     ]
 ))

molter.setup(bot, default_prefix='>')

#change presence on runtime
@molter.prefixed_command()
async def change(ctx:molter.MolterContext, types ,content=""):
     if not await ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
              return
     else:
          if types == "0":
               await bot.change_presence(interactions.ClientPresence(
                    status=interactions.StatusType.INVISIBLE,
                    activities=[]
               ))
          else:
               await bot.change_presence(interactions.ClientPresence(
                    status=interactions.StatusType.DND,
                    activities=[
                         interactions.PresenceActivity(name=content,type=interactions.PresenceActivityType.GAME)
                 ]))

@bot.event
async def on_message_create(msg: interactions.Message):
     if(msg.author.bot):
          return
     elif(not msg.content.startswith(">")) and msg.channel_id == 1084962082593718392:
        channel = await interactions.get(bot, interactions.Channel, object_id=int(1084940810002374746))
        async with Typing(bot._http, int(1084940810002374746)):      
                await asyncio.sleep(len(msg.content)*0.015)
                await channel.send(msg.content)

bot.start()
