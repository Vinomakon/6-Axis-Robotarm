from vector import Vector3
import json
import numpy as np
import copy

def ik_calculate(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot, deg=False) -> tuple[float, float, float]:
    goal = Vector3(x_pos, y_pos, z_pos)

    d: dict
    with open('../data/ik_config.json') as f:
        d = json.load(f)
        f.close()

    m0 = Vector3(d['motor0']['x'], d['motor0']['y'], d['motor0']['z'])
    m1 = Vector3(d['motor1']['x'], d['motor1']['y'], d['motor1']['z'])
    m2 = Vector3(d['motor2']['x'], d['motor2']['y'], d['motor2']['z'])
    m3 = Vector3(d['motor3']['x'], d['motor3']['y'], d['motor3']['z'])
    m4 = Vector3(d['motor4']['x'], d['motor4']['y'], d['motor4']['z'])
    m5 = Vector3(d['motor5']['x'], d['motor5']['y'], d['motor5']['z'])

    nm5 = copy.copy(m5)

    nm5.rotate(x_rot, y_rot, z_rot, mode='deg')
    new_goal = copy.copy(goal)
    new_goal = new_goal - nm5

    lj1 = abs(m2)
    lj2 = np.sqrt(np.pow(m5.x + m4.x + m3.x, 2) + np.pow(m5.y + m4.y + m3.y, 2))

    q2 = -np.arccos(
        ((np.pow(new_goal.x, 2) + np.pow(new_goal.y, 2) + np.pow(new_goal.z, 2)) - np.pow(lj1, 2) - np.pow(lj2, 2))
        / (2 * lj1 * lj2))
    q1 = np.atan2(new_goal.y, new_goal.x) - np.atan2(lj2 * np.sin(q2), lj1 + lj2 * np.cos(q2))

    o1 = np.atan2(new_goal.z, new_goal.x)
    if deg:
        return np.rad2deg(o1), np.rad2deg(q1), np.rad2deg(q2)
    else:
        return o1, q1, q2
