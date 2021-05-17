x = []
with open("data/data", "r") as file:
    x = eval(file.read())


keys = list(x["pos"].keys())
for key in keys:
    if key[:8] == "MZ-3-004":
        del x["pos"][key]



with open("data/data", "w") as file:
    file.write(str(x))