import numpy as np
from numpy import sin as s, cos as c

class Rotation:

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


    def roll_rotation(self, roll):  # X-Rotation
        return np.matrix([[1, 0, 0], [0, c(roll), -s(roll)], [0, s(roll), c(roll)]])

    def pitch_rotation(self, pitch):  # Y-Rotation
        return np.matrix([[c(pitch), 0, s(pitch)], [0, 1, 0], [-s(pitch), 0, c(pitch)]])

    def yaw_rotation(self, yaw) -> np.matrix:  # Z-Rotation
        return np.matrix([[c(yaw), -s(yaw), 0], [s(yaw), c(yaw), 0], [0, 0, 1]])

    def euler_rotation(self, roll, pitch, yaw) -> np.matrix:
        # https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles#:~:text=heading%2C%20pitch%2C%20bank.-,Rotation%20matrices,-%5Bedit%5D
        return self.yaw_rotation(yaw) * self.pitch_rotation(pitch) * self.roll_rotation(roll)

    @property
    def rot_matrix(self, order: str = 'zyx'):
        return self.euler_rotation(self.x, self.y, self.z)