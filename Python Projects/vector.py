import numpy as np
from numpy import cos as c, sin as s, pow, sqrt

from typing import Union

def euler_rotation(roll, pitch, yaw) -> np.matrix:
    # https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles#:~:text=heading%2C%20pitch%2C%20bank.-,Rotation%20matrices,-%5Bedit%5D
    r = np.matrix([[c(yaw), -s(yaw), 0], [s(yaw), c(yaw), 0], [0, 0, 1]])
    p = np.matrix([[c(pitch), 0, s(pitch)], [0, 1, 0], [-s(pitch), 0, c(pitch)]])
    y = np.matrix([[1, 0, 0], [0, c(roll), -s(roll)], [0, s(roll), c(roll)]])
    return r * p * y


class Vector3:
    pass

class Vector3:
    def __init__(self, x: Union[int, float, np.uint64, np.float64], y: Union[int, float, np.uint64, np.float64], z: Union[float, np.uint64, np.float64]):
        self.x = x
        self.y = y
        self.z = z

    @property
    def vec2matrix(self):
        return np.matrix([self.x, self.y, self.z])

    def matrix2vec(self, matrix):
        x = matrix.item((0, 0))
        y = matrix.item((0, 1))
        z = matrix.item((0, 2))
        return x, y, z

    def __str__(self):
        return f'[X: {self.x}, Y: {self.y}, Z: {self.z}]'

    def __abs__(self):
        return sqrt(pow(self.x, 2) + pow(self.y, 2) + pow(self.z, 2))

    def __add__(self, other):
        if type(other) == Vector3:
            self.x + other.x
            self.y + other.y
            self.z + other.z

    def __sub__(self, other):
        if type(other) == Vector3:
            self.x - other.x
            self.y - other.y
            self.z - other.z

    def rotate(self, x: Union[int, float, np.uint64, np.float64], y: Union[int, float, np.uint64, np.float64], z: Union[int, float, np.uint64, np.float64], mode: str = 'rad', rounding: int = 4):
        if mode == 'deg':
            x = np.deg2rad(x)
            y = np.deg2rad(y)
            z = np.deg2rad(z)
        elif mode != 'rad':
            raise Exception
        vec = self.vec2matrix * euler_rotation(x, y, z)
        self.x, self.y, self.z = self.matrix2vec(vec)


    def rotate_around(self, x: Union[int, float, np.uint64, np.float64], y: Union[int, float, np.uint64, np.float64], z: Union[int, float, np.uint64, np.float64], vec: Union[Vector3]):
        m = self.vec2matrix - vec.vec2matrix
        v = m * euler_rotation(x, y, z)
        self.x, self.y, self.z = self.matrix2vec(v)
