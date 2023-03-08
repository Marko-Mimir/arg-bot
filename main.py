import interactions
from interactions import Client, Intents
from interactions.ext import molter
from interactions.ext.molter.utils import Typing
import interactions.ext.wait_for as wf

import json
import sqlite3 as sl
import asyncio
import os
import interpreter.inter as ter

loop = asyncio.get_event_loop()

cur = sl.connect('notes.db')
c = cur.cursor()

try:
    c.execute("""CREATE TABLE notes (
        name text,
        author text,
        data text,
        authorid text
    )""")
except sl.OperationalError:
    pass

f = open("./json/settings.json")
data = json.load(f)
f.close

bot = Client(token=data['token'],
 intents=Intents.DEFAULT | Intents.GUILD_MESSAGE_CONTENT,
 presence=interactions.ClientPresence(
     status=interactions.StatusType.DND,
     activities=[
          interactions.PresenceActivity(name="Running V0.4",type=interactions.PresenceActivityType.GAME)
     ]
 ))

molter.setup(bot, default_prefix='>')

@bot.event
async def on_ready():
     ter.init()
     print('ready!')

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


#send command to given channel
@molter.prefixed_command()
async def send(ctx: molter.MolterContext, id, content):
        if not await ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
              return
        else:

          rem = ["<","#",">"]
          for x in rem:
               id = id.replace(x,"")
          channel = await interactions.get(bot, interactions.Channel, object_id=int(id))
          async with Typing(ctx._http, int(id)):      
                await asyncio.sleep(len(content)*0.015)
                await channel.send(content=content);

#Reply to messages
@molter.prefixed_command()
async def reply(ctx: molter.MolterContext, messageId, channelId, content):
     rem = ["<","#",">"]
     for x in rem:
          channelId = channelId.replace(x,"")
     message = await interactions.get(bot, interactions.Message, object_id=messageId, parent_id=channelId)
     await message.reply(content);

#command to get tags
@molter.prefixed_command()
async def tag(ctx:molter.MolterContext, name=None):
      if name == "list":
           con = c.execute("SELECT name FROM notes WHERE authorid =?", (str(ctx.author.id),)).fetchall()
           print(con)
           string = "Every tag you own:\n"
           for x in con:
                string = string+str(x[0])+"\n"
           return await ctx.send(string);
      if name != None:
           res = c.execute("SELECT name FROM notes").fetchall();
           r = [''.join(i) for i in res]
           if name in r:
                content = c.execute("SELECT data, author FROM notes WHERE name = ?", (name,)).fetchone()
                con = [''.join(i) for i in content]
                emb = interactions.Embed(title=name)
                emb.footer = interactions.EmbedFooter(text="Tag created by "+con[1])
                emb.add_field('',con[0])
                emb.color = 0x992D22
                await ctx.send(embeds=[emb])
           else:
                await ctx.reply('This is not a valid tag name, or a valid sub-command.')
      else:
           await ctx.reply('This is not a valid tag name, or a valid sub-command.')

#tag setter
@tag.subcommand()
async def create(ctx: molter.MolterContext, name=None, content=None):

    async def check(msg):
         if int(msg.author.id) == int(ctx.author.id):
              return True
         else:
              return False
         
    if name != None and content != None:
        c.execute("INSERT INTO notes VALUES(?, ?, ?, ?)", (name, ctx.author.name, content, str(ctx.author.id)))
        cur.commit();
        await ctx.send("Tag **"+name+"** was created!")
    elif name != None and content == None:
         await ctx.reply("What should go into this tag?")
         try:
            msg: interactions.Message = await wf.wait_for(bot, "on_message_create", check=check, timeout=15)
         except asyncio.TimeoutError:
              return await ctx.send("Sorry, I cant wait any longer, please try again.")
         
         c.execute("INSERT INTO notes VALUES(?, ?, ?, ?)", (name, ctx.author.name, msg.content, str(ctx.author.id)));
         cur.commit();
         await ctx.send("Tag **"+name+"** was created!")
    else:
         await ctx.reply("What should I name this tag?")
         try:
            msg1: interactions.Message = await wf.wait_for(bot, "on_message_create", check=check, timeout=15)
         except asyncio.TimeoutError:
              return await ctx.send("Sorry, I cant wait any longer, please try again.")
         await ctx.send("What should go into this tag?")

         try:
            msg2: interactions.Message = await wf.wait_for(bot, "on_message_create", check=check, timeout=15)
         except asyncio.TimeoutError:
              return await ctx.send("Sorry, I cant wait any longer, please try again.")
         
         c.execute('INSERT INTO notes VALUES (?, ?, ?, ?)', (msg1.content, str(ctx.author.name), msg2.content, str(ctx.author.id)))
         cur.commit();
         await ctx.send("Tag **"+msg1.content+"** was created!")

