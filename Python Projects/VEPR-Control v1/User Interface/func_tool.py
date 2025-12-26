data = ''
speed = ''
for i in range(6):
    data += f'mot_speed{i}: int, '
for i in range(6):
    data += f'mot_inverse_direction{i}: bool, '
for i in range(6):
    data += f'mot_accel{i}: int, '
for i in range(6):
    data += f'mot_reduc{i}: float, '
for i in range(6):
    data += f'mot_mult{i}: float, '
for i in range(6):
    data += f'mot_home_speed{i}: int, '
for i in range(6):
    data += f'mot_home_inverse{i}: bool, '
for i in range(6):
    data += f'mot_home_accel{i}: int, '
for i in range(6):
    data += f'mot_home_offset{i}: int, '
for i in range(6):
    data += f'mot_home_mult{i}: float, '
for i in range(6):
    data += f'microsteps{i}: int, '
for i in range(6):
    data += f'rms_current{i}: int, '
for i in range(6):
    data += f'hold_current_mult{i}: float, '
print(data)