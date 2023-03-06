import interactions
from interactions import Client, Intents
from interactions.ext import molter
from interactions.ext.molter.utils import Typing

import json
import sqlite3 as sl
import asyncio
import os


cur = sl.connect('notes.db')
c = cur.cursor()

try:
    c.execute("""CREATE TABLE notes (
        name text,
        author text,
        data text
    )""")
except sl.OperationalError:
    pass

f = open("./settings.json")
data = json.load(f)
f.close

bot = Client(token=data['token'],
 intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT)

molter.setup(bot, default_prefix='>')

@bot.event
async def on_ready():
	print('ready!')

#send command to given channel
@molter.prefixed_command()
async def send(ctx: molter.MolterContext, id, content):
        if not await ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
              return
        else:
            channel = await interactions.get(bot, interactions.Channel, object_id=int(id))
            await channel.send(content=content);


#command to make tags
@molter.prefixed_command()
async def tag(ctx:molter.MolterContext, name):
      await ctx.send("unfinished ty")

#write generated script files
@molter.prefixed_command()
async def script(ctx:molter.MolterContext, name, content):
    if not await ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
        return

    try:
        f = open("scripts/"+str(name)+".txt", "x")
        f.close();
    except FileExistsError:
        pass;
    
    
    f = open("scripts/"+str(name)+".txt", "a")

    f.write(content+"\n");

    f.close
    await ctx.send("added "+content);

#read generated script files
@molter.prefixed_command()
async def read(ctx:molter.MolterContext, name, id):
    if not await ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
        return
    try:
          f=open("scripts/"+name+".txt", "r")
    except FileNotFoundError:
          await ctx.send("Hey! This file was no found. Beware! This is **CaSe SeNsItIvE**")
          return;
    data = f.read()
    f.close()
    splitData = data.splitlines();
    print(splitData)
    print(data)

    
    channel = await interactions.get(bot, interactions.Channel, object_id=int(id))

    #Janky ass work arround, using http requests instead of the channel.typing because it 
    #kept giving me an error.
    for x in splitData: 
        async with Typing(ctx._http, int(id)):      
            await asyncio.sleep(len(x)*0.025)
            await channel.send(x);

#delete generated script files.
@molter.prefixed_command()
async def delete(ctx:molter.MolterCommand, name):
    if not await ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
        return

    base_dir = os.path.dirname(os.path.realpath(__file__))
    fpath = "{}/scripts/"+str(name)
    fpath = fpath.format(base_dir)

    try:
        os.remove(fpath+".txt");
    except FileNotFoundError:
        await ctx.send(name+".txt was not found!");
        return
    
    await ctx.send(name+".txt was removed!");
         

bot.start()