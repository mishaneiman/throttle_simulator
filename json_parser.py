import json
import numpy as np
import matplotlib.pyplot as plt
import glob

file_names = glob.glob("_arazim_driver_imu-*")
data = []
for file_name in file_names:    
    with open(file_name) as json_data:
        d = json.load(json_data)
    data.extend(d)
    

    
acceleration_values = [accels.values()[-2] for accels in data]
    
y_accel = [x.values()[0] for x in acceleration_values]
x_accel = [y.values()[1] for y in acceleration_values]
z_accel = [z.values()[2] for z in acceleration_values]

y_vel = np.cumsum(y_accel)
x_vel = np.cumsum(x_accel)
z_vel = np.cumsum(z_accel)

t = np.arange(0, len(y_vel))

#plt.plot(t, x_vel)
#plt.plot(t, y_vel)

x = x_vel * t
y = y_vel * t

plt.plot(x, y)
plt.axes().set_aspect('equal')

