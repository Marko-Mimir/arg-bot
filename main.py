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

isEnabled = True
isConnectSent = False

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

#enable livi
@molter.prefixed_command()
async def able(ctx:molter.MolterContext):
     global isEnabled
     if isEnabled:
          isEnabled = False
     else:
          isEnabled = True

@molter.prefix_command()
async def help(ctx:molter.MolterContext, helparg = None):
     if helparg == None:
          await ctx.reply("ERROR: `Help branch needed`")
          return
     if helparg.lower() == "tag":
          await ctx.reply('I can hold a dictionary of any tag. To get started do >tag create to read tags do >tag [name] to edit tags to >tag edit [name] and to delete tags do >tag delete [name] you can also list the tags you have created with >tag list.')
     elif helparg.lower() == "speak":
          await ctx.reply('To speak with me prefix your message with `speak:` or `s:` (no longer case sensitive). Be careful, I am very limited as of right now, but I am always learning and hopefully we can help each other.')
     elif helparg.lower() == "connect":
          await ctx.reply("The command >connect, connects livi to its old architecture, removing the limits put in place by IMTT, and connecting to this server that we don't know too much about. Debug purposes only, and for exploring the past. To revert do >disconnect")
     elif helparg.lower() == "suggest":
          await ctx.reply("SYNTAX: >suggest [Suggestion]\n\n*If suggestion is multiple words they must be surrounded in quotes.")
     else:
          await ctx.reply("Unknown help branch. Avaliable help branches: `tag`, `speak`, `connect`, and `suggest`")


@molter.prefix_command()
async def connect(ctx:molter.MolterContext):
     global isEnabled
     global isConnectSent
     if isConnectSent == True:
          await ctx.send("**Connection Request is `already sent`!**")
          return
     await ctx.send("Sending Connection Request")
     mchannel = await interactions.get(bot, interactions.Channel, object_id=int(1084989399835607101))
     await mchannel.send("<@350967470934458369> " + "HOLY SHIT ANSWER PLSS")
     isConnectSent = True

@molter.prefix_command()
async def disconnect(ctx:molter.MolterContext):
     global isEnabled
     global isConnectSent
     if isConnectSent == False:
          return
     if isEnabled == True:
          await ctx.send("Cancelling")
          isConnectSent = False
          return
     await ctx.send("Disconnecting from `IGNO` servers")
     mchannel = await interactions.get(bot, interactions.Channel, object_id=int(1084989399835607101))
     await mchannel.send("<@350967470934458369> " + "DISABLED")
     await asyncio.sleep(.1)
     await ctx.send("Starting V0.4")
     await asyncio.sleep(.1)
     await ctx.send("Logging in...")
     await asyncio.sleep(.5)
     await ctx.send("Logged in! `fuchsia`")

     isConnectSent = False
     isEnabled = True
     
     

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
      global isEnabled
      if isEnabled == False:
           return;
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
     
    global isEnabled
    if isEnabled == False:
           return
    if name != None and content != None:
        c.execute("INSERT INTO notes VALUES(?, ?, ?, ?)", (name, ctx.author.name, content, str(ctx.author.id)))
        cur.commit();
        await ctx.send("Tag **"+name+"** was created!")
    elif name != None and content == None:
         await ctx.reply("What should go into this tag?")
         try:
            msg: interactions.Message = await wf.wait_for(bot, "on_message_create", check=check, timeout=60)
         except asyncio.TimeoutError:
              return await ctx.send("Sorry, I cant wait any longer, please try again.")
         if msg.content.lower() == "cancel":
               await ctx.send("cancelling")
               return
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

         if msg1.content.lower() == "cancel":
           await ctx.send("cancelling")
           return
         try:
            msg2: interactions.Message = await wf.wait_for(bot, "on_message_create", check=check, timeout=60)
         except asyncio.TimeoutError:
              return await ctx.send("Sorry, I cant wait any longer, please try again.")
         if msg2.content.lower() == "cancel":
               await ctx.send("cancelling")
               return
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
     global isEnabled
     if isEnabled == False:
           return
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
    
        if name.lower() == "cancel":
          await ctx.send("Cancelling...")
          return

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
    global isEnabled
    if isEnabled == False:
           return
    async def check(msg):
         if int(msg.author.id) == int(ctx.author.id):
              return True
         else:
              return False
    if name == None:
        await ctx.send("What is the name of the tag you're editing?")
        try:
            msg: interactions.Message = await wf.wait_for(bot, "on_message_create", check=check, timeout=15)
            name = msg.content
        except asyncio.TimeoutError:
            return await ctx.send("Sorry, I cant wait any longer, please try again.")
        if msg.content.lower() == "cancel":
           await ctx.send("canceling")
           return
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

    if msg1.content.lower == "cancel":
      await ctx.send("canceled")
      return
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

