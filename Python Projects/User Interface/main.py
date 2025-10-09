import asyncio
import gradio as gr
import websockets
import constants as c
import json
from formatting import n_th
from ik_help import ik_calculate
import numpy as np
from vector import Vector3

DEFAULT_STEPS = 1000

async def con(data: list) -> None:
    async with websockets.connect("ws://192.168.4.1/ws") as websocket:
        for i in data:
            # print(f"sending {i}")
            await websocket.send(i)
    # print("finished")

async def con_get(data: list) -> list:
    end_data = []
    async with websockets.connect("ws://192.168.4.1/ws") as websocket:
        for i in data:
            # print(f"sending {i}")
            await websocket.send(i)
            end_data.append(str(await websocket.recv()))
    # print("finished")
    return end_data


def load_json_config() -> dict:
    with open('../data/user_config.json') as f:
        d = json.load(f)
        f.close()
        return d

def setup_config():
    user_config_ = load_json_config()
    global preset_list
    mot_speed_ = []
    mot_inverse_ = []
    mot_accel_ = []
    mot_reduc_ = []
    mot_home_speed_ = []
    mot_home_inverse_ = []
    mot_home_accel_ = []
    mot_shome_offset_ = []
    mot_home_mult_ = []
    mot_home_offset_ = []
    microsteps_ = []
    irun_ = []
    ihold_ = []
    mot_mult_ = []
    for m in range(6):
        mot_speed_.append(gr.Number(value=user_config_[f"motor{m}"]["speed"], step=1, minimum=0, label="Speed", interactive=True))
        mot_inverse_.append(gr.Checkbox(label="Inverse Direction",
                                                            value=user_config[f"motor{m}"]["inverse_direction"]))
        mot_accel_.append(gr.Number(value=user_config_[f"motor{m}"]["acceleration"], step=1, minimum=0,
                                       label="Motor Acceleration"))
        mot_reduc_.append(gr.Number(value=user_config_[f"motor{m}"]["reduction"], label="Reduction"))

        mot_home_speed_.append(gr.Number(value=user_config[f"motor{m}"]["home_speed"], step=1, minimum=0, label="Homing Speed"))
        mot_home_inverse_.append(gr.Checkbox(label="Inverse Homing Direction", value=user_config[f"motor{m}"]["homing_inverse_direction"]))
        mot_home_accel_.append(gr.Number(value=user_config[f"motor{m}"]["home_acceleration"], step=1, minimum=0, label="Homing Acceleration"))
        mot_shome_offset_.append(gr.Number(value=user_config[f"motor{m}"]["shome_offset"], label="Second Homing Offset"))
        mot_home_mult_.append(gr.Number(value=user_config[f"motor{m}"]["home_mult"], minimum=0, maximum=1, label="Second Homing Speed Multiplier"))
        mot_home_offset_.append(gr.Number(value=user_config[f"motor{m}"]["home_offset"], label="Homing Offset"))
        print(user_config[f"motor{m}"]["home_offset"])
        microsteps_.append(gr.Number(value=user_config[f"motor{m}"]["microsteps"], step=1, minimum=0, label="Microsteps"))
        irun_.append(gr.Number(value=user_config[f"motor{m}"]["irun"], step=1, minimum=0, maximum=31, label="IRUN"))
        ihold_.append(gr.Number(value=user_config[f"motor{m}"]["ihold"], step=1, minimum=0, maximum=31, label="IHOLD"))

        mot_mult_.append(gr.Number(value=user_config[f'motor{m}']['speed_mult'], label=f"Motor Speed Multiplier", minimum=0, maximum=1))

    mot_global_speed_ = gr.Number(value=user_config["general"]["global_mot_speed"], step=1, minimum=1, label="Global Motor Speed")
    mot_global_accel_ = gr.Number(value=user_config["general"]["global_mot_accel"], step=1, minimum=1, label="Global Motor Acceleration")
    mot_steps_ = gr.Number(label='Number of Steps per full revolution',
                                  value=user_config["general"]["steps_p_revolution"], step=1, minimum=0)
    preset_list = user_config_['preset_positions']
    deg_presets_ = gr.Dataset(label='Motor Position Presets', components=[mot_deg[mot] for mot in range(6)],
                             headers=[f'Motor {num + 1}' for num in range(6)], samples=preset_list)

    return [mot_global_speed_, mot_global_accel_, *mot_speed_, *mot_mult, *mot_inverse_, *mot_accel_, *mot_reduc_,
            *mot_home_speed_, *mot_home_inverse_, *mot_home_accel_, *mot_shome_offset_, *mot_home_mult_,  *mot_home_offset_,
            *microsteps_, *irun_, *ihold_, mot_steps_,
            deg_presets_]

