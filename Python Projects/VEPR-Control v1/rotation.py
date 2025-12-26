import numpy as np
from numpy import sin as s, cos as c


def roll_rotation(roll):  # X-Rotation
    return np.matrix([[1, 0, 0], [0, c(roll), -s(roll)], [0, s(roll), c(roll)]])


def pitch_rotation(pitch):  # Y-Rotation
    return np.matrix([[c(pitch), 0, s(pitch)], [0, 1, 0], [-s(pitch), 0, c(pitch)]])


def yaw_rotation(yaw) -> np.matrix:  # Z-Rotation
    return np.matrix([[c(yaw), -s(yaw), 0], [s(yaw), c(yaw), 0], [0, 0, 1]])

class Rotation:

    def __init__(self, x, y, z, order:str='zyx'):
        self.x = x
        self.y = y
        self.z = z
        self.order = order

    def def_matrix(self) -> np.matrix:
        return np.matrix([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])

    @property
    def rot_matrix(self, order: str = 'zyx'):
        vec = self.def_matrix()
        for r in list(self.order):
            if r == 'x':
                vec = vec * roll_rotation(self.x)
            if r == 'y':
                vec = vec * pitch_rotation(self.y)
            if r == 'z':
                vec = vec * yaw_rotation(self.z)
        return vec