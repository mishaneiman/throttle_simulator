#################
# input: expected_acceleration_graph (np-array)
#            expected_acc_point = [time, acceleration]
#        sampled_acceleration_graph (np-array)
#            sampled_acc_point = [time, acceleration]

# delay =  sampled_acc_point.time - expected_acc_point.time

# output: delay (number)
#################

import numpy as np
from scipy.optimize import least_squares
import matplotlib.pyplot as plt
import matplotlib.animation

"""builds the piecewise linear function between the pulses over system time"""

def v_from_pulses(pulses, acceleration_values, dense_sampled_t, v_in):
    
    v_out = v_in.copy()

    for i,t_p in enumerate(pulses):
        
        if i==0:
            
            v_out[dense_sampled_t <= np.floor(t_p)] = 0
            v_prev = 0
            t_prev = t_p
            
        else:
            
            active_inds = np.logical_and(dense_sampled_t > np.floor(t_prev), dense_sampled_t <= np.floor(t_p))
            v_out[active_inds] = (dense_sampled_t[active_inds] - t_prev)*acceleration_values[i-1]+v_prev
            v_prev = (t_p - t_prev)*acceleration_values[i-1]+v_prev
            t_prev = t_p
        
    active_inds = dense_sampled_t > np.floor(t_prev)
    v_out[active_inds] = (dense_sampled_t[active_inds] - t_prev)*acceleration_values[i-1]+v_prev
    
    return v_out

def err_func(sugg):
   
    """Returns the difference between the desired signal and the actual (delayed, noisy and multiplied by gain) signal shifted by a suggested time interval for optimization
    sugg[0] is the suggested gain, sugg[1] is the suggested delay""" 
    
    v_suggested = sugg[0]* (v_from_pulses(pulses + sugg[1], acceleration_values, dense_sampled_t, v_as_dense))
    return v_suggested - v_shifted


"""main method"""

DENSE_STEP = 0.1
UNKNOWN_GAIN = 5

pulses = np.sort(np.random.uniform(0, 500, size = int(np.random.uniform(50,150)))) # the times at which the accelerator pedal is manipulated
acceleration_values = np.random.uniform(-20, 20, size = pulses.shape) # the acceleration values at each pulse

delay = np.random.uniform()*np.max(pulses)/3 # the standard system delay

dense_sampled_t_min = np.floor(pulses[0]/DENSE_STEP)*DENSE_STEP
dense_sampled_t_max = np.ceil((pulses[-1]+np.max(delay))/DENSE_STEP)*DENSE_STEP
dense_sampled_t = np.arange(dense_sampled_t_min, dense_sampled_t_max, DENSE_STEP) # system time

shift = np.random.normal(delay, 0.3, size = pulses.shape) # adds a variance to the delay so that each pulse is delayed differently
disturbance = np.random.normal(0, 5, size = dense_sampled_t.shape)
v_as_dense = np.zeros(shape=dense_sampled_t.shape)*np.nan
v_org = v_from_pulses(pulses, acceleration_values, dense_sampled_t, v_as_dense)
v_shifted = UNKNOWN_GAIN * (v_from_pulses(pulses+shift, acceleration_values, dense_sampled_t, v_as_dense) + disturbance)    


found_gain, found_delay = least_squares(err_func, np.array([0,0])).x

plt.plot(pulses, acceleration_values, '+:')
plt.clf()
plt.plot(dense_sampled_t, v_shifted, dense_sampled_t, v_org) 