def config_save(mot_global_speed_: int, mot_global_accel_: int,
                mot_speed0: int, mot_speed1: int, mot_speed2: int, mot_speed3: int, mot_speed4: int, mot_speed5: int,
                mot_mult0: float, mot_mult1: float, mot_mult2: float, mot_mult3: float, mot_mult4: float, mot_mult5: float,
                mot_inverse0: bool, mot_inverse1: bool, mot_inverse2: bool, mot_inverse3: bool, mot_inverse4: bool, mot_inverse5: bool,
                mot_accel0: int, mot_accel1: int, mot_accel2: int, mot_accel3: int, mot_accel4: int, mot_accel5: int,
                mot_reduc0: float, mot_reduc1: float, mot_reduc2: float, mot_reduc3: float, mot_reduc4: float, mot_reduc5: float,
                mot_home_speed0: int, mot_home_speed1: int, mot_home_speed2: int, mot_home_speed3: int, mot_home_speed4: int, mot_home_speed5: int,
                mot_home_inverse0: bool, mot_home_inverse1: bool, mot_home_inverse2: bool, mot_home_inverse3: bool, mot_home_inverse4: bool, mot_home_inverse5: bool,
                mot_home_accel0: int, mot_home_accel1: int, mot_home_accel2: int, mot_home_accel3: int, mot_home_accel4: int, mot_home_accel5: int,
                mot_shome_offset0: int, mot_shome_offset1: int, mot_shome_offset2: int, mot_shome_offset3: int, mot_shome_offset4: int, mot_shome_offset5: int,
                mot_home_mult0: float, mot_home_mult1: float, mot_home_mult2: float, mot_home_mult3: float, mot_home_mult4: float, mot_home_mult5: float,
                mot_home_offset0: int, mot_home_offset1: int, mot_home_offset2: int, mot_home_offset3: int, mot_home_offset4: int, mot_home_offset5: int,
                microsteps0: int, microsteps1: int, microsteps2: int, microsteps3: int, microsteps4: int, microsteps5: int,
                irun0: int, irun1: int, irun2: int, irun3: int, irun4: int, irun5: int,
                ihold0: int, ihold1: int, ihold2: int, ihold3: int, ihold4: int, ihold5: int,
                mot_steps_: int):
    save = {}
    mot_speed_ = [mot_speed0, mot_speed1, mot_speed2, mot_speed3, mot_speed4, mot_speed5]
    mot_inverse_ = [mot_inverse0, mot_inverse1, mot_inverse2, mot_inverse3, mot_inverse4, mot_inverse5]
    mot_accel_ = [mot_accel0, mot_accel1, mot_accel2, mot_accel3, mot_accel4, mot_accel5]
    mot_reduc_ = [mot_reduc0, mot_reduc1, mot_reduc2, mot_reduc3, mot_reduc4, mot_reduc5]
    mot_mult_ = [mot_mult0, mot_mult1, mot_mult2, mot_mult3, mot_mult4, mot_mult5]
    mot_home_speed_ = [mot_home_speed0, mot_home_speed1, mot_home_speed2, mot_home_speed3, mot_home_speed4, mot_home_speed5]
    mot_home_inverse_ = [mot_home_inverse0, mot_home_inverse1, mot_home_inverse2, mot_home_inverse3, mot_home_inverse4, mot_home_inverse5]
    mot_home_accel_ = [mot_home_accel0, mot_home_accel1, mot_home_accel2, mot_home_accel3, mot_home_accel4, mot_home_accel5]
    mot_home_offset_ = [mot_home_offset0, mot_home_offset1, mot_home_offset2, mot_home_offset3, mot_home_offset4, mot_home_offset5]
    mot_home_mult_ = [mot_home_mult0, mot_home_mult1, mot_home_mult2, mot_home_mult3, mot_home_mult4, mot_home_mult5]
    mot_shome_offset_ = [mot_shome_offset0, mot_shome_offset1, mot_shome_offset2, mot_shome_offset3, mot_shome_offset4, mot_shome_offset5]
    microsteps_ = [microsteps0, microsteps1, microsteps2, microsteps3, microsteps4, microsteps5]
    irun_ = [irun0, irun1, irun2, irun3, irun4, irun5]
    ihold_ = [ihold0, ihold1, ihold2, ihold3, ihold4, ihold5]
    for j in range(6):
        save[f'motor{j}'] = {}
        save[f'motor{j}']['speed'] = mot_speed_[j]
        save[f'motor{j}']['inverse_direction'] = mot_inverse_[j]
        save[f'motor{j}']['acceleration'] = mot_accel_[j]
        save[f'motor{j}']['reduction'] = mot_reduc_[j]
        save[f'motor{j}']['speed_mult'] = mot_mult_[j]
        save[f'motor{j}']['home_speed'] = mot_home_speed_[j]
        save[f'motor{j}']['homing_inverse_direction'] = mot_home_inverse_[j]
        save[f'motor{j}']['home_acceleration'] = mot_home_accel_[j]
        save[f'motor{j}']['shome_offset'] = mot_shome_offset_[j]
        save[f'motor{j}']['home_offset'] = mot_home_offset_[j]

        save[f'motor{j}']['home_mult'] = mot_home_mult_[j]
        save[f'motor{j}']['microsteps'] = microsteps_[j]
        save[f'motor{j}']['irun'] = irun_[j]
        save[f'motor{j}']['ihold'] = ihold_[j]
    save['general'] = {}
    save['general']['global_mot_speed'] = mot_global_speed_
    save['general']['global_mot_accel'] = mot_global_accel_
    save['general']['steps_p_revolution'] = mot_steps_
    save['preset_positions'] = preset_list

    with open('../data/user_config.json', "w") as f:
        json.dump(save, f)
        f.close()
    print('Successfully saved config to \'user_config.json\'')

