import numpy as np
import sympy

def roll_rotation(idx): # X-Rotation
    return sympy.Matrix([[1, 0, 0], [0, f"c{idx}", f"-s{idx}"], [0, f"s{idx}", f"c{idx}"]])
    # return np.matrix([[1, 0, 0], [0, c(roll), -s(roll)], [0, s(roll), c(roll)]])

def pitch_rotation(idx): # Y-Rotation
    return sympy.Matrix([[f"c{idx}", 0, f"s{idx}"], [0, 1, 0], [f"-s{idx}", 0, f"c{idx}"]])
    # return np.matrix([[c(pitch), 0, s(pitch)], [0, 1, 0], [-s(pitch), 0, c(pitch)]])

def yaw_rotation(idx): # Z-Rotation
    return sympy.Matrix([[f"c{idx}", f"-s{idx}", 0], [f"s{idx}", f"c{idx}", 0], [0, 0, 1]])
    # return np.matrix([[c(yaw), -s(yaw), 0], [s(yaw), c(yaw), 0], [0, 0, 1]])


print(roll_rotation("x") * pitch_rotation("y") * yaw_rotation("z"))

# [[cy*cz, -cy*sz, sy], [cx*sz + cz*sx*sy, cx*cz - sx*sy*sz, -cy*sx], [-cx*cz*sy + sx*sz, cx*sy*sz + cz*sx, cx*cy]]