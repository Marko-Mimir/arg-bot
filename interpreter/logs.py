#logs :)
import interactions
import json
import datetime

def init():
    #the check to see if you have to cooldown
    global runtimes
    runtimes = 0
    
    #Cooldown handeler
    global time
    time = None
    
    #Holds JSON data
    global data 
    data = None

    #Holds arguments
    global name
    name = None

async def log(msg: interactions.Message):
    global data 
    global runtimes
    global name
    global time

    if data == None:
        f = open("./json/logs.json")
        data = json.load(f)
        f.close
    
    start_channel = await msg.get_channel()

    
    name = start_channel.name.lower().split("-")

    #Key-Symbols
    if(msg.content.startswith("!")):
        return
    elif(msg.content.startswith(">")):
        await start_channel.send("Please do not use `>` to prefix log commands. I instead moniter any message in <#1088557069281529986>.")
        return
    
    #subcommands
    if(msg.content.lower().startswith("cd") or msg.content.lower().startswith("change")):
        if time != None:
            now = datetime.datetime.now()
            d = False
            x = str(now.strftime("%d,%H,%M"))
            x = x.split(",")
            b = 0
            for i in x:
                if int(i)>int(time[b]):
                    d = True
                    runtimes == 0
                    break
                b += 1
            
            if not d:
                await start_channel.send(f"You are currently on cooldown, wait untill <t:{time[3]}:R>")
                return
            else:
                time = None
        args = msg.content.lower().split(" ")
        diir = data
        if not args[1].startswith("root"):
            for x in name:
                diir = diir[x]
        args.pop(0)
        args = args[0].split("/")
        for x in args:
            try:
                diir = diir[x]
            except KeyError:
                await start_channel.send("Directory not found: `"+x+"`\n\nplease make sure you are only using the name. not including . or /")
                return
            except Exception as e:
                await start_channel.send("Error code raised: `"+str(e)+"`")
                return
        if type(diir) == str:
            await start_channel.send("My systems have detected that this is a XSW file. Please just say the file name without the cd command.")
            return
        x = diir["NAME"]
        await start_channel.set_name(f"{x}")
        x = x.replace(" ", "/")
        await start_channel.send(f"Changing active directory to: `{x}/`")
        runtimes+=1
        if runtimes == 2:
            y = str(datetime.datetime.now().strftime("%d, %H, %M"))
            y = y.split(",")
            y[2] = int(y[2])+10
            v = str(datetime.datetime.now().timestamp() + 10*60)
            v = v.split(".")
            v = v[0]
            y.append(v)
            time = y
        return
    elif(msg.content.lower().startswith("debug") and msg.author.id == 350967470934458369):
        runtimes == 2
        y = str(datetime.datetime.now().strftime("%d, %H, %M"))
        y = y.split(",")
        y[2] = int(y[2])+10
        v = str(datetime.datetime.now().timestamp() + 10*60)
        v = v.split(".")
        v = v[0]
        y.append(v)
        time = y
        return
    elif(msg.content.lower().startswith("help")):
        await start_channel.send((
            "Listing avaliable sub commands: \n\n```list -> List the current avaliable and re-discovered files and directories.\ncd -> Change directory, you can change to any directory listed with command list. \n{Syntax:[cd root/(DIRECTORY NAME)] OR [cd (DIRECTORY NAME)]}\n\nPLEASE KEEP IN MIND: I can only change directorys 2 times per 10 minutes. I will let you know when you excede this rate limit\n\n\nTo view a file just say the file name. \nThank you!```"
        ))
    elif(msg.content.lower().startswith("list all")):
        await start_channel.send("`Unable to list all files due to processing error.`")
        return
    elif(msg.content.lower().startswith("list")):
        diir = data
        for x in name:
            diir = diir[x]
        await start_channel.send("Current avaliable files: "+diir["LST"]+"")
        return#list surface level files
    elif(msg.content.lower().startswith("root")):
        if time != None:
            now = datetime.datetime.now()
            d = False
            x = str(now.strftime("%d,%H,%M"))
            x = x.split(",")
            b = 0
            for i in x:
                if int(i)>int(time[b]):
                    d = True
                    runtimes == 0
                    break
                b += 1
            
            if not d:
                await start_channel.send(f"You are currently on cooldown, wait untill <t:{time[3]}:R>")
                return
            else:
                time = None
                    
        if start_channel.name == "root":
            await start_channel.send("Directory is already focused on `root`!")
            return
        x = data["root"]["NAME"]
        await start_channel.set_name(f"{x}")
        await start_channel.send("Changing active directory to: `root/`")
        runtimes+=1
        if runtimes == 2:
            y = str(datetime.datetime.now().strftime("%d, %H, %M"))
            y = y.split(",")
            y[2] = int(y[2])+10
            v = str(datetime.datetime.now().timestamp() + 10*60)
            v = v.split(".")
            v = v[0]
            y.append(v)
            time = y
    else:
        diir = data
        for x in name:
            diir = diir[x]
        try:
            z = diir[msg.content.lower()]
        except KeyError:
            await start_channel.send("Sorry, i dont recognize this command or file name, if this is a comment, start with `!`, if this is a command please try `help`")
            return
        if type(z)==dict:
            await start_channel.send("My systems have detected this is a directory. Please choose an .XSW file.")
            return
        else:
            await start_channel.send(z)
            return