user_config = load_json_config()

def submit_homing_parameters(mot_home_speed0: int, mot_home_speed1: int, mot_home_speed2: int, mot_home_speed3: int, mot_home_speed4: int, mot_home_speed5: int,
                mot_home_inverse0: bool, mot_home_inverse1: bool, mot_home_inverse2: bool, mot_home_inverse3: bool, mot_home_inverse4: bool, mot_home_inverse5: bool,
                mot_home_accel0: int, mot_home_accel1: int, mot_home_accel2: int, mot_home_accel3: int, mot_home_accel4: int, mot_home_accel5: int,
                mot_shome_offset0: int, mot_shome_offset1: int, mot_shome_offset2: int, mot_shome_offset3: int, mot_shome_offset4: int, mot_shome_offset5: int,
                mot_home_mult0: float, mot_home_mult1: float, mot_home_mult2: float, mot_home_mult3: float, mot_home_mult4: float, mot_home_mult5: float,
                mot_home_offset0: int, mot_home_offset1: int, mot_home_offset2: int, mot_home_offset3: int, mot_home_offset4: int, mot_home_offset5: int,):
    mot_home_speed_ = [mot_home_speed0, mot_home_speed1, mot_home_speed2, mot_home_speed3, mot_home_speed4,
                       mot_home_speed5]
    mot_home_inverse_ = [mot_home_inverse0, mot_home_inverse1, mot_home_inverse2, mot_home_inverse3, mot_home_inverse4,
                         mot_home_inverse5]
    mot_home_accel_ = [mot_home_accel0, mot_home_accel1, mot_home_accel2, mot_home_accel3, mot_home_accel4,
                       mot_home_accel5]
    mot_shome_offset_ = [mot_shome_offset0, mot_shome_offset1, mot_shome_offset2, mot_shome_offset3, mot_shome_offset4,
                        mot_shome_offset5]
    mot_home_mult_ = [mot_home_mult0, mot_home_mult1, mot_home_mult2, mot_home_mult3, mot_home_mult4, mot_home_mult5]
    mot_home_offset_ = [mot_home_offset0, mot_home_offset1, mot_home_offset2, mot_home_offset3, mot_home_offset4,
                         mot_home_offset5]
    data = []
    for mot in range(6):
        data.append(f'{mot}{c.ihomsp}{mot_home_speed_[mot]}')
        data.append(f'{mot}{c.ihomin}{"1" if mot_home_inverse_[mot] else "0"}')
        data.append(f'{mot}{c.ihomac}{mot_home_accel_[mot]}')
        data.append(f'{mot}{c.ishmof}{mot_shome_offset_[mot]}')
        data.append(f'{mot}{c.ihommu}{mot_home_mult_[mot]}')
        data.append(f'{mot}{c.ihomof}{mot_home_offset_[mot]}')
    asyncio.run(con(data))

def init_tmc(microsteps0: int, microsteps1: int, microsteps2: int, microsteps3: int, microsteps4: int, microsteps5: int,
                irun0: int, irun1: int, irun2: int, irun3: int, irun4: int, irun5: int,
                ihold0: int, ihold1: int, ihold2: int, ihold3: int, ihold4: int, ihold5: int,
                mot_steps_: int):
    microsteps_ = [microsteps0, microsteps1, microsteps2, microsteps3, microsteps4, microsteps5]
    irun_ = [irun0, irun1, irun2, irun3, irun4, irun5]
    ihold_ = [ihold0, ihold1, ihold2, ihold3,
              ihold4, ihold5]

    data = []
    for mot in range(6):
        data.append(f'{mot}{c.imrstp}{microsteps_[mot]}')
        data.append(f'{mot}{c.i_irun}{irun_[mot]}')
        data.append(f'{mot}{c.i_hold}{ihold_[mot]}')
        data.append(f'{mot}{c.itmcen}')
    data.append(f'{c.igener}{c.idefst}{mot_steps_}')
    asyncio.run(con(data))

