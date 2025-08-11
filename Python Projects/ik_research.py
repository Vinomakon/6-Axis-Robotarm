import numpy as np
import json
import matplotlib.pyplot as plt


cube_size = 300
def normalize(vec: np.array):
    n = 0
    for p in vec:
        n += np.pow(p, 2)
    return np.sqrt(n)


x_pos = 250
y_pos = 50
z_pos = 0
x_rot = 0
y_rot = 0
z_rot = 0


d: dict
with open('data/ik_config.json') as f:
    d = json.load(f)
    f.close()

m0 = d['motor0']
m1 = d['motor1']
m2 = d['motor2']
m3 = d['motor3']
m4 = d['motor4']
m5 = d['motor5']

lm0 = np.sqrt(np.pow(m0['x'], 2) + np.pow(m0['y'], 2) + np.pow(m0['z'], 2))
lm1 = np.sqrt(np.pow(m1['x'], 2) + np.pow(m1['y'], 2) + np.pow(m1['z'], 2))
lm2 = np.sqrt(np.pow(m2['x'], 2) + np.pow(m2['y'], 2) + np.pow(m2['z'], 2))
lm3 = np.sqrt(np.pow(m3['x'], 2) + np.pow(m3['y'], 2) + np.pow(m3['z'], 2))
lm4 = np.sqrt(np.pow(m4['x'], 2) + np.pow(m4['y'], 2) + np.pow(m4['z'], 2))

m5x = m5['x']
m5y = m5['y']
m5z = m5['z']

m5norm = np.sqrt(np.pow(m5x, 2) + np.pow(m5y, 2) + np.pow(m5z, 2))

# First operation
m5x = round(m5norm * np.cos(np.deg2rad(-x_rot)), 4)
m5z = round(m5norm * np.sin(np.deg2rad(-x_rot)), 4)

# Second operation
m5y = round(m5z * np.cos(np.deg2rad(-z_rot)), 4)
m5z = round(m5z * np.sin(np.deg2rad(-z_rot)), 4)

print(m5x, m5y, m5z)

m4x = m5x + m4['x']
m4y = m5y + m4['y']

x_g = x_pos - m5x
y_g = y_pos - m5y
z_g = z_pos - m5z
print(x_g, y_g, z_g)

lj1 = lm2
lj2 = np.sqrt(np.pow(m5x + m4['x'] + m3['x'], 2) + np.pow(m5y + m4['y'] + m3['y'], 2))


# print((np.pow(x_pos, 2) + np.pow(y_pos, 2)))
# print(((np.pow(x_pos, 2) + np.pow(y_pos, 2)) - np.pow(lj1, 2) - np.pow(lj2, 2)) / (2 * lj1 * lj2))
q2 = np.arccos(
    ((np.pow(x_pos, 2) + np.pow(y_pos, 2)) - np.pow(lj1, 2) - np.pow(lj2, 2))
    / (2 * lj1 * lj2))

q1 = np.atan2(y_g, x_g) - np.atan2(lj2 * np.sin(q2), lj1 + lj2 * np.cos(q2))
print(np.rad2deg(q1), np.rad2deg(q2))
print(lj1, lj2)

fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.plot([0, x_pos], [0, y_pos], [0, z_pos], c='#ff00ff')

j1 = np.array([lj1 * np.cos(q1), lj1 * np.sin(q1), 0])
j2 = np.array([lj2 * np.cos(-(q1 + q2)) + j1[0], lj2 * np.sin(-(q1 + q2)) + j1[0], 0])
j3 = np.array([x_g, y_g, z_g])
print(j1, j2)
# ax.plot([0, m5x], [0, m5y], [0, m5z])
# ax.scatter([0], [0], [0], marker='*', c='#ff0000')
# ax.plot([0, 0, 0, 0, 0], [-m5norm, m5norm, m5norm, -m5norm, -m5norm], [-m5norm, -m5norm, m5norm, m5norm, -m5norm], linestyle='dashed')

ax.plot([0, j1[0], j2[0]], [0, j1[1], j2[1]], [0, j1[2], j2[2]], c='#fcba03')
# ax.plot([j2[0], j3[0]], [j2[1], j3[0]], [j2[2], j3[0]])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_xlim(-cube_size, cube_size)
ax.set_ylim(-cube_size, cube_size)
ax.set_zlim(-cube_size, cube_size)
plt.show()

