import json
from numpy import NaN
import pandas as pd
import matplotlib.pyplot as plt

df=pd.DataFrame(columns=["id","frame difference","x_difference","y_difference","avg_speed"])

with open('./result.json') as jsonfile:
    data = json.load(jsonfile)

for key in data:
    first_fr=data[key]["pos"][0]
    last_fr=data[key]["pos"][-1]
    frame_diff=last_fr["frame"]-first_fr["frame"]
    x_diff=last_fr["x"]-first_fr["x"]
    y_diff=last_fr["y"]-first_fr["y"]
    speed=((x_diff**2+y_diff**2)**(0.5))/frame_diff
    df.loc[len(df)]=[key,frame_diff,x_diff,y_diff,speed]

print(df)
print("Average sheep speed:",df["avg_speed"].mean())
df["avg_speed"].plot()
plt.show()

print("Average number of frames spent on screen",df["frame difference"].mean())
df["frame difference"].plot()
plt.show()
