import json
import numpy as np
import sys
from matplotlib import pyplot as plt


file = open(sys.argv[1])  # File content is gonna be result.json
data = json.load(file)


frame_list = []
speed_list = []


for item in data:
    frame_count = data[item]["pos"][-1]["frame"] - data[item]["pos"][0]["frame"]
    speed = abs((data[item]["pos"][-1]["x"] - data[item]["pos"][0]["x"]**2) -
                (data[item]["pos"][-1]["y"] - data[item]["pos"][0]["y"]**2)) ** 0.5 / frame_count
    speed = "%.2f" % speed

    d = {"Sheep ID": data[item]["id"], "Frame Count": frame_count, "Sheep Speed": speed}

    frame_list.append(frame_count)
    speed_list.append(speed)

max_frame = max(frame_list)
max_speed = max(speed_list)

frame_array = np.array(frame_list)
speed_array = np.array(speed_list)


file.close()


# Shows all the speed values
plt.hist(speed_array, color="lightgreen", bins=25, alpha=0.5)
plt.ylabel('Sheep Frequency')
plt.xlabel('Speed Values')
plt.show()


plt.hist(frame_array, color="pink", bins=5, alpha=0.75)
plt.ylabel('Sheep Frequency')
plt.xlabel('Frame Count')
plt.show()
