import numpy as np
from numpy import cos as c, sin as s, pow, sqrt
from typing import Union
from vector import Vector3
from rotation import Rotation

def normal(x, y, z):
    return np.sqrt(np.pow(x, 2) + np.pow(y, 2) + np.pow(z, 2))

class Link:
    def __init__(self, *args: Union[int, float, list, tuple, np.float64, np.uint64, np.ndarray, np.matrix, Vector3]):
        self.transform: np.matrix
        self.offset: np.matrix = np.matrix([0, 0, 0])
        self.rotation = Rotation(0, 0, 0)
        self.system = self.rotation.def_matrix()
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
            elif type(args[0]) == Vector3:
                self.transform = args[0].vec2matrix
            else:
                raise AttributeError(
                    'Either a  list, tuple,  numpy.ndarray, numpy.matrix or 3 positional arguments (x, y, z) should be given')

        elif len(args) == 3:
            self.transform = np.matrix([args[0], args[1], args[2]])
        else:
            raise ValueError(
                'Either a  list, numpy.ndarray, numpy.matrix or 3 positional arguments (x, y, z) should be given')

    def __str__(self):
        ef = self.end_effector
        return f'Link-EF[X: {ef.item(0)}, Y: {ef.item(1)}, Z: {ef.item(2)}]'

    @property
    def x(self):
        return self.end_effector.item(0)

    @property
    def y(self):
        return self.end_effector.item(1)

    @property
    def z(self):
        return self.end_effector.item(2)

    def set_rotation(self, x, y, z, order:str='yzx'):
        self.rotation = Rotation(x, y, z, order)

    def set_transform(self, *args: Union[int, float, list, tuple, np.float64, np.uint64, np.ndarray, np.matrix, Vector3]):
        if len(args) == 1:
            if type(args[0]) == list or type(args[0]) == tuple or type(args[0]) == np.ndarray:
                if len(args[0]) == 3:
                    self.transform = np.matrix([args[0], args[1], args[2]])
                else:
                    raise AttributeError(
                        f'Length of list/tuple/numpy.ndarray/numpy.matrix is not valid. Expected length: 3, Received: {len(args[0])}')
            elif type(args[0]) == np.matrix:
                self.transform = args[0]
            elif type(args[0]) == Vector3:
                self.transform = args[0].vec2matrix
            else:
                raise AttributeError(
                    'Either a  list, tuple,  numpy.ndarray, numpy.matrix or 3 positional arguments (x, y, z) should be given')

        elif len(args) == 3:
            self.transform = np.matrix([args[0], args[1], args[2]])
        else:
            raise ValueError(
                'Either a  list, numpy.ndarray, numpy.matrix or 3 positional arguments (x, y, z) should be given')

    def update_chain(self):
        if self.last_link is not None:
            last_system, last_offset = self.last_link.update_chain()
            self.system: np.matrix = last_system
            self.offset: np.matrix = last_offset
            return self.rotation.rot_matrix * last_system, last_offset + self.local_end_effector
        return self.rotation.rot_matrix * self.system, self.end_effector

    def assign_last_link(self, last_link=None):
        if last_link is None:
            return
        self.last_link: Link = last_link
        last_system, last_offset = self.last_link.update_chain()
        self.system: np.matrix = last_system
        self.offset: np.matrix = last_offset

    @property
    def local_end_effector(self):
        m: np.matrix = self.transform * self.rotation.rot_matrix * self.system
        return m.flatten()

    @property
    def end_effector(self):
        m: np.matrix = self.transform * self.rotation.rot_matrix * self.system + self.offset
        return m.flatten()

    def set_relative_vector(self, vec: Vector3):
        m = vec.vec2matrix - self.end_effector
        j = m * (self.system * self.rotation.rot_matrix).transpose()
        return Vector3(j)