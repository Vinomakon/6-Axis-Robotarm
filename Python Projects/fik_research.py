import copy
import numpy as np
import json
import matplotlib.pyplot as plt
from vector import Vector3
import vector
import rotation as rt
from ik_link import Link
import ik_link

cube_size = 300

x_pos = 300
y_pos = 200
z_pos = 0
x_rot = 0
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

nm5.rotate(x_rot, y_rot, z_rot, mode='deg', order='xyz')
new_goal = copy.copy(goal)
new_goal = new_goal - nm5

lj1 = abs(m2)
lj2 = np.sqrt(np.pow(m4.x + m3.x, 2) + np.pow(m4.y + m3.y, 2))
lj3 = abs(m5)

q2 = -np.arccos(
    ((np.pow(new_goal.x, 2) + np.pow(new_goal.y, 2) + np.pow(new_goal.z, 2)) - np.pow(lj1, 2) - np.pow(lj2, 2))
    / (2 * lj1 * lj2))
q1 = np.atan2(new_goal.y, np.sqrt((np.pow(new_goal.x, 2) + (np.pow(new_goal.z, 2))))) - np.atan2(lj2 * np.sin(q2), lj1 + lj2 * np.cos(q2))

o1 = np.atan2(new_goal.z, new_goal.x)

print(np.rad2deg(o1), np.rad2deg(q1), np.rad2deg(q2))
print(lj2)

l1 = Link(Vector3(0, 50, 0))
l1.offset = np.matrix([0, -50, 0])
l1.set_rotation(0, o1, 0)
l2 = Link(Vector3(lj1, 0, 0))
l2.assign_last_link(l1)
l2.set_rotation(0, 0, -q1)
l3 = Link(Vector3(lj2, 0, 0))
l3.assign_last_link(l2)
l3.set_rotation(0, 0, -q2)

m = l3.set_relative_vector(goal)
j = copy.copy(m)
j1 = np.atan2(j.z, j.x)
j.rotate(0, -j1, 0)
j2 = np.atan2(j.y, j.x)
# j1 = np.atan2(j.y, np.sqrt(abs(np.pow(j.x, 2) - np.pow(j.z, 2))))
# j2 = np.atan2(j.y, np.sqrt(abs(np.pow(j.z, 2) - np.pow(j.x, 2))))

l4 = Link(Vector3(lj3, 0, 0))
l4.assign_last_link(l3)
l4.update_chain()


fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.plot([0, goal.x], [0, goal.y], [0, goal.z], c='#00ff00')
ax.plot([0,new_goal.x], [0, new_goal.y], [0, new_goal.z], c='#ff00ff')

ax.plot([0, l1.x, l2.x, l3.x], [-50, l1.y, l2.y, l3.y], [0, l1.z, l2.z, l3.z], c='#fcba03')
ax.plot([l3.x, l4.x], [l3.y, l4.y], [l3.z, l4.z], c='#434343')
ax.plot([goal.x, new_goal.x], [goal.y, new_goal.y], [goal.z, new_goal.z], c="#0000ff")

i1 = Link(Vector3(0, lj3, 0))
i1.set_rotation(0, j1, np.pi/2 - j2)

rd1 = rt.Rotation(x_rot, y_rot, z_rot)
rn1 = rd1.rot_matrix * l4.system.transpose()
q5 = np.arccos(rn1.item(0, 0))
if q5 != 0:
    q4 = np.atan2(rn1.item(1, 0), -rn1.item(2, 0))
    q6 = np.atan2(rn1.item(0, 1), rn1.item(0, 2))
else:
    q4, q6 = 0, 0
print(q4, q5, q6)
print(np.round(l4.system * rt.roll_rotation(q4) * rt.pitch_rotation(q5) * rt.roll_rotation(q6), 10))
print(rd1.rot_matrix)

m = Vector3(lj3, 0, 0) * l4.system * rt.roll_rotation(q4) * rt.pitch_rotation(q5) * rt.roll_rotation(q6)
o = Vector3(l3.end_effector)
m = m + o
print(m)

# ax.plot([0, 0], [0, lj3], [0, 0], c='#fcba03')
# ax.plot([o.x, m.x], [o.y, m.y], [o.z, m.z], c='#00ff00')
# ax.plot([0, i1.x], [0, i1.y], [0, i1.z])
# ax.plot([0, j.x], [0, j.y], [0, j.z], c='#ff00ff')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_xlim(-cube_size, cube_size)
ax.set_ylim(-cube_size, cube_size)
ax.set_zlim(-cube_size, cube_size)
plt.show()