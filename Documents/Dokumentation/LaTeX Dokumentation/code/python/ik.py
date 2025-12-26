import numpy as np
from numpy import cos as c, sin as s
def roll_rotation(roll):  # X-Rotation
    return np.matrix([[1, 0, 0], [0, c(roll), -s(roll)], [0, s(roll), c(roll)]])

def pitch_rotation(pitch):  # Y-Rotation
    return np.matrix([[c(pitch), 0, s(pitch)], [0, 1, 0], [-s(pitch), 0, c(pitch)]])

def yaw_rotation(yaw) -> np.matrix:  # Z-Rotation
    return np.matrix([[c(yaw), -s(yaw), 0], [s(yaw), c(yaw), 0], [0, 0, 1]])

def inverse_kinematics(x, y, z, rx, ry, rz, l1, l2, l3, l4):
    R_D = roll_rotation(rx) * pitch_rotation(ry) * yaw_rotation(rz)
    X_D = np.matrix([x, y, z]) - np.matrix([l4, 0, 0]) * R_D
    xd, yd, zd = X_D.tolist()[0]


    n_X_D = np.sqrt(np.pow(xd, 2) + np.pow(yd - l2, 2) + np.pow(zd, 2))
    q1 = np.arctan2(yd, xd)
    solutions_1 = [[q1], [q1 + np.pi]]
    c3 = (np.pow(xd, 2) + np.pow(zd, 2) + np.pow(yd - l1, 2) - np.pow(l2, 2) - np.pow(l3, 2))/(2 * l2 * l3)
    if c3 > 0:
        return None
    elif c3 == 1:
        q2 = np.atan2(yd - l1, np.hypot(xd, zd))
        q3 = 0
        solutions_2 = [[q2, q3]]
    elif c3 == -1 and n_X_D != 0:
        q2 = np.atan2(yd - l1, np.hypot(xd, zd))
        q3 = np.pi
        solutions_2 = [[q2, q3]]
    elif c3 == -1 and n_X_D == 0:
        q2 = 0
        q3 = np.pi
        solutions_2 = [[q2, q3]]
    else:
        q3_1 = np.arccos(c3)
        q2_1 = np.atan2(yd - l1, np.hypot(xd, zd)) - np.atan2(l3 * np.sin(q3_1), l2 + l3 * np.cos(q3_1))
        q3_2 = -np.arccos(c3)
        q2_2 = np.atan2(yd - l1, np.hypot(xd, zd)) - np.atan2(l3 * np.sin(q3_2), l2 + l3 * np.cos(q3_2))
        solutions_2 = [[q2_1, q3_1], [q2_2, q3_2]]
    solutions_3 = []
    for i in solutions_1:
        for j in solutions_2:
            R_3 = yaw_rotation(j[1]) * yaw_rotation(j[0]) * pitch_rotation(i[0])
            R_N = R_D * R_3.transpose()
            if R_N.item(0, 0) == 1:
                q4 = 0
                q5 = 0
                q6 = np.arccos(R_N.item(1, 1))
                solutions_3 = [[q4, q5, q6], [q4, q5, -q6]]
            else:
                q4 = np.atan2(R_N.item(1, 0), -R_N.item(2, 0))
                q5 = np.arccos(R_N.item(0, 0))
                q6 = np.atan2(R_N.item(0, 1), R_N.item(0, 2))
                solutions_3.append([q4, -q5, q6])
                solutions_3.append([q4, q5, q6])

    solutions = []
    for i in solutions_1:
        for j in solutions_2:
            for k in solutions_3:
                solutions.append(i + j + k)
    
    return solutions
