import asyncio
import gradio as gr
import websockets
import sys
import os
import constants as c
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
    mot_home_offset_ = []
    mot_home_mult_ = []
    microsteps_ = []
    rms_current_ = []
    hold_current_mult_ = []
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
        mot_home_offset_.append(gr.Number(value=user_config[f"motor{m}"]["home_offset"], label="Homing Offset"))
        mot_home_mult_.append(gr.Number(value=user_config[f"motor{m}"]["home_mult"], minimum=0, maximum=1, label="Second Homing Speed Multiplier"))

        microsteps_.append(gr.Number(value=user_config[f"motor{m}"]["microsteps"], step=1, minimum=0, label="Microsteps"))
        rms_current_.append(gr.Number(value=user_config[f"motor{m}"]["rms_current"], step=1, minimum=0, label="RMS Current"))
        hold_current_mult_.append(gr.Number(value=user_config[f"motor{m}"]["hold_current_mult"], label="Hold Current Multiplier"))

        mot_mult_.append(gr.Number(value=user_config[f'motor{m}']['speed_mult'], label=f"Motor Speed Multiplier", minimum=0, maximum=1))

    mot_steps_ = gr.Number(label='Number of Steps per full revolution',
                                  value=user_config["general"]["steps_p_revolution"], step=1, minimum=0)
    preset_list = user_config_['preset_positions']
    deg_presets_ = gr.Dataset(label='Motor Position Presets', components=[mot_deg[mot] for mot in range(6)],
                             headers=[f'Motor {num + 1}' for num in range(6)], samples=preset_list)

    return [*mot_speed_, *mot_inverse_, *mot_accel_, *mot_reduc_,
            *mot_home_speed_, *mot_home_inverse_, *mot_home_accel_, *mot_home_offset_, *mot_home_mult_,
            *microsteps_, *rms_current_, *hold_current_mult_, mot_steps_,
            *mot_mult, deg_presets_]

def config_save():
    save = {}
    for j in range(6):
        save[f'motor{j}'] = {}
        save[f'motor{j}']['speed'] = mot_speed[j].value
        save[f'motor{j}']['inverse_direction'] = mot_inverse[j].value
        save[f'motor{j}']['acceleration'] = mot_accel[j].value
        save[f'motor{j}']['reduction'] = mot_reduc[j].value
        save[f'motor{j}']['speed_mult'] = mot_mult[j].value
        save[f'motor{j}']['home_speed'] = mot_home_speed[j].value
        save[f'motor{j}']['homing_inverse_direction'] = mot_home_inverse[j].value
        save[f'motor{j}']['home_acceleration'] = mot_home_accel[j].value
        save[f'motor{j}']['home_offset'] = mot_home_offset[j].value
        save[f'motor{j}']['home_mult'] = mot_home_mult[j].value
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

def init_tmc():
    submit_params()
    asyncio.run(con([f'{mot}{c.itmcen}' for mot in range(6)]))

def submit_params():
    data = []
    for mot in range(6):
        data.append(f'{mot}{c.ispeed}{mot_speed[mot].value}')
        data.append(f'{mot}{c.iaccel}{mot_speed[mot].value}')
        data.append(f'{mot}{c.ireduc}{mot_reduc[mot].value}')

        data.append(f'{mot}{c.ihomsp}{mot_home_speed[mot].value}')
        data.append(f'{mot}{c.ihomin}{mot_home_inverse[mot].value}')
        data.append(f'{mot}{c.ihomac}{mot_home_accel[mot].value}')
        data.append(f'{mot}{c.ihomof}{mot_home_offset[mot].value}')
        data.append(f'{mot}{c.ihommu}{mot_home_mult[mot].value}')

        data.append(f'{mot}{c.imrstp}{microsteps[mot].value}')
        data.append(f'{mot}{c.ihcmlt}{rms_current[mot].value}')
        data.append(f'{mot}{c.icrpos}{hold_current_mult[mot].value}')
    data.append(f'{c.igener}{c.idefst}{mot_steps.value}')
    asyncio.run(con(data))

def individual_movement(mot: int):
    mult = mot_mult[mot].value
    speed = f'{mot}1{mot_speed[mot].value * mult}'
    accel = f'{mot}2{mot_accel[mot].value * mult}'
    move = f"{mot}0{mot_deg[mot].value}"
    asyncio.run(con([speed, accel, move, '000']))

def start_movement():
    class StepModule:
        def __init__(self, motor: int, deg: float, speed: int, accel: int, cur_: float):
            self.motor = motor
            self.steps = deg
            self.a_degs = abs(deg - cur_)
            self.d_degs = abs(deg)
            self.speed = speed * mot_mult[motor]
            self.accel = accel * mot_mult[motor]
            self.speed = 0
            self.accel = 0

        def __lt__(self, other):
            return self.a_degs < other.a_degs

        def __repr__(self):
            return f"(Motor: {self.motor}, Degrees: {self.a_degs})"

        def __int__(self):
            return self.steps

        def set_values(self, deg: float) -> None:
            if self.a_degs == 0:
                return
            else:
                self.speed = self.speed * (self.a_degs / deg)
                self.accel = self.accel * (self.a_degs / deg)

        def get_msg(self) -> list:
            return [f"{self.motor}0{self.steps}", f"{self.motor}1{self.speed}", f"{self.motor}2{self.accel}"]

    cur_pos_ = asyncio.run(con_get([f'{mot + 1}8' for mot in range(6)]))
    values = [StepModule(n, mot_deg[n], mot_speed[n], mot_accel[n], float(cur_pos_[n])) for n in range(6)]
    values.sort(reverse=True)
    main_val = values[0]
    if main_val.a_degs == 0:
        return
    for n in range(6):
        values[n].set_values(main_val.a_degs)
    data = []
    for n in range(6):
        data = data + values[n].get_msg()
    data.append('000')
    asyncio.run(con(data))

