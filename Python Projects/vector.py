import numpy as np
from numpy import cos as c, sin as s, pow, sqrt

from typing import Union


def roll_rotation(roll): # X-Rotation
    return np.matrix([[1, 0, 0], [0, c(roll), -s(roll)], [0, s(roll), c(roll)]])

def pitch_rotation(pitch): # Y-Rotation
    return np.matrix([[c(pitch), 0, s(pitch)], [0, 1, 0], [-s(pitch), 0, c(pitch)]])

def yaw_rotation(yaw): # Z-Rotation
    return np.matrix([[c(yaw), -s(yaw), 0], [s(yaw), c(yaw), 0], [0, 0, 1]])

def euler_rotation(roll, pitch, yaw) -> np.matrix:
    # https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles#:~:text=heading%2C%20pitch%2C%20bank.-,Rotation%20matrices,-%5Bedit%5D
    return yaw_rotation(yaw) * pitch_rotation(pitch) * roll_rotation(roll)

def normal(x, y, z):
    return np.sqrt(np.pow(x, 2) + np.pow(y, 2) + np.pow(z, 2))

def normalize(x, y, z):
    m = max(x, y, z)
    return x / m, y / m, z / m


class Vector3:

    def __init__(self, *args: Union[int, float, list, tuple, np.float64, np.uint64, np.ndarray, np.matrix]):
        self.x: float
        self.y: float
        self.z: float
        if len(args) == 1:
            if type(args[0]) == list or type(args[0]) == tuple or type(args[0]) == np.ndarray:
                if len(args[0]) == 3:
                    self.x = args[0][0]
                    self.y = args[0][1]
                    self.z = args[0][2]
                else:
                    raise AttributeError(
                    f'Length of list/tuple/numpy.ndarray/numpy.matrix is not valid. Expected length: 3, Received: {len(args[0])}')
            elif type(args[0]) == np.matrix:
                self.x = args[0].item(0, 0)
                self.y = args[0].item(0, 1)
                self.z = args[0].item(0, 2)
            else:
                raise AttributeError(
                    'Either a  list, tuple,  numpy.ndarray, numpy.matrix or 3 positional arguments (x, y, z) should be given')

        elif len(args) == 3:
            self.x = args[0]
            self.y = args[1]
            self.z = args[2]

        else:
            raise ValueError('Either a  list, numpy.ndarray, numpy.matrix or 3 positional arguments (x, y, z) should be given')

    def __str__(self):
        return f'[X: {self.x}, Y: {self.y}, Z: {self.z}]'

    def __abs__(self):
        return sqrt(pow(self.x, 2) + pow(self.y, 2) + pow(self.z, 2))

    def __add__(self, other):
        if type(other) == Vector3:
            return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
        elif type(other) == list or type(other) == tuple or type(other) == np.ndarray:
            if len(other) == 3:
                return Vector3(self.x + other[0], self.y + other[1], self.z + other[2])
            else:
                raise Exception
        elif type(other) == np.matrix:
            return Vector3(self.vec2matrix + other)

    def __sub__(self, other):
        if type(other) == Vector3:
            return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
        elif type(other) == list or type(other) == tuple or type(other) == np.ndarray:
            if len(other) == 3:
                return Vector3(self.x - other[0], self.y - other[1], self.z - other[2])
            else:
                raise Exception
        elif type(other) == np.matrix:
            return Vector3(self.vec2matrix - other)

    def __mul__(self, other):
        if type(other) == Vector3:
            return Vector3(self.x * other.x, self.y * other.y, self.z * other.z)
        elif type(other) == list or type(other) == tuple or type(other) == np.ndarray:
            if len(other) == 3:
                return Vector3(self.x * other[0], self.y * other[1], self.z * other[2])
            else:
                raise Exception
        elif type(other) == np.matrix:
            return Vector3(self.vec2matrix * other)

    @property
    def vec2matrix(self):
        return np.matrix([self.x, self.y, self.z])

    def matrix2vec(self, matrix):
        x = matrix.item((0, 0))
        y = matrix.item((0, 1))
        z = matrix.item((0, 2))
        return x, y, z

    def rotate(self, x: Union[int, float, np.uint64, np.float64], y: Union[int, float, np.uint64, np.float64], z: Union[int, float, np.uint64, np.float64], mode: str = 'rad', order: str='yzx'):
        if mode == 'deg':
            x = np.deg2rad(x)
            y = np.deg2rad(y)
            z = np.deg2rad(z)
        elif mode != 'rad':
            raise Exception
        vec = self.vec2matrix
        for r in list(order):
            if r == 'x':
                vec = vec * roll_rotation(x)
            if r == 'y':
                vec = vec * pitch_rotation(y)
            if r == 'z':
                vec = vec * yaw_rotation(z)
        self.x, self.y, self.z = self.matrix2vec(vec)
        return vec

    def rotate_axis(self, rot: Union[int, float, np.uint64, np.float64], axis: str, mode: str = 'rad'):
        if mode == 'deg':
            rot = np.deg2rad(rot)
        elif mode != 'rad':
            raise Exception
        m = self.vec2matrix
        if axis == 'x':
            m = m * roll_rotation(rot)
        elif axis == 'y':
            m = m * pitch_rotation(rot)
        elif axis == 'z':
            m = m * yaw_rotation(rot)
        else:
            raise Exception
        self.x, self.y, self.z = self.matrix2vec(m)

    def rotate_around(self, x: Union[int, float, np.uint64, np.float64], y: Union[int, float, np.uint64, np.float64], z: Union[int, float, np.uint64, np.float64], vec):
        if type(vec) == list or type(vec) == tuple or type(vec) == np.ndarray or type(vec) == np.matrix:
            vec = Vector3(vec)
        m = self.vec2matrix - vec.vec2matrix
        v = m * euler_rotation(x, y, z)
        self.x, self.y, self.z = self.matrix2vec(v)

    def align_to_lign(self, vec1, vec2):
        x = np.atan2(abs(vec2.z - vec1.z), np.sqrt(np.pow(abs(vec2.y - vec1.y), 2) + np.pow(abs(vec2.z - vec1.z), 2)))
        y = np.atan2(abs(vec2.z - vec1.z), np.sqrt(np.pow(abs(vec2.x - vec1.x), 2) + np.pow(abs(vec2.y - vec1.y), 2)))
        z = np.atan2(abs(vec2.y - vec1.y), np.sqrt(np.pow(abs(vec2.x - vec1.x), 2) + np.pow(abs(vec2.z - vec1.z), 2)))
        v = np.matrix([[normal(self.x, self.y, self.z), 0, 0], [0, 0, 0], [0, 0, 0]]) * euler_rotation(x, y, z)
        self.x, self.y, self.z = self.matrix2vec(v)
        return x, y, z
