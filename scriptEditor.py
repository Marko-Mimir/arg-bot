import interactions
from interactions import Client, Intents
from interactions.ext import molter

import os


async def script(ctx):
    
    x = await makefile();

    f = open(str(x)+".txt", "x")
    f.close();
    f = open(str(x)+"txt", "w")

    f.write("temp");

    f.close


async def makefile():
    x = 0
    base_dir = os.path.dirname(os.path.realpath(__file__))
    fpath = "{}/"+str(x)
    fpath = fpath.format(base_dir)

    while os.path.isfile(fpath):
        x=+1
        fpath = "{}/"+str(x)
        fpath = fpath.format(base_dir)
    
    return x;

