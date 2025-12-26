import json
import random

from vector import Vector3, yaw_rotation, pitch_rotation, roll_rotation
import copy
import numpy as np

with open('../data/ik_config.json') as f:
    d = json.load(f)
    f.close()

m0 = Vector3(d['motor0']['x'], d['motor0']['y'], d['motor0']['z'])
m1 = Vector3(d['motor1']['x'], d['motor1']['y'], d['motor1']['z'])
m2 = Vector3(d['motor2']['x'], d['motor2']['y'], d['motor2']['z'])
m3 = Vector3(d['motor3']['x'], d['motor3']['y'], d['motor3']['z'])
m4 = Vector3(d['motor4']['x'], d['motor4']['y'], d['motor4']['z'])
m5 = Vector3(d['motor5']['x'], d['motor5']['y'], d['motor5']['z'])

l1 = m0 + m1
l2 = m2
l3 = m3 + m4
l4 = m5

nm5 = Vector3(d['motor5']['x'], d['motor5']['y'], d['motor5']['z'])


def ik_calculate(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot):
    global nm5
    x_d = Vector3(x_pos, y_pos, z_pos)
    x_rot = np.deg2rad(x_rot)
    y_rot = np.deg2rad(y_rot)
    z_rot = np.deg2rad(z_rot)
    r_d = roll_rotation(x_rot) * pitch_rotation(y_rot) * yaw_rotation(z_rot)
    # print("NEW OPERATION")
    nm5 = Vector3(nm5.vec2matrix * roll_rotation(x_rot) * pitch_rotation(y_rot) * yaw_rotation(-z_rot))
    # print(nm5, "nm5")
    x_n = copy.copy(x_d)
    x_n = x_n - nm5
    # print(x_n, "X_N")
    xd, yd, zd = x_n.vec2matrix.tolist()[0]

    n_x_n = x_n - l1
    # print(n_x_n, l1)
    nxd, nyd, nzd = n_x_n.vec2matrix.tolist()[0]

    q1 = np.arctan2(zd, xd)
    c3 = (np.pow(abs(n_x_n), 2) - np.pow(abs(l2), 2) - np.pow(abs(l3), 2))/(2 * abs(l2) * abs(l3))
    if c3 > 1:
        # print("Calculation not possible")
        return None
    elif c3 == 1:
        q2 = np.atan2(nyd - l1.y, np.hypot(xd - l1.x, zd))
        q3 = 0
    elif c3 == -1 and abs(n_x_n) != 0:
        q2 = np.atan2(nyd, np.hypot(nxd, nzd))
        q3 = np.pi
    elif c3 == -1 and n_x_n == 0:
        q2 = 0
        q3 = np.pi
    else:
        q3 = -np.arccos(c3)
        q2 = np.atan2(nyd, np.hypot(nxd, nzd)) - np.atan2(abs(l3) * np.sin(q3), abs(l2) + abs(l3) * np.cos(q3))

    o3 = np.atan2(l3.y, l3.x)

    r_3 = yaw_rotation(q3 - o3) * yaw_rotation(q2) * pitch_rotation(q1)
    r_n = r_d * r_3.transpose()
    if r_n.item(0, 0) == 1:
        q4 = 0
        q5 = 0
        q6 = np.arccos(r_n.item(1, 1))
    else:
        q6 = np.atan2(r_n.item(1, 0), -np.float64(r_n.item(2, 0)))
        q5 = -np.arccos(r_n.item(0, 0))
        q4 = np.atan2(r_n.item(0, 1), np.float64(r_n.item(0, 2)))

    return [q1, q2, q3, q4, q5, q6]

def fk_calculate(mot1, mot2, mot3, mot4, mot5, mot6):
    return [random.randint(0, 10) for i in range(6)]


pot = l1 + Vector3(0, l2.x, 0) + l3 + l4
default_configuration = np.round(np.asarray([pot.x, pot.y, pot.z, 0, 0, 0]), 4)

# print(pot)
# ik = ik_calculate(pot.x-40, pot.y, 0, 0, 0, 90)
# p3 = np.atan2(l3.y, l3.x)
# ik[1] -= np.pi / 2
# ik[2] -= -np.pi / 2 + p3
