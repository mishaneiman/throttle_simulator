import rospy
from sensor_msgs.msg import Joy
from std_msgs.msg import String

def callback(data):

    if data.axes[6] == 1.0:
        move = "left"
    if data.axes[6] ==