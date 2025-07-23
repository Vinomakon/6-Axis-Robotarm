import asyncio
import gradio as gr
import websockets
import sys
import os
from constants import *
import json
from formatting import n_th

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
    with open('data/config.json') as f:
        d = json.load(f)
        print(d)
        f.close()
        return d

def setup_config():
    user_config_ = load_json_config()
    global preset_list
    mot_speed_ = []
    mot_accel_ = []
    mot_r_ = []
    for i in range(6):
        mot_speed_.append(gr.Number(value=user_config_[f"motor{i}"]["speed"], step=1, minimum=0, label="Speed"))
        mot_accel_.append(gr.Number(value=user_config_[f"motor{i}"]["acceleration"], step=1, minimum=0,
                                       label="Motor Acceleration"))
        mot_r_.append(gr.Number(value=user_config_[f"motor{i}"]["reduction"], label="Reduction"))
        preset_list = user_config_['preset_positions']
    deg_presets_ = gr.Dataset(label='Motor Position Presets', components=[mot_deg[mot] for mot in range(6)],
                             headers=[f'Motor {num + 1}' for num in range(6)], samples=preset_list)

    return [*mot_speed_, *mot_accel_, *mot_r_, deg_presets_]

def config_save():
    save = {}
    for j in range(6):
        save[f'motor{j}'] = {}
        save[f'motor{j}']['speed'] = mot_speed[j].value
        save[f'motor{j}']['acceleration'] = mot_accel[j].value
        save[f'motor{j}']['reduction'] = mot_r[j].value
        save[f'motor{j}']['home_speed'] = mot_home_speed[j].value
        save[f'motor{j}']['home_acceleration'] = mot_home_accel[j].value
        save[f'motor{j}']['home_offset'] = mot_home_offset[j].value
        save[f'motor{j}']['microsteps'] = microsteps[j].value
        save[f'motor{j}']['rms_current'] = rms_current[j].value
        save[f'motor{j}']['hold_current_mult'] = hold_current_mult[j].value
    save['general'] = {}
    save['general']['steps_p_revolution'] = mot_steps.value
    save['preset_positions'] = preset_list

    with open('data/config.json', "w") as f:
        json.dump(save, f)
        f.close()
    print('Successfully saved config to \'config.json\'')

user_config = load_json_config()


def givePos1(x: float):
    data = f"10{x}"
    asyncio.run(con([data]))


def givePos2(x: float):
    data = f"20{x}"
    asyncio.run(con([data]))


def set_stepPS1(x: int):
    data = f"11{x}"
    asyncio.run(con([data]))


def set_stepPS2(x: int):
    data = f"21{x}"
    asyncio.run(con([data]))


def set_global_stepsPS(x: float):
    data = f"01{x}"
    asyncio.run(con([data]))


def initTMC():
    asyncio.run(con(["99"]))


def individual_movement(mot: int, mot_s: int, mot_a: int, deg: float):
    data = f"{mot + 1}0{deg}"
    asyncio.run(con([data]))
    print(f"{mot}, {mot_s}, {mot_a}, {deg}")


