import json
import sys


file = open(sys.argv[1])
data = json.load(file)

stationary_objects = []

for item in data:
    displacement = abs((data[item]["pos"][-1]["x"] - data[item]["pos"][0]["x"]**2) -
                       (data[item]["pos"][-1]["y"] - data[item]["pos"][0]["y"]**2)) ** 0.5

    if displacement <= 20:
        stationary_objects.append(data[item]["id"])

print(stationary_objects)
