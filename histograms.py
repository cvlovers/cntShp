""" A script calculating how many frames each sheep spends on the screen & then creates a histogram.
The histogram shows the frame count intervals and the number of sheep having frame counts in those intervals.
"""

import json
import numpy as np
import statistics
import sys
from matplotlib import pyplot as plt
from scipy.stats import norm


file = open(sys.argv[1])
data = json.load(file)

# Speed data is currently thought to be unneeded, and thus is commented out

frame_list = []
# speed_list = []


for item in data:
    frame_count = data[item]["pos"][-1]["frame"] - data[item]["pos"][0]["frame"]
    # speed = abs((data[item]["pos"][-1]["x"] - data[item]["pos"][0]["x"]**2) -
                # (data[item]["pos"][-1]["y"] - data[item]["pos"][0]["y"]**2)) ** 0.5 / frame_count
    # speed = "%.2f" % speed
    # speed = float(speed)

    # d = {"Sheep ID": data[item]["id"], "Frame Count": frame_count, "Sheep Speed": speed}

    frame_list.append(frame_count)
    # speed_list.append(speed)

max_frame = max(frame_list)
# max_speed = max(speed_list)

frame_array = np.array(frame_list)
# speed_array = np.array(speed_list)


file.close()


# plt.hist(speed_array, color="lightgreen", bins=25, alpha=0.5)
# plt.ylabel('Sheep Frequency')
# plt.xlabel('Speed Values')
# print(max_speed)
# plt.xticks(np.arange(0, max_speed, 2))
# plt.show()


plt.hist(frame_array, color="pink", bins=100, alpha=0.75)
plt.ylabel('Sheep Frequency')
plt.xlabel('Frame Count')
plt.xticks(np.arange(0, max_frame, 125))
plt.show()

x_axis = np.arange(0, max_frame, 1)

mean = statistics.mean(x_axis)
sd = statistics.stdev(x_axis)

plt.plot(x_axis, norm.pdf(x_axis, mean, sd))
plt.show()
