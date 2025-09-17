import copy
import numpy as np
import json
import matplotlib.pyplot as plt
from vector import Vector3
import vector
from ik_link import Link
import ik_link

cube_size = 300

x_pos = 300
y_pos = 200
z_pos = 0
x_rot = 0
y_rot = 0
z_rot = 0
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

nm5.rotate(x_rot, y_rot, z_rot)
new_goal = copy.copy(goal)
new_goal = new_goal - nm5

lj1 = abs(m2)
lj2 = np.sqrt(np.pow(m5.x + m4.x + m3.x, 2) + np.pow(m5.y + m4.y + m3.y, 2))
lj3 = abs(m5)

q2 = -np.arccos(
    ((np.pow(new_goal.x, 2) + np.pow(new_goal.y, 2) + np.pow(new_goal.z, 2)) - np.pow(lj1, 2) - np.pow(lj2, 2))
    / (2 * lj1 * lj2))
q1 = np.atan2(new_goal.y, np.sqrt((np.pow(new_goal.x, 2) + (np.pow(new_goal.z, 2))))) - np.atan2(lj2 * np.sin(q2), lj1 + lj2 * np.cos(q2))

o1 = np.atan2(new_goal.z, new_goal.x)

print(np.rad2deg(o1), np.rad2deg(q1), np.rad2deg(q2))

l1 = Link(Vector3(0, 50, 0))
l1.offset = np.matrix([0, -50, 0])
l1.set_rotation(0, o1, 0)
l2 = Link(Vector3(lj1, 0, 0))
l2.assign_last_link(l1)
l2.set_rotation(0, 0, -q1)
l3 = Link(Vector3(lj2, 0, 0))
l3.assign_last_link(l2)
l3.set_rotation(0, 0, -q2)

j = l3.set_relative_vector(goal)
j1 = np.atan2(j.y, j.x)
j2 = np.atan2(j.y, j.z)

print(np.rad2deg(j1), np.rad2deg(j2))
print(j)
print(abs(j))

l4 = Link(Vector3(lj3, 0, 0))
l4.assign_last_link(l3)
l4.system = ik_link.def_matrix()
l4.set_rotation(0, 0, -j1)
print(l4)
print(l4.transform)
print(goal)


fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.plot([0, goal.x], [0, goal.y], [0, goal.z], c='#00ff00')
ax.plot([0,new_goal.x], [0, new_goal.y], [0, new_goal.z], c='#ff00ff')

ax.plot([0, l1.x, l2.x, l3.x], [-50, l1.y, l2.y, l3.y], [0, l1.z, l2.z, l3.z], c='#fcba03')
ax.plot([l3.x, l4.x], [l3.y, l4.y], [l3.z, l4.z], c='#434343')
# ax.scatter([l3.x, l4.x], [l3.y, l4.y], [l3.z, l4.z], marker='1')
# ax.plot([0, j1.x, j2.x], [0, j1.y, j2.y], [0, j1.z, j2.z], c='#fcba03')
# ax.plot([j2.x, j3.x], [j2.y, j3.y], [j2.z, j3.z], c='#434343')
# ax.scatter([j2.x, g3.x], [j2.y, g3.y], [j2.z, g3.z])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_xlim(-cube_size, cube_size)
ax.set_ylim(-cube_size, cube_size)
ax.set_zlim(-cube_size, cube_size)
plt.show()