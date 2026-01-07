import numpy
import numpy as np
import sympy
import json
import kinematics
from numpy import cos as c, sin as s, pow, sqrt

with open('../data/user_config.json', mode="r") as f:
    config = json.load(f)
    f.close()
reductions = []
for m in range(6):
    reductions.append(config[f"motor{m}"]["reduction"])
reduction = np.asarray(reductions)
print(reductions)

lst = np.array([range(6), [100, 500, 400, 600, 200, 300]])

a = np.array(range(6))
b = np.array(range(6))

def roll_rotation(idx): # X-Rotation
    return sympy.Matrix([[1, 0, 0], [0, f"c{idx}", f"-s{idx}"], [0, f"s{idx}", f"c{idx}"]])
    # return np.matrix([[1, 0, 0], [0, c(roll), -s(roll)], [0, s(roll), c(roll)]])

def pitch_rotation(idx): # Y-Rotation
    return sympy.Matrix([[f"c{idx}", 0, f"s{idx}"], [0, 1, 0], [f"-s{idx}", 0, f"c{idx}"]])
    # return np.matrix([[c(pitch), 0, s(pitch)], [0, 1, 0], [-s(pitch), 0, c(pitch)]])

def yaw_rotation(idx): # Z-Rotation
    return sympy.Matrix([[f"c{idx}", f"-s{idx}", 0], [f"s{idx}", f"c{idx}", 0], [0, 0, 1]])
    # return np.matrix([[c(yaw), -s(yaw), 0], [s(yaw), c(yaw), 0], [0, 0, 1]])

def cpp_implement():
    r_d = roll_rotation("x") * pitch_rotation("y") * yaw_rotation("z")
    r_d_t = r_d.transpose()
    print("R_D Matrix:",r_d)
    r_3 = yaw_rotation("3") * yaw_rotation("2") * pitch_rotation("2")
    print("R_3 Matrix:",r_d)

    nm5 = sympy.Matrix([["l"], [0], [0]])

    print("End-Effector:", r_d * nm5)
    r_n = r_3 * r_d_t
    print("R_N Matrix:",r_n)
    print("Element [0, 0]:", r_n[0, 0])
    print("Element [1, 0]:", r_n[1, 0])
    print("Element [2, 0]:", r_n[2, 0])
    print("Element [0, 1]:", r_n[0, 1])
    print("Element [0, 2]:", r_n[0, 2])

reductions = np.asarray([4.5, 20.0, 40.0, 2.5, 4.0, 20.0], dtype="float")
steps_p_revolution = 200

def interpolate(start_point, end_point):
    # print("Start Point:", start_point)
    # print("End   Point:", end_point)
    start_ik = np.asarray(kinematics.specific_ik_calculate(*start_point))
    end_ik = np.asarray(kinematics.specific_ik_calculate(*end_point))
    rotations = end_ik - start_ik
    steps_to_take = np.round(rotations * steps_p_revolution * reductions)
    print(steps_to_take)
    return

def interpolation(start_point, end_point, interpolations_steps):
    dif = end_point - start_point
    dif[3:6] = (dif[3:6]+180) % 360 - 180

    step = dif / interpolations_steps
    print(dif)
    print(step)
    steps = []
    for i in range(interpolations_steps):
        steps.append(interpolate((start_point + step*i), (start_point + step*(i+1))))


point_a = np.array([276.8, 360, 0, 0, 0, 0])
point_b = np.array([276.8, 200, 0, 0, 0, 0])

# interpolation(point_a, point_b, 100000)

def cartesian_linear_path(p_start, p_end, n_pts):
    t = np.linspace(0, 1, n_pts)
    dif = p_end - p_start
    dif[3:6] = (dif[3:6] + 180) % 360 - 180
    return p_start[None, :] + t[:, None] * dif[None, :]

def joint_path_from_cartesian(path):
    q_path = []
    for p in path:
        q = kinematics.specific_ik_calculate(*p)
        q_path.append(q)
    return np.asarray(q_path)

cartesian_path = cartesian_linear_path(point_a, point_b, 500)
joint_path = joint_path_from_cartesian(cartesian_path)