def set_motor_position(mot: int, pos: float):
    asyncio.run(con([f'{mot}{c.istpos}{pos}']))
    print(f'{mot}{c.istpos}{pos}')

def individual_movement(mot: int, deg_: float, speed_: int, inverse_: bool, mult_: float, accel_: int, reduc_: float):
    speed = f'{mot}{c.ispeed}{round(speed_ * mult_)}'
    accel = f'{mot}{c.iaccel}{round(accel_ * mult_)}'
    reduc = f"{mot}{c.ireduc}{reduc_}"
    move = f"{mot}{c.iangle}{deg_ * (-1 if inverse_ else 1)}"
    asyncio.run(con([speed, accel, reduc, move, c.istart]))

def manual_movement(mot_angle0: float, mot_angle1: float, mot_angle2: float, mot_angle3: float, mot_angle4: float, mot_angle5: float,
        mot_speed0: int, mot_speed1: int, mot_speed2: int, mot_speed3: int, mot_speed4: int, mot_speed5: int,
        mot_inverse0: bool, mot_inverse1: bool, mot_inverse2: bool, mot_inverse3: bool, mot_inverse4: bool, mot_inverse5: bool,
        mot_mult0: float, mot_mult1: float, mot_mult2: float, mot_mult3: float, mot_mult4: float, mot_mult5: float,
        mot_accel0: int, mot_accel1: int, mot_accel2: int, mot_accel3: int, mot_accel4: int, mot_accel5: int,
        mot_reduc0: float, mot_reduc1: float, mot_reduc2: float, mot_reduc3: float, mot_reduc4: float, mot_reduc5: float,
                   global_mot_speed_: int, global_mot_accel_: int):
    mot_reduc_ = [mot_reduc0, mot_reduc1, mot_reduc2, mot_reduc3, mot_reduc4, mot_reduc5]
    mot_angle_ = [mot_angle0, mot_angle1, mot_angle2, mot_angle3, mot_angle4, mot_angle5]
    mot_speed_ = [mot_speed0, mot_speed1, mot_speed2, mot_speed3, mot_speed4, mot_speed5]
    mot_inverse_ = [mot_inverse0, mot_inverse1, mot_inverse2, mot_inverse3,
                    mot_inverse4, mot_inverse5]
    mot_mult_ = [mot_mult0, mot_mult1, mot_mult2, mot_mult3, mot_mult4, mot_mult5]
    mot_accel_ = [mot_accel0, mot_accel1, mot_accel2, mot_accel3, mot_accel4, mot_accel5]
    class StepModule:
        def __init__(self, mot_: int, deg_: float, speed_: int, mult_: float, accel_: int, reduc_: float, cur_: float):
            self.motor = mot_
            self.deg = deg_
            self.a_deg = abs(deg_ - cur_)
            self.d_deg = abs(deg_)
            self.speed = 0
            self.accel = 0
            self.max_speed = round(speed_ * mult_)
            self.max_accel = round(accel_ * mult_)
            self.speed_overdrive = 0  # How much the calculated speed is over the current motor's maximum speed
            self.accel_overdrive = 0# How much the calculated acceleration is over the current motor's maximum acceleration
            self.reduc = reduc_

        def __lt__(self, other):
            return self.a_deg < other.a_deg

        def __repr__(self):
            return f"(Motor: {self.motor}, Degrees: {self.a_deg})"

        def __int__(self):
            return self.deg

        def set_values(self, deg_: float, speed: int, accel: int, reduc_: int) -> None:
            if self.a_deg == 0:
                return
            else:
                self.speed = round(speed * (self.a_deg / deg_) * self.reduc / reduc_)
                self.speed_overdrive = max(0, self.speed - self.max_speed)
                self.accel = round(accel * (self.a_deg / deg_) * self.reduc / reduc_)
                self.accel_overdrive = max(0, self.accel - self.max_accel)

        def get_overdrive(self):
            return self.max_speed, self.speed_overdrive, self.max_accel, self.accel_overdrive, self.a_deg

        def get_msg(self) -> list:
            if self.a_deg > 0:
                return [f"{self.motor}{c.ispeed}{self.speed}", f"{self.motor}{c.iaccel}{self.accel}", f"{self.motor}{c.ireduc}{self.reduc}", f"{self.motor}{c.iangle}{self.deg}"]
            else:
                return []

    cur_pos_ = asyncio.run(con_get([f'{mot}{c.icrpos}' for mot in range(6)]))
    #cur_pos_ = [0 for n in range(6)]



    values = []
    highest_reduc = 0
    for n in range(6):
        temp_ = StepModule(n, mot_angle_[n] * (-1 if mot_inverse_[n] else 1), mot_speed_[n], mot_mult_[n], mot_accel_[n], mot_reduc_[n], float(cur_pos_[n]))
        if temp_.a_deg > 0:
            values.append(temp_)
            if highest_reduc < temp_.reduc:
                highest_reduc = temp_.reduc
    if len(values) == 0:
        print("no more values")
        return
    values.sort(reverse=True)
    main_val = values[0]
    not_satisfied = True
    overdrive_speed: int
    overdrive_accel: int
    while not_satisfied:

        if main_val.a_deg == 0:
            return
        for n in range(len(values)):
            values[n].set_values(main_val.a_deg, global_mot_speed_, global_mot_accel_, highest_reduc)
        overdrive_speed = 0
        overdrive_accel = 0
        for n in range(len(values)):
            overdrive = values[n].get_overdrive()
            if overdrive[1] > overdrive_speed or overdrive[3] > overdrive_accel:
                overdrive_speed = overdrive[1]
                global_mot_speed_ = overdrive[0] / (overdrive[4] / main_val.a_deg)
                overdrive_accel = overdrive[3]
                global_mot_accel_ = overdrive[2] / (overdrive[4] / main_val.a_deg)
                print(f"overdrive at {n} with speed now being {global_mot_speed_} and acceleration {global_mot_accel_}")
                print(f"overdriven speed {overdrive[0]} or acceleration {overdrive[2]}")

        if overdrive_speed <= 0 and overdrive_accel <= 0:
            not_satisfied = False
        print("not satisfied")
    data = []
    for n in range(len(values)):
        data = data + values[n].get_msg()
    data.append(c.istart)
    print(data)
    asyncio.run(con(data))

