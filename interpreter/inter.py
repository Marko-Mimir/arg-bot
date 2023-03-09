import json
import interactions

def init():
    global data 
    data = None

async def interprate(msg : interactions.Message):
    global data 

    if data == None:
        f = open("./json/livi.json")
        data = json.load(f)
        f.close

    isIn = []
    wasin = False
    questions = data["1"].keys()
    for x in questions:
        if x in msg.content.lower():
            isIn.append(x)
            wasin = True

    gen = data["2"]["gen"].keys()
    for x in gen:
        if x in msg.content.lower() and not wasin:
            isIn.append(x)
    
    if len(isIn) > 1:
        return "Please narrow down your question :("
    elif wasin:
        pass #do question stuff
        try:
            questions = data["1"][isIn[0]].keys()
        except IndexError:
            await log(msg.content)
            return data["2"]["err"]
        for x in questions:
            if x in msg.content.lower():
                isIn.append(x)
                break;
        try:
            data["1"][isIn[0]][isIn[1]].keys()
        except AttributeError:
            return data["1"][isIn[0]][isIn[1]]
        except IndexError:
            await log(msg.content)
            return data["2"]["err"]

        questions = data["1"][isIn[0]][isIn[1]].keys()
        for x in questions:
            if x in msg.content.lower():
                isIn.append(x)
                return data["1"][isIn[0]][isIn[1]][isIn[2]]
    

    elif len(isIn) >= 1:
        return data["2"]["gen"][isIn[0]]

    isIn = []
    if isIn == []:
        
        await log(msg.content)
        isIn.append(data["2"]["err"])
    return isIn[0]


async def log(content):
    try:
            f = open("log.txt", "x")
            f.close();
    except FileExistsError:
            pass
    f = open(str("log")+".txt", "a")
    f.write(content+"\n\n");
    f.close()