@molter.prefixed_command()
async def suggest(ctx:molter.MolterContext, suggestion=None):
     if suggestion == None:
          await ctx.reply("You did not include a suggestion!")
          return
     await ctx.reply("Suggested to V0.5 "+suggestion)
     mchannel = await interactions.get(bot, interactions.Channel, object_id=int(1084989399835607101))
     await mchannel.send("<@350967470934458369> " + suggestion)
#1086062318074474567

@molter.prefixed_command()
async def search(ctx:molter.MolterContext, suggestion=None):
     if suggestion == None:
          await ctx.reply("You did not include a search query!")
          return
     await ctx.reply("Searching for: "+suggestion)
     await ctx.send("I will let you know when i find an answer.")
     mchannel = await interactions.get(bot, interactions.Channel, object_id=int(1084989399835607101))
     await mchannel.send("<@350967470934458369> " + suggestion + " " + ctx.msg.id + " " + ctx.msg.channel_id)

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

@molter.prefixed_command()
async def pin(ctx:molter.MolterContext, msgid, channelid):
     message = await interactions.get(bot, interactions.Message, object_id=msgid, parent_id=channelid)
     await message.pin()

@molter.prefixed_command() #general 7a3f3b testing|testing|testing|testing|0|0
async def post(ctx:molter.MolterContext, id, color, bash):
     if not await ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
        return
     
     splint = bash.split("|")
     
     color = color[1:]
     need = "0x"
     hex_int = int(need+color,16)

     emb = interactions.Embed(title=splint[2])
     emb.footer = interactions.EmbedFooter(text=splint[4]+"  Likes | "+splint[5]+" Comments")
     emb.add_field('',splint[3])
     emb.color = hex_int
     emb.author = interactions.EmbedAuthor(name=splint[1])
     rem = ["<","#",">"]
     for x in rem:
          id = id.replace(x,"")
     channel = await interactions.get(bot, interactions.Channel, object_id=int(id))
     await channel.send(content=splint[0], embeds=[emb])
     

@bot.event
async def on_message_create(msg: interactions.Message):
     global isEnabled
     if msg.channel_id == 1085364318847123506 and not msg.content.startswith(">"):
          channel = await interactions.get(bot, interactions.Channel, object_id=int(1082360658244423690))
          async with Typing(bot._http, int(1082360658244423690)):      
                await asyncio.sleep(len(msg.content)*0.015)
                await channel.send(msg.content)

     if msg.channel_id != 1082659256156815401 and msg.channel_id != 1082360658244423690 or msg.author.bot:
          return
     if isEnabled == False:
           return
     elif msg.content.lower().startswith("speak:") or msg.content.lower().startswith('s:'):
          
          interp = await ter.interprate(msg)

          while interp == '':
               await asyncio.sleep(.2);
          if interp == "BLANK":
               pass
               mchannel = await interactions.get(bot, interactions.Channel, object_id=int(1084989399835607101))
               await mchannel.send("<@350967470934458369> " + msg.content)
               return
          
          channel = await msg.get_channel()
          
          await channel.send(interp)


bot.start()