def ik_movement(x_pos_: float, y_pos_: float, z_pos_: float, x_rot_: float, y_rot_: float, z_rot_: float,
        mot_speed0: int, mot_speed1: int, mot_speed2: int, mot_speed3: int, mot_speed4: int, mot_speed5: int,
        mot_inverse0: bool, mot_inverse1: bool, mot_inverse2: bool, mot_inverse3: bool, mot_inverse4: bool, mot_inverse5: bool,
        mot_mult0: float, mot_mult1: float, mot_mult2: float, mot_mult3: float, mot_mult4: float, mot_mult5: float,
        mot_accel0: int, mot_accel1: int, mot_accel2: int, mot_accel3: int, mot_accel4: int, mot_accel5: int,
        mot_reduc0: float, mot_reduc1: float, mot_reduc2: float, mot_reduc3: float, mot_reduc4: float, mot_reduc5: float,
                   global_mot_speed_: int, global_mot_accel_: int):
    mot_reduc_ = [mot_reduc0, mot_reduc1, mot_reduc2, mot_reduc3, mot_reduc4, mot_reduc5]
    mot_speed_ = [mot_speed0, mot_speed1, mot_speed2, mot_speed3, mot_speed4, mot_speed5]
    mot_inverse_ = [mot_inverse0, mot_inverse1, mot_inverse2, mot_inverse3,
                    mot_inverse4, mot_inverse5]
    mot_mult_ = [mot_mult0, mot_mult1, mot_mult2, mot_mult3, mot_mult4, mot_mult5]
    mot_accel_ = [mot_accel0, mot_accel1, mot_accel2, mot_accel3, mot_accel4, mot_accel5]
    class StepModule:
        def __init__(self, mot_: int, deg_: float, speed_: int, mult_: float, accel_: int, reduc_: float, cur_: float):
            self.motor = mot_
            self.deg = deg_
            self.a_deg = abs(deg_ - cur_)
            self.d_deg = abs(deg_)
            self.speed = 0
            self.accel = 0
            self.max_speed = round(speed_ * mult_)
            self.max_accel = round(accel_ * mult_)
            self.speed_overdrive = 0  # How much the calculated speed is over the current motor's maximum speed
            self.accel_overdrive = 0# How much the calculated acceleration is over the current motor's maximum acceleration
            self.reduc = reduc_

        def __lt__(self, other):
            return self.a_deg < other.a_deg

        def __repr__(self):
            return f"(Motor: {self.motor}, Degrees: {self.a_deg})"

        def __int__(self):
            return self.deg

        def set_values(self, deg_: float, speed: int, accel: int, reduc_: int) -> None:
            if self.a_deg == 0:
                return
            else:
                self.speed = round(speed * (self.a_deg / deg_) * self.reduc / reduc_)
                self.speed_overdrive = max(0, self.speed - self.max_speed)
                self.accel = round(accel * (self.a_deg / deg_) * self.reduc / reduc_)
                self.accel_overdrive = max(0, self.accel - self.max_accel)

        def get_overdrive(self):
            return self.max_speed, self.speed_overdrive, self.max_accel, self.accel_overdrive, self.a_deg

        def get_msg(self) -> list:
            if self.a_deg > 0:
                return [f"{self.motor}{c.ispeed}{self.speed}", f"{self.motor}{c.iaccel}{self.accel}", f"{self.motor}{c.ireduc}{self.reduc}", f"{self.motor}{c.iangle}{self.deg}"]
            else:
                return []

    cur_pos_ = asyncio.run(con_get([f'{mot}{c.icrpos}' for mot in range(6)]))
    # cur_pos_ = [0 for n in range(6)]

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

    pot = _l1 + Vector3(0, _l2.x, 0) + _l3 + _l4
    print(pot)
    ik = ik_calculate(pot.x - 40, pot.y, 0, 0, 0, 90)
    o3 = np.atan2(_l3.y, _l3.x)

    ik = ik_calculate(x_pos_, y_pos_, z_pos_, x_rot_, z_rot_, y_rot_)

    ik[1] -= np.pi / 2
    ik[2] -= -np.pi / 2 + o3
    ik = np.asarray(ik)
    np.round(ik, 6)

    mot_angle_ = ik.asarray()

    values = []
    highest_reduc = 0
    for n in range(6):
        temp_ = StepModule(n, mot_angle_[n] * (-1 if mot_inverse_[n] else 1), mot_speed_[n], mot_mult_[n], mot_accel_[n], mot_reduc_[n], float(cur_pos_[n]))
        if temp_.a_deg > 0:
            values.append(temp_)
            if highest_reduc < temp_.reduc:
                highest_reduc = temp_.reduc
    if len(values) == 0:
        print("no more values")
        return
    values.sort(reverse=True)
    main_val = values[0]
    not_satisfied = True
    overdrive_speed: int
    overdrive_accel: int
    while not_satisfied:

        if main_val.a_deg == 0:
            return
        for n in range(len(values)):
            values[n].set_values(main_val.a_deg, global_mot_speed_, global_mot_accel_, highest_reduc)
        overdrive_speed = 0
        overdrive_accel = 0
        for n in range(len(values)):
            overdrive = values[n].get_overdrive()
            if overdrive[1] > overdrive_speed or overdrive[3] > overdrive_accel:
                overdrive_speed = overdrive[1]
                global_mot_speed_ = overdrive[0] / (overdrive[4] / main_val.a_deg)
                overdrive_accel = overdrive[3]
                global_mot_accel_ = overdrive[2] / (overdrive[4] / main_val.a_deg)
                print(f"overdrive at {n} with speed now being {global_mot_speed_} and acceleration {global_mot_accel_}")
                print(f"overdriven speed {overdrive[0]} or acceleration {overdrive[2]}")

        if overdrive_speed <= 0 and overdrive_accel <= 0:
            not_satisfied = False
        print("not satisfied")
    data = []
    for n in range(len(values)):
        data = data + values[n].get_msg()
    data.append(c.istart)
    print(data)
    asyncio.run(con(data))


