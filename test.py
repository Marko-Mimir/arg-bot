import json

f = open("./json/livi.json")
data = json.load(f)
f.close

data["1"]["who"]["you"].keys()