def startMovement(synch: bool,
                  mot_s: int, mot_a: int,
                  b_mot_s: int, b_mot_a: int,
                  b_m1: bool, b_m2: bool, b_m3: bool, b_m4: bool, b_m5: bool, b_m6: bool,
                  m_deg1: float, m_deg2: float, m_deg3: float, m_deg4: float, m_deg5: float, m_deg6: float):
    degs = [m_deg1, m_deg2, m_deg3, m_deg4, m_deg5, m_deg6]
    b_mot = [b_m1, b_m2, b_m3, b_m4, b_m5, b_m6]

    class step_module:
        def __init__(self, motor: int, b_: bool, deg: float, cur_: float):
            self.motor = motor
            self.steps = deg
            self.a_degs = abs(deg - cur_)
            self.d_degs = abs(deg)
            if b_:
                self.def_speed = b_mot_s
                self.def_accel = b_mot_a
            else:
                self.def_speed = mot_s
                self.def_accel = mot_a
            self.speed = 0
            self.accel = 0

        def __lt__(self, other):
            return self.a_degs < other.a_degs

        def __repr__(self):
            return f"(Motor: {self.motor}, Degrees: {self.a_degs})"

        def __int__(self):
            return self.steps

        def setValues(self, deg: float) -> None:
            if self.a_degs == 0:
                self.speed = self.def_speed
                self.accel = self.def_accel
            else:
                self.speed = self.def_speed * (self.a_degs / deg)
                self.accel = self.def_accel * (self.a_degs / deg)

        def getMsg(self):
            return [f"{self.motor}0{self.steps}", f"{self.motor}1{self.speed}", f"{self.motor}2{self.accel}"]

    """if synch:
        cur_poss = asyncio.run(con_get([getPos1(), getPos2()]))
        print(cur_poss)
        steps = [step_module(1, step1, float(cur_poss[0])), step_module(2, step2, float(cur_poss[1]))]
        steps.sort()
        speeds = []
        accels = []
        for i in range(len(steps)):
            if i == 0:
                speeds.append(speed)
                accels.append(accel)
                continue
            if steps[i].t_steps == 0:
                speeds.append(int(speed))
            else:
                speeds.append(int(speed * (steps[0] / steps[i])))
            if steps[0].t_steps == 0:
                accels.append(int(accel))
            else:
                accels.append(int(accel * (steps[i] / steps[0])))
        send_data = [get_setPos1(step1), get_setPos2(step2)]
        if steps[0].motor == 1:
            send_data.append(get_stepPS1(speeds[1]))
            send_data.append(get_accel1(accels[0]))
            send_data.append(get_stepPS2(speeds[0]))
            send_data.append(get_accel2(accels[1]))
        else:
            send_data.append(get_stepPS1(speeds[0]))
            send_data.append(get_accel1(accels[1]))
            send_data.append(get_stepPS2(speeds[1]))
            send_data.append(get_accel2(accels[0]))
        send_data.append("00")
        asyncio.run(con(send_data))"""
    if synch:
        cur_poss = asyncio.run(con_get(["18", "28", "38", "48", "58", "68"]))
        values = [step_module(i + 1, b_mot[i], degs[i], float(cur_poss[i])) for i in range(6)]
        values.sort(reverse=True)
        main_val = values[0]
        if main_val.a_degs == 0:
            return
        for i in range(6):
            values[i].setValues(main_val.a_degs)
        data = []
        for i in range(6):
            for j in values[i].getMsg():
                data.append(j)
        data.append("00")
        asyncio.run(con(data))

    else:
        send_data = []
        for m in range(6):
            cur = m + 1
            b = b_mot[m]
            send_data.append(f"{cur}0{degs[m]}")
            send_data.append(f"{cur}1{b_mot_s if b else mot_s}")
            send_data.append(f"{cur}2{b_mot_a if b else mot_a}")
        # send_data = [get_setPos1(step1), get_setPos2(step2), get_stepPS1(speed), get_stepPS2(speed), "00"]
        send_data.append("00")
        asyncio.run(con(send_data))


def home_motor(mot: int):
    asyncio.run(con([f"{mot + 1}3"]))
    pass


def home_all_motors():
    asyncio.run(con(["13", "23", "33", "43", "53", "63"]))