def home_motor(mot: int):
    print([f'{mot}{c.ihomst}'])
    asyncio.run(con([f'{mot}{c.ihomst}']))
    pass

def home_all_motors():
    asyncio.run(con([f'{n}{c.ihomst}' for n in range(6)]))

def enable_motor(mot: int, mode: bool):
    asyncio.run(con([f'{mot}{c.ienmot}{"1" if mode else "0"}']))
    return gr.Button(f"Submit Motor {mot + 1} Position", interactive=mode)

preset_list = user_config['preset_positions']

def deg_preset(set_: list):
    return set_

def deg_preset_add(deg1: int, deg2: int, deg3: int, deg4: int, deg5: int, deg6: int):
    global preset_list
    preset_list.append([deg1, deg2, deg3, deg4, deg5, deg6])
    return gr.Dataset(label='Motor Position Presets', components=[mot_deg[mot] for mot in range(6)], headers=[f'Motor {num + 1}' for num in range(6)], samples=preset_list)

def deg_preset_remove(deg1: int, deg2: int, deg3: int, deg4: int, deg5: int, deg6: int):
    global preset_list
    preset_list = [i for i in preset_list if i != [deg1, deg2, deg3, deg4, deg5, deg6]]
    return gr.Dataset(label='Motor Position Presets', components=[mot_deg[mot] for mot in range(6)], headers=[f'Motor {num + 1}' for num in range(6)], samples=preset_list)

