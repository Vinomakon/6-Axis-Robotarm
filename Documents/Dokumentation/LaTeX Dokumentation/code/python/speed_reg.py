import numpy as np
def mots(rotation, max_speeds, reduction):
    rot = np.asarray(rotation, dtype=float)
    vmax = np.asarray(max_speeds, dtype=float)
    red = np.asarray(reduction, dtype=float)

    speeds = np.zeros(6, dtype=float) 

    eff = np.abs(rot) * red
    if not np.any(eff > 0.0):
        return speeds.tolist()
    
    m = int(np.argmax(eff))

    satisfied = False
    while not satisfied:
        satisfied = True

        base = vmax[m] / eff[m]

        for i in range(6):
            if eff[i] == 0.0:
                speeds[i] = 0.0
                continue
            speed = base * eff[i]
            if speed > vmax[i]:
                m = i
                satisfied = False
                break
            speeds[i] = speed
    
    return speeds.tolist()