def en_mot(m1: bool, m2: bool, m3: bool, m4: bool, m5: bool, m6: bool):
    mots = [m1, m2, m3, m4, m5, m6]
    data = []
    for m in range(6):
        data.append(f"{m + 1}9{1 if mots[m] else 0}")
    asyncio.run(con(data))


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
    with gr.Accordion("Parameters", open=False):
        with gr.Tab(label='Motor Parameters'):
            mot_speed = []
            mot_accel = []
            mot_r = []
            with gr.Row():
                for i in range(6):
                    with gr.Group():
                        gr.HTML(f"<p{i}>Motor {i + 1}<p{i}>")
                        mot_speed.append(gr.Number(value=user_config[f"motor{i}"]["speed"], step=1, minimum=0, label="Speed"))
                        mot_accel.append(gr.Number(value=user_config[f"motor{i}"]["acceleration"], step=1, minimum=0, label="Acceleration"))
                        mot_r.append(gr.Number(value=user_config[f"motor{i}"]["reduction"], label="Reduction"))
        with gr.Tab(label='Homing Parameters'):
            mot_home_speed = []
            mot_home_accel = []
            mot_home_offset = []
            with gr.Row():
                for i in range(6):
                    with gr.Group():
                        gr.HTML(f"<p{i}>Motor {i + 1}<p{i}>")
                        mot_home_speed.append(gr.Number(value=user_config[f"motor{i}"]["home_speed"], step=1, minimum=0, label="Homing Speed"))
                        mot_home_accel.append(gr.Number(value=user_config[f"motor{i}"]["home_acceleration"], step=1, minimum=0, label="Homing Acceleration"))
                        mot_home_offset.append(gr.Number(value=user_config[f"motor{i}"]["home_offset"], label="Homing Offset"))
        with gr.Tab(label='Technical Parameters'):
            microsteps = []
            rms_current = []
            hold_current_mult = []
            with gr.Row():
                for i in range(6):
                    with gr.Group():
                        gr.HTML(f"<p{i}>Motor {i + 1}<p{i}>")
                        microsteps.append(gr.Number(value=user_config[f"motor{i}"]["microsteps"], step=1, minimum=0, label="Microsteps"))
                        rms_current.append(gr.Number(value=user_config[f"motor{i}"]["rms_current"], step=1, minimum=0, label="RMS Current"))
                        hold_current_mult.append(gr.Number(value=user_config[f"motor{i}"]["hold_current_mult"], label="Hold Current Multiplier"))
            mot_steps = gr.Number(label='Number of Steps per full revolution',
                                  value=user_config["general"]["steps_p_revolution"], step=1, minimum=0)

    with gr.Row():
        mot_en = []
        for i in range(6):
            mot_en.append(gr.Checkbox(label=f"Enable Motor {i + 1}", value=False))
        mot_en_but = gr.Button("Submit States")
        mot_en_but.click(en_mot, inputs=tuple(mot_en))
        init_tmc = gr.Button("INIT TMCs")
        init_tmc.click(initTMC)

    with gr.Accordion(label="Motor Positions"):
        with gr.Accordion(label="Motor Homing", open=False):
            with gr.Column():
                home_all_btn = gr.Button("Home all Motors")
                home_all_btn.click(home_all_motors)
                with gr.Row():
                    home_btn = []
                    for i in range(6):
                        home_st = gr.State(i)
                        btn_ = gr.Button(f"Home Motor {i+1}")
                        btn_.click(fn=home_motor, inputs=[home_st])
                        home_btn.append(btn_)

        sync_movement = gr.Checkbox(value=False, label="Synchronous Movement")
        with gr.Row():
            with gr.Column(min_width=1300):
                with gr.Row():
                    # Position
                    mot_deg = []
                    for i in range(6):
                        with gr.Group():
                            motor_i = gr.State(i)
                            mot_deg_ = gr.Number(value=0, label=f"Degree Position of {n_th(i + 1)} Motor")
                            mot_deg.append(mot_deg_)
                            deg_btn_ = gr.Button(f"Submit Motor {i + 1} Position")
                            deg_btn_.click(individual_movement, inputs=[motor_i, mot_speed[i], mot_accel[i], mot_deg_])

                start_btn = gr.Button("Submit Position")
                ''' start_btn.click(startMovement, inputs=[
                    sync_movement,
                    mot_speed, mot_accel, b_mot_speed, b_mot_accel,
                    r_mot1, r_mot2, r_mot3, r_mot4, r_mot5, r_mot6,
                    deg1, deg2, deg3, deg4, deg5, deg6
                ])'''
            home_btn = gr.Button("Set All to Position 0")
            ''' home_btn.click(startMovement, inputs=[
                    sync_movement,
                    mot_speed, mot_accel, b_mot_speed, b_mot_accel,
                    r_mot1, r_mot2, r_mot3, r_mot4, r_mot5, r_mot6,
                    global_deg, global_deg, global_deg, global_deg, global_deg, global_deg
                ]) '''
        deg_presets = gr.Dataset(label='Motor Position Presets', components=[mot_deg[i] for i in range(6)], headers=[f'Motor {i+1}' for i in range(6)], samples=preset_list)
        deg_presets.click(fn=deg_preset, inputs=[deg_presets], outputs=[mot_deg[i] for i in range(6)])
        deg_presets_add = gr.Button(value='Add Preset')
        deg_presets_add.click(fn=deg_preset_add, inputs=[mot_deg[i] for i in range(6)], outputs=[deg_presets])
        deg_presets_remove = gr.Button(value='Remove Preset')
        deg_presets_remove.click(fn=deg_preset_remove, inputs=[mot_deg[i] for i in range(6)], outputs=[deg_presets])
    with gr.Accordion(label='Config Options', open=False):
        with gr.Row():
            save_config = gr.Button(value='Save Config')
            save_config.click(fn=config_save)
            load_config = gr.Button(value='Load Config')
            load_config.click(fn=setup_config, outputs=[*mot_speed, *mot_accel, *mot_r, deg_presets])

iface.launch()
