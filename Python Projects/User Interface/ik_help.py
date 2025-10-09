import json
from vector import Vector3, yaw_rotation, pitch_rotation, roll_rotation
import vector
import copy
import numpy as np


def ik_calculate(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot):
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
    X_D = Vector3(x_pos, y_pos, z_pos)
    nm5 = copy.copy(l4)
    x_rot = np.deg2rad(x_rot)
    y_rot = np.deg2rad(y_rot)
    z_rot = np.deg2rad(z_rot)
    R_D = vector.euler_rotation(x_rot, y_rot, z_rot)
    print(R_D)

    nm5.rotate(-x_rot, -y_rot, -z_rot, mode='rad')
    X_N = copy.copy(X_D)
    X_N = X_N - nm5
    xd, yd, zd = X_N.vec2matrix.tolist()[0]

    nX_N = X_N - l1
    nxd, nyd, nzd = nX_N.vec2matrix.tolist()[0]

    q1 = np.arctan2(zd, xd)
    c3 = (np.pow(abs(nX_N), 2) - np.pow(abs(l2), 2) - np.pow(abs(l3), 2))/(2 * abs(l2) * abs(l3))
    if c3 > 1:
        print("Calculation not possible")
        return None
    elif c3 == 1:
        q2 = np.atan2(nyd - l1.y, np.hypot(xd - l1.x, zd))
        q3 = 0
    elif c3 == -1 and abs(nX_N) != 0:
        q2 = np.atan2(nyd, np.hypot(nxd, nzd))
        q3 = np.pi
    elif c3 == -1 and (nX_N) == 0:
        q2 = 0
        q3 = np.pi
    else:
        print("Normal case")
        q3 = -np.arccos(c3)
        q2 = np.atan2(nyd, np.hypot(nxd, nzd)) - np.atan2(abs(l3) * np.sin(q3), abs(l2) + abs(l3) * np.cos(q3))

    o3 = np.atan2(l3.y, l3.x)

    R_3 = pitch_rotation(-q1) * yaw_rotation(q2) * yaw_rotation(q3 - o3)
    R_N = R_D * R_3.transpose()
    print(R_N)
    if R_N.item(0, 0) == 1:
        print("special")
        q4 = 0
        q5 = 0
        q6 = np.arccos(R_N.item(1, 1))
    else:
        q4 = np.atan2(R_N.item(1, 0), -np.float64(R_N.item(2, 0)))
        q5 = np.arccos(R_N.item(0, 0))
        q6 = np.atan2(R_N.item(0, 1), np.float64(R_N.item(0, 2)))

    return [q1, q2, q3, q4, q5, q6]

with open('../data/ik_config.json') as f:
    d = json.load(f)
    f.close()

m0 = Vector3(d['motor0']['x'], d['motor0']['y'], d['motor0']['z'])
m1 = Vector3(d['motor1']['x'], d['motor1']['y'], d['motor1']['z'])
m2 = Vector3(d['motor2']['x'], d['motor2']['y'], d['motor2']['z'])
m3 = Vector3(d['motor3']['x'], d['motor3']['y'], d['motor3']['z'])
m4 = Vector3(d['motor4']['x'], d['motor4']['y'], d['motor4']['z'])
m5 = Vector3(d['motor5']['x'], d['motor5']['y'], d['motor5']['z'])

_l1 = m0 + m1
_l2 = m2
_l3 = m3 + m4
_l4 = m5

print(_l1, _l2, _l3, _l4)

pot = _l1 + Vector3(0, _l2.x, 0) + _l3 + _l4
print(pot)
print(abs(Vector3(0, _l2.x, 0) + _l3))
ik = ik_calculate(pot.x-40, pot.y, 0, 0, 0, 90, _l1, _l2, _l3, _l4)
o3 = np.atan2(_l3.y, _l3.x)
ik[1] -= np.pi / 2
ik[2] -= -np.pi / 2 + o3
for i in range(len(ik)):
    print(np.rad2deg(ik[i]), f"q{i + 1}")
    pass