def home_motor(mot: int):
    asyncio.run(con([f"{mot + 1}3"]))
    pass

def home_all_motors():
    asyncio.run(con(["03", "13", "23", "33", "43", "53"]))

def enable_motors():
    data = []
    for m in range(6):
        data.append(f"{m}{c.ienmot}{'1' if mot_en[m].value else '0'}")
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
            mot_inverse = []
            mot_accel = []
            mot_reduc = []
            with gr.Row():
                for i in range(6):
                    with gr.Group():
                        gr.HTML(f"<p{i}>Motor {i + 1}<p{i}>")
                        mot_speed.append(gr.Number(value=user_config[f"motor{i}"]["speed"], step=1, minimum=0, label="Speed", interactive=True))
                        mot_inverse.append(gr.Checkbox(label="Inverse Direction",
                                                            value=user_config[f"motor{i}"]["inverse_direction"], interactive=True))
                        mot_accel.append(gr.Number(value=user_config[f"motor{i}"]["acceleration"], step=1, minimum=0, label="Acceleration", interactive=True))
                        mot_reduc.append(gr.Number(value=user_config[f"motor{i}"]["reduction"], label="Reduction", interactive=True))
        with gr.Tab(label='Homing Parameters'):
            mot_home_speed = []
            mot_home_inverse = []
            mot_home_accel = []
            mot_home_offset = []
            mot_home_mult = []
            with gr.Row():
                for i in range(6):
                    with gr.Group():
                        gr.HTML(f"<p{i}>Motor {i + 1}<p{i}>")
                        mot_home_speed.append(gr.Number(value=user_config[f"motor{i}"]["home_speed"], step=1, minimum=0, label="Homing Speed", interactive=True))
                        mot_home_inverse.append(gr.Checkbox(label="Inverse Homing Direction", value=user_config[f"motor{i}"]["homing_inverse_direction"], interactive=True))
                        mot_home_accel.append(gr.Number(value=user_config[f"motor{i}"]["home_acceleration"], step=1, minimum=0, label="Homing Acceleration", interactive=True))
                        mot_home_offset.append(gr.Number(value=user_config[f"motor{i}"]["home_offset"], minimum=0, label="Homing Offset", interactive=True))
                        mot_home_mult.append(
                            gr.Number(value=user_config[f"motor{i}"]["home_mult"], minimum=0, maximum=1, label="Second Homing Speed Multiplier", interactive=True))
        with gr.Tab(label='Technical Parameters'):
            microsteps = []
            rms_current = []
            hold_current_mult = []
            with gr.Row():
                for i in range(6):
                    with gr.Group():
                        gr.HTML(f"<p{i}>Motor {i + 1}<p{i}>")
                        microsteps.append(gr.Number(value=user_config[f"motor{i}"]["microsteps"], step=1, minimum=0, label="Microsteps", interactive=True))
                        rms_current.append(gr.Number(value=user_config[f"motor{i}"]["rms_current"], step=1, minimum=0, label="RMS Current", interactive=True))
                        hold_current_mult.append(gr.Number(value=user_config[f"motor{i}"]["hold_current_mult"], label="Hold Current Multiplier", interactive=True))
            mot_steps = gr.Number(label='Number of Steps per full revolution',
                                  value=user_config["general"]["steps_p_revolution"], step=1, minimum=0, interactive=True)
        submit_params = gr.Button("Submit all Parameters")
        submit_params.click()

    with gr.Row():
        mot_en = []
        for i in range(6):
            en_mot = gr.Checkbox(label=f"Enable Motor {i + 1}", value=False)
            en_mot.input(fn=enable_motors)
            mot_en.append(en_mot)
        tmc_init = gr.Button("INIT TMC Drivers")
        tmc_init.click(fn=init_tmc)

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
                    mot_mult = []
                    for i in range(6):
                        with gr.Group():
                            motor_i = gr.State(i)
                            mot_deg_ = gr.Number(value=0, label=f"Degree Position of {n_th(i + 1)} Motor")
                            mot_deg.append(mot_deg_)
                            mot_mult_i = gr.Number(value=user_config[f'motor{i}']['speed_mult'], label=f"Motor Speed Multiplier", minimum=0, maximum=1)
                            mot_mult.append(mot_mult_i)
                            deg_btn_ = gr.Button(f"Submit Motor {i + 1} Position")
                            deg_btn_.click(individual_movement, inputs=[motor_i])

                start_btn = gr.Button("Submit Position")
                start_btn.click(fn=start_movement)
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
            load_config.click(fn=setup_config, outputs=[*mot_speed, *mot_home_inverse, *mot_accel, *mot_reduc,
                                                        *mot_home_speed, *mot_home_inverse, *mot_home_accel, *mot_home_offset, *mot_home_mult,
                                                        *microsteps, *rms_current, *hold_current_mult, mot_steps,
                                                        *mot_mult, deg_presets])

iface.launch()
