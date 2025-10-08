import json
from vector import Vector3, yaw_rotation, pitch_rotation, roll_rotation
import vector
import copy
import numpy as np


def ik_calculate(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot, l1, l2, l3, l4, deg=False):
    X_D = Vector3(x_pos, y_pos, z_pos)
    nm5 = copy.copy(l4)
    R_D = vector.euler_rotation(x_rot, y_rot, z_rot)

    nm5.rotate(x_rot, y_rot, z_rot, mode='deg')
    X_N = copy.copy(X_D)
    X_N = X_N - nm5
    xd, yd, zd = X_N.vec2matrix.tolist()[0]

    nX_N = X_N - l1
    nxd, nyd, nzd = nX_N.vec2matrix.tolist()[0]

    q1 = np.arctan2(zd, xd)
    c3 = (np.pow(abs(nX_N), 2) - np.pow(abs(l2), 2) - np.pow(abs(l3), 2))/(2 * abs(l2) * abs(l3))
    print(c3)
    if c3 > 1:
        print('fuckyou')
        return None
    elif c3 == 1:
        q2 = np.atan2(yd - l1.y, np.hypot(xd - l1.x, zd))
        q3 = 0
    elif c3 == -1 and abs(nX_N) != 0:
        q2 = np.atan2(nyd, np.hypot(nxd, nzd))
        q3 = np.pi
    elif c3 == -1 and (nX_N) == 0:
        q2 = 0
        q3 = np.pi
    else:
        q3 = np.arccos(c3)
        q2 = np.atan2(nyd, np.hypot(nxd, nzd)) - np.atan2(abs(l3) * np.sin(q3), abs(l2) + abs(l3) * np.cos(q3))

    R_3 = yaw_rotation(q3) * yaw_rotation(q2) * pitch_rotation(q3)
    R_N = R_D * R_3.transpose()
    if R_N.item(0, 0) == 1:
        q4 = 0
        q5 = 0
        q6 = np.arccos(R_N.item(1, 1))
    else:
        q4 = np.atan2(R_N.item(1, 0), -np.float64(R_N.item(2, 0)))
        q5 = np.arccos(R_N.item(0, 0))
        q6 = np.atan2(R_N.item(0, 1), -np.float64(R_N.item(0, 2)))

    return q1, q2, q3, q4, q5, q6

with open('data/ik_config.json') as f:
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
_l3 = m2 + m4
_l4 = m5

print(_l1, _l2, _l3, _l4)

pot = _l1 + _l2 + _l3 + _l4
print(pot)
ik = ik_calculate(pot.x - 1, pot.y, 0, 0, 0, 0, _l1, _l2, _l3, _l4)
o3 = np.atan2(_l3.y, _l3.x)
print(o3)
for q in ik:
    print(np.rad2deg(q))


