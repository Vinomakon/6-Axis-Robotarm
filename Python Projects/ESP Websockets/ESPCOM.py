import asyncio
import gradio as gr
import websockets
from constants import *

'''
// 00 (Start Movement)
// 01 (Move first motor to position X)
// 02 (Move second motor to position X)
'''
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


def startMovement(synch: bool, speed: float, step1: float, step2: float):
    class step_module:
        def __init__(self, motor, step, cur):
            self.motor = motor
            self.steps = step
            self.t_steps = abs(step - cur)
            self.a_steps = abs(step)

        def __lt__(self, other):
            return self.t_steps < other.t_steps

        def __repr__(self):
            return f"(Motor: {self.motor}; Steps: {self.t_steps})"

        def __int__(self):
            return self.t_steps

        def __truediv__(self, other) -> int:
            return self.t_steps / other.t_steps

    if synch:
        cur_poss = asyncio.run(con_get([getPos1(), getPos2()]))
        print(cur_poss)
        steps = [step_module(1, step1, float(cur_poss[0])), step_module(2, step2, float(cur_poss[1]))]
        steps.sort()
        speeds = []
        for i in range(len(steps)):
            if i == 0:
                speeds.append(speed)
                continue
            speeds.append(round(speed * (steps[0] / steps[i]), 5))
        send_data = [get_setPos1(step1), get_setPos2(step2)]
        if steps[0].motor == 1:
            send_data.append(get_stepPS1(speeds[1]))
            send_data.append(get_stepPS2(speeds[0]))
        else:
            send_data.append(get_stepPS1(speeds[0]))
            send_data.append(get_stepPS2(speeds[1]))
        send_data.append("00")
        asyncio.run(con(send_data))
    else:
        send_data = [get_setPos1(step1), get_setPos2(step2), get_global_stepsPS(speed), "00"]
        asyncio.run(con(send_data))


def homeSend(synch: bool, speed: float):
    startMovement(synch, speed, 0, 0)


with gr.Blocks() as iface:
    init_tmc = gr.Button("INIT TMCs")
    init_tmc.click(initTMC)

    # Motor 1
    with gr.Row():
        # Position
        deg1 = gr.Number(value=0, label="Degree Position of first Motor", minimum=-360 * 3, maximum=360 * 3)
        deg1_btn = gr.Button("Submit DegreePosition")

    # Motor 2
    with gr.Row():
        # Position
        deg2 = gr.Number(value=0, label="Degree Position of second Motor", minimum=-360 * 3, maximum=360 * 3)
        deg2_btn = gr.Button("Submit DegreePosition")

    # Global Variables
    with gr.Row():
        speed_set = gr.Number(value=1000, label="Global Motor Speed", minimum=0, maximum=10000)
        speed_btn = gr.Button("Submit Global Speed")

    sync_movement = gr.Checkbox(value=False, label="Synchronous Movement")
    start_btn = gr.Button("Start Movement")
    start_btn.click(startMovement, inputs=[sync_movement, speed_set, deg1, deg2])
    home_btn = gr.Button("Set To 0")
    home_btn.click(homeSend, inputs=[sync_movement, speed_set])
    # CHOPCONF
    '''
    with gr.Accordion("CHOPCONF", open=False):
        toff = gr.Slider(value=0, label="Off Time {toff}", minimum=0, maximum=15, step=1)
        hstrt = gr.Slider(value=0, label="Hysteresis Start Value {hstrt}", minimum=0, maximum=7, step=1)
        hend = gr.Slider(value=0, label="Hysteresis End Value {hend}", minimum=0, maximum=15, step=1)
        fd3 = gr.Checkbox(value=False, label="TFD {fd3}")
        disfdcc = gr.Checkbox(value=False, label="Fast Decay Mode {disfdcc}")
        rndtf = gr.Checkbox(value=False, label="Random Off Time {rndtf}")
        chm = gr.Checkbox(value=True, label="Chopper Mode {chm}")
        tbl = gr.Dropdown([16, 24, 36, 54], interactive=True, label="Blank Time Select {tbl}")
        vsense = gr.Checkbox(value=False, label="Sense Resistor Voltage {vsense}")
        vhighfs = gr.Checkbox(value=False, label="High Velocity Fullstep Selection {vhighfs}")
        vhighchm = gr.Checkbox(value=False, label="High Velocity Chopper Mode {vhighchm}")
        sync = gr.Slider(value=0, label="PWM Sync Clock", minimum=0, maximum=15, step=1)
        mres = gr.Dropdown([256, 128, 64, 32, 16, 8, 4, 2, 1], interactive=True, label="Step Resolution {mres}")
        intpol = gr.Checkbox(value=False, label="Interpolation to 256 Microsteps {intpol}")
        dedge = gr.Checkbox(value=False, label="Enable Double Edge Step Pulses {dedge}")
        diss2g = gr.Checkbox(value=False, label="Short to Ground {diss2g}")'''

iface.launch()
