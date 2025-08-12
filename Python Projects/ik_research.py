import copy

import numpy as np
import json
import matplotlib.pyplot as plt
from vector import Vector3

cube_size = 300
def normalize(vec: np.array):
    n = 0
    for p in vec:
        n += np.pow(p, 2)
    return np.sqrt(n)


x_pos = 300
y_pos = 0
z_pos = 0
x_rot = 45
y_rot = 0
z_rot = 45
goal = Vector3(x_pos, y_pos, z_pos)

d: dict
with open('data/ik_config.json') as f:
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
# nm5.rotate_axis(y_rot, 'y', mode='deg')
# nm5.rotate_axis(x_rot, 'x', mode='deg')
print(nm5)
print(np.round(nm5.vec2matrix, 4))
new_goal = copy.copy(goal)
new_goal = new_goal - nm5
print(new_goal)

lj1 = abs(m2)
lj2 = np.sqrt(np.pow(m5.x + m4.x + m3.x, 2) + np.pow(m5.y + m4.y + m3.y, 2))

q2 = -np.arccos(
    ((np.pow(new_goal.x, 2) + np.pow(new_goal.y, 2) + np.pow(new_goal.z, 2)) - np.pow(lj1, 2) - np.pow(lj2, 2))
    / (2 * lj1 * lj2))
q1 = np.atan2(new_goal.y, new_goal.x) - np.atan2(lj2 * np.sin(q2), lj1 + lj2 * np.cos(q2))

o1 = np.atan2(new_goal.z, new_goal.x)

j1 = Vector3([lj1, 0, 0])
j1.rotate(0, o1, -q1)
j2 = Vector3([lj2, 0, 0])
j2.rotate(0, o1, -(q1 + q2))
j2 = j1 + j2
j3 = Vector3([x_pos, y_pos, z_pos])

fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.plot([0, goal.x], [0, goal.y], [0, goal.z], c='#00ff00', linestyle='dashed')
ax.plot([0,new_goal.x], [0, new_goal.y], [0, new_goal.z], c='#ff00ff', linestyle='dashed')

ax.plot([0, j1.x, j2.x], [0, j1.y, j2.y], [0, j1.z, j2.z], c='#fcba03')
ax.plot([j2.x, j3.x], [j2.y, j3.y], [j2.z, j3.z])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_xlim(-cube_size, cube_size)
ax.set_ylim(-cube_size, cube_size)
ax.set_zlim(-cube_size, cube_size)
plt.show()

