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

def def_matrix() -> np.matrix:
    return np.matrix([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ])

class Rotation:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z



class Link:
    def __init__(self, *args: Union[int, float, list, tuple, np.float64, np.uint64, np.ndarray, np.matrix]):
        self.system = def_matrix()
        self.transform: np.matrix
        self.offset: np.matrix = np.matrix([0, 0, 0])
        self.rotation = Rotation(0, 0, 0)
        self.last_link: Union[None, Link] = None
        if len(args) == 1:
            if type(args[0]) == list or type(args[0]) == tuple or type(args[0]) == np.ndarray:
                if len(args[0]) == 3:
                    self.transform = np.matrix([args[0], args[1], args[2]])
                else:
                    raise AttributeError(
                        f'Length of list/tuple/numpy.ndarray/numpy.matrix is not valid. Expected length: 3, Received: {len(args[0])}')
            elif type(args[0]) == np.matrix:
                self.transform = args[0]
            else:
                raise AttributeError(
                    'Either a  list, tuple,  numpy.ndarray, numpy.matrix or 3 positional arguments (x, y, z) should be given')

        elif len(args) == 3:
            self.transform = np.matrix([args[0], args[1], args[2]])
        else:
            raise ValueError(
                'Either a  list, numpy.ndarray, numpy.matrix or 3 positional arguments (x, y, z) should be given')

    def calc_rel_pos(self, transform, rotation):
        pass

    @property
    def x(self):
        return self.transform.item(0)

    @property
    def y(self):
        return self.transform.item(1)

    @property
    def z(self):
        return self.transform.item(2)

    def set_rotation(self, x, y, z):
        self.rotation.x = x
        self.rotation.y = y
        self.rotation.z = z

    def update_chain(self):
        if self.last_link is not None:
            last_system, last_transform = self.last_link.update_chain()
            self.system: np.matrix = last_system
            self.offset: np.matrix = last_transform
            return last_system * np.round(euler_rotation(self.rotation.x, self.rotation.y, self.rotation.z), 4), last_transform + self.transform * np.round(euler_rotation(self.rotation.x, self.rotation.y, self.rotation.z), 4)
        return self.system * np.round(euler_rotation(self.rotation.x, self.rotation.y, self.rotation.z), 4), self.transform * np.round(euler_rotation(self.rotation.x, self.rotation.y, self.rotation.z), 4)

    def assign_last_link(self, last_link=None):
        if last_link is None:
            return
        self.last_link: Link = last_link
        last_system, last_transform = self.last_link.update_chain()
        self.system: np.matrix = last_system
        self.offset: np.matrix = last_transform

    @property
    def end_effector(self):
        m: np.matrix = self.transform * np.round(euler_rotation(self.rotation.x, self.rotation.y, self.rotation.z), 4) + self.offset
        return m.flatten()


l1 = Link(100, 0, 0)
l1.set_rotation(0, 0, np.pi/2)
l2 = Link(100, 0, 0)
l2.set_rotation(0, 0, np.pi/4)
l2.assign_last_link(l1)