#tag.admin.debug
@tag.subcommand()
async def debug(ctx:molter.MolterContext, name):
     if not await ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
              return
     else:
          con = c.execute("SELECT * FROM notes WHERE name =?", (name,)).fetchall()
          await ctx.send("Name: "+con[0][0]+"\nAuthor: "+con[0][1]+"\nContents: "+con[0][2]+"\nAuthor Id: "+con[0][3])

#tag delete
@tag.subcommand()
async def delete(ctx:molter.MolterContext, name=None):
     async def check(msg):
         if int(msg.author.id) == int(ctx.author.id):
              return True
         else:
              return False

     if name == None:
        await ctx.send("What is the name of the tag you're deleting?")
        try:
            msg: interactions.Message = await wf.wait_for(bot, "on_message_create", check=check, timeout=15)
            name = msg.content
        except asyncio.TimeoutError:
              return await ctx.send("Sorry, I cant wait any longer, please try again.")
    
     content = c.execute("SELECT authorid FROM notes WHERE name =?", (name,)).fetchall();
     if len(content) > 1:
          print("HUGGGE FUCKING ERROR LIKE MASSIVE FUCKING ERROR, LINE 132 of __MAIN__")
          return await ctx.send("Somehow I have recevied multiple datapoints. This should not be possible. I have logged this odd behaviour")
     elif len(content) <= 0:
          return await ctx.send("Tag not found. Check capitilization, it's **CaSe SeNsItIvE**")
     elif content[0][0] == ctx.author.id:
          c.execute("DELETE FROM notes WHERE name =?", (name,))
          cur.commit()
          return await ctx.send("Tag **"+name+"** has been perminantly deleted.")
     else:
          return await ctx.send("You are not the author of this tag.")

#edit tags
@tag.subcommand()
async def edit(ctx:molter.MolterContext, name=None):
    async def check(msg):
         if int(msg.author.id) == int(ctx.author.id):
              return True
         else:
              return False
    if name == None:
        await ctx.send("What is the name of the tag you're deleting?")
        try:
            msg: interactions.Message = await wf.wait_for(bot, "on_message_create", check=check, timeout=15)
            name = msg.content
        except asyncio.TimeoutError:
            return await ctx.send("Sorry, I cant wait any longer, please try again.")
    
    entry = c.execute("SELECT * FROM notes WHERE name =?", (name,)).fetchall();
    if len(entry) <= 0:
         return await ctx.send("Tag not found. Check capitilization, it's **CaSe SeNsItIve**")
    elif entry[0][3] != ctx.author.id:
         return await ctx.send("You are not the author of this tag.")
    
    await ctx.send("The current content inside of "+name+" is: "+entry[0][2]+"\n\nWhat would you like to change this to?")
    try:
            msg1: interactions.Message = await wf.wait_for(bot, "on_message_create", check=check, timeout=15)
    except asyncio.TimeoutError:
            return await ctx.send("Sorry, I cant wait any longer, please try again.")

    c.execute("UPDATE notes SET data = ? WHERE name = ?",(msg1.content, name))
    cur.commit()
    await ctx.send("Update complete!")

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

    
    channel = await interactions.get(bot, interactions.Channel, object_id=int(id))

    #Janky ass work arround, using http requests instead of the channel.typing because it 
    #kept giving me an error.
    for x in splitData: 
        async with Typing(ctx._http, int(id)):      
            await asyncio.sleep(len(x)*0.015)
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
         
@bot.event
async def on_message_create(msg: interactions.Message):
     if msg.channel_id != 1082659256156815401 or msg.author.bot:
          return
     elif msg.content.startswith("speak:"):
          
          interp = await ter.interprate(msg)

          while interp == '':
               await asyncio.sleep(.2);
          
          channel = await msg.get_channel()
          
          await channel.send(interp)


bot.start()