with gr.Blocks() as iface:
    zero_state = gr.State(0)
    i_state = [gr.State(i) for i in range(6)]
    with gr.Accordion("Parameters", open=False):
        with gr.Tab(label='Motor Parameters'):
            mot_speed = []
            mot_inverse = []
            mot_accel = []
            mot_reduc = []
            global_mot_speed = gr.Number(value=user_config["general"]["global_mot_speed"], step=1, minimum=1,
                                         label="Global Motor Speed")
            global_mot_accel = gr.Number(value=user_config["general"]["global_mot_accel"], step=1, minimum=1,
                                         label="Global Motor Acceleration")
            with gr.Row():
                for i in range(6):
                    with gr.Group():
                        gr.HTML(f"<p{i}>Motor {i + 1}<p{i}>")
                        mot_speed.append(gr.Number(value=user_config[f"motor{i}"]["speed"], step=1, minimum=0, label="Maximum Speed", interactive=True))
                        mot_inverse.append(gr.Checkbox(label="Inverse Direction",
                                                            value=user_config[f"motor{i}"]["inverse_direction"], interactive=True))
                        mot_accel.append(gr.Number(value=user_config[f"motor{i}"]["acceleration"], step=1, minimum=0, label="Maximum Acceleration", interactive=True))
                        mot_reduc.append(gr.Number(value=user_config[f"motor{i}"]["reduction"], label="Reduction", interactive=True))
        with gr.Tab(label='Homing Parameters'):
            mot_home_speed = []
            mot_home_inverse = []
            mot_home_accel = []
            mot_shome_offset = []
            mot_home_mult = []
            mot_home_offset = []
            with gr.Row():
                for i in range(6):
                    with gr.Group():
                        gr.HTML(f"<p{i}>Motor {i + 1}<p{i}>")
                        mot_home_speed.append(gr.Number(value=user_config[f"motor{i}"]["home_speed"], step=1, minimum=0, label="Homing Speed", interactive=True))
                        mot_home_inverse.append(gr.Checkbox(label="Inverse Homing Direction", value=user_config[f"motor{i}"]["homing_inverse_direction"], interactive=True))
                        mot_home_accel.append(gr.Number(value=user_config[f"motor{i}"]["home_acceleration"], step=1, minimum=0, label="Homing Acceleration", interactive=True))
                        mot_shome_offset.append(gr.Number(value=user_config[f"motor{i}"]["shome_offset"], minimum=0,
                                                          label="Second Homing Offset", interactive=True))
                        mot_home_mult.append(
                            gr.Number(value=user_config[f"motor{i}"]["home_mult"], minimum=0, maximum=1,
                                      label="Second Homing Speed Multiplier", interactive=True))
                        mot_home_offset.append(gr.Number(value=user_config[f"motor{i}"]["home_offset"],
                                                          label="Homing Offset", interactive=True))


            submit_homing_params = gr.Button("Submit Technical Parameters")
            submit_homing_params.click(fn=submit_homing_parameters,
                                          inputs=[*mot_home_speed, *mot_home_inverse, *mot_home_accel,
                                                      *mot_shome_offset, *mot_home_mult, *mot_home_offset])
        with gr.Tab(label='Technical Parameters'):
            microsteps = []
            irun = []
            ihold = []
            with gr.Row():
                for i in range(6):
                    with gr.Group():
                        gr.HTML(f"<p{i}>Motor {i + 1}<p{i}>")
                        microsteps.append(gr.Number(value=user_config[f"motor{i}"]["microsteps"], step=1, minimum=0, label="Microsteps", interactive=True))
                        irun.append(gr.Number(value=user_config[f"motor{i}"]["irun"], step=1, minimum=0, maximum=31, label="IRUN", interactive=True))
                        ihold.append(gr.Number(value=user_config[f"motor{i}"]["ihold"], step=1, minimum=0, maximum=31, label="IHOLD", interactive=True))
            mot_steps = gr.Number(label='Number of Steps per full revolution',
                                  value=user_config["general"]["steps_p_revolution"], step=1, minimum=0, interactive=True)

    with gr.Accordion("Motor Settings"):
        with gr.Row():
            mot_en = []
            for i in range(6):
                en_mot = gr.Checkbox(label=f"Enable Motor {i + 1}", value=False)
                mot_en.append(en_mot)
            tmc_init = gr.Button("INIT TMC Drivers")
            tmc_init.click(fn=init_tmc, inputs=[*microsteps, *irun, *ihold, mot_steps])
        gr.HTML(f"<p>Emergency Motor Position Set<p>")
        with gr.Row():
            for i in range(6):
                with gr.Column():
                    mot_pos = gr.Number(label=f'Motor {i + 1} Position')
                    set_mot_pos = gr.Button(value="Set Motor Position")
                    set_mot_pos.click(fn=set_motor_position, inputs=[i_state[i], mot_pos])

    with gr.Accordion(label="Manual Movement", open=False):
        with gr.Accordion(label="Motor Homing", open=False):
            with gr.Column():
                home_all_btn = gr.Button("Home all Motors")
                home_all_btn.click(home_all_motors)
                with gr.Row():
                    home_btn = []
                    for i in range(6):
                        btn_ = gr.Button(f"Home Motor {i+1}")
                        btn_.click(fn=home_motor, inputs=[i_state[i]])
                        home_btn.append(btn_)

        with gr.Row():
            with gr.Column(min_width=1300):
                with gr.Row():
                    # Position
                    mot_deg = []
                    mot_mult = []
                    deg_btn = []
                    for i in range(6):
                        with gr.Group():
                            mot_deg_ = gr.Number(value=0, label=f"Degree Position of {n_th(i + 1)} Motor")
                            mot_deg.append(mot_deg_)
                            mot_mult_i = gr.Number(value=user_config[f'motor{i}']['speed_mult'], label=f"Motor Speed Multiplier", minimum=0, maximum=1)
                            mot_mult.append(mot_mult_i)
                            deg_btn_ = gr.Button(f"Submit Motor {i + 1} Position", interactive=False)
                            deg_btn_.click(individual_movement, inputs=[i_state[i], mot_deg_, mot_speed[i], mot_inverse[i], mot_mult_i, mot_accel[i], mot_reduc[i]])
                            deg_btn.append(deg_btn_)

                manual_btn = gr.Button("Submit Position")
                manual_btn.click(fn=manual_movement, inputs=[*mot_deg, *mot_speed, *mot_inverse, *mot_mult, *mot_accel, *mot_reduc, global_mot_speed, global_mot_accel])
            manual_zero_btn = gr.Button("Set All to Position 0")
            manual_zero_btn.click(manual_movement, inputs=[*[zero_state for j in range(6)], *mot_speed, *mot_inverse, *mot_mult, *mot_accel, *mot_reduc, global_mot_speed, global_mot_accel])
        deg_presets = gr.Dataset(label='Motor Position Presets', components=[mot_deg[i] for i in range(6)], headers=[f'Motor {i+1}' for i in range(6)], samples=preset_list)
        deg_presets.click(fn=deg_preset, inputs=[deg_presets], outputs=[mot_deg[i] for i in range(6)])
        deg_presets_add = gr.Button(value='Add Preset')
        deg_presets_add.click(fn=deg_preset_add, inputs=[mot_deg[i] for i in range(6)], outputs=[deg_presets])
        deg_presets_remove = gr.Button(value='Remove Preset')
        deg_presets_remove.click(fn=deg_preset_remove, inputs=[mot_deg[i] for i in range(6)], outputs=[deg_presets])

    with gr.Accordion(label="IK Movement", open=False):
        with gr.Row():
            with gr.Column():
                x_pos = gr.Number(value=0, label=f'X Position')
                y_pos = gr.Number(value=0, label=f'Y Position')
                z_pos = gr.Number(value=0, label=f'Z Position')
            with gr.Column():
                x_rot = gr.Number(value=0, label=f'X Rotation')
                y_rot = gr.Number(value=0, label=f'Y Rotation')
                z_rot = gr.Number(value=0, label=f'Z Rotation')
            with gr.Column():
                ik_btn = gr.Button("Submit Position")
                ik_btn.click(fn=ik_movement,
                                 inputs=[x_pos, y_pos, z_pos, x_rot, y_rot, z_rot, *mot_speed, *mot_inverse, *mot_mult, *mot_accel, *mot_reduc,
                                         global_mot_speed, global_mot_accel])
                ik_default_btn = gr.Button("Set All to Default Position")
                ik_default_btn.click(ik_movement,
                                  inputs=[*[zero_state for i in range(6)], *mot_speed, *mot_inverse, *mot_mult, *mot_accel,
                                          *mot_reduc, global_mot_speed, global_mot_accel])

    with gr.Accordion(label='Config Options', open=False):
        with gr.Row():
            save_config = gr.Button(value='Save Config')
            load_config = gr.Button(value='Load Config')

    for i in range(6):
        mot_en[i].input(fn=enable_motor, inputs=[i_state[i], mot_en[i]], outputs=[deg_btn[i]])

    save_config.click(fn=config_save, inputs=[global_mot_speed, global_mot_accel,
                                                *mot_speed, *mot_mult, *mot_inverse, *mot_accel, *mot_reduc,
                                                *mot_home_speed, *mot_home_inverse, *mot_home_accel, *mot_shome_offset, *mot_home_mult, *mot_home_offset,
                                                *microsteps, *irun, *ihold, mot_steps])
    load_config.click(fn=setup_config, outputs=[global_mot_speed, global_mot_accel,
                                                *mot_speed, *mot_mult, *mot_inverse, *mot_accel, *mot_reduc,
                                                *mot_home_speed, *mot_home_inverse, *mot_home_accel, *mot_shome_offset, *mot_home_mult, *mot_home_offset,
                                                *microsteps, *irun, *ihold, mot_steps,
                                                deg_presets])

iface.launch()
