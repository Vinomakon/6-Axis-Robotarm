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


def home_motor1():
    asyncio.run(con(["13"]))


def home_motor2():
    asyncio.run(con(["23"]))


def home_motor3():
    asyncio.run(con(["33"]))


def home_motor4():
    asyncio.run(con(["43"]))


def home_motor5():
    asyncio.run(con(["53"]))


def home_motor6():
    asyncio.run(con(["63"]))


def home_all_motors():
    asyncio.run(con(["13", "23", "33", "43", "53", "63"]))


def en_mot(m1: bool, m2: bool, m3: bool, m4: bool, m5: bool, m6: bool):
    mots = [m1, m2, m3, m4, m5, m6]
    data = []
    for m in range(6):
        data.append(f"{m + 1}9{1 if mots[m] else 0}")
    asyncio.run(con(data))


with gr.Blocks() as iface:
    with gr.Accordion("Motor Parameters", open=False):
        with gr.Row():
            with gr.Column():
                mot_speed = gr.Number(value=600, step=1, minimum=0, label="Motor Speed")
                mot_accel = gr.Number(value=800, step=1, minimum=0, label="Motor Acceleration")
            with gr.Column():
                b_mot_speed = gr.Number(value=6000, step=1, label="Big Motor Speed")
                b_mot_accel = gr.Number(value=10000, step=1, label="Big Motor Acceleration")
        with gr.Row():
            mot1_en = gr.Checkbox(label="Enable Motor 1", value=False)
            mot2_en = gr.Checkbox(label="Enable Motor 2", value=False)
            mot3_en = gr.Checkbox(label="Enable Motor 3", value=False)
            mot4_en = gr.Checkbox(label="Enable Motor 4", value=False)
            mot5_en = gr.Checkbox(label="Enable Motor 5", value=False)
            mot6_en = gr.Checkbox(label="Enable Motor 6", value=False)
            mot_en = gr.Button("Submit States")
            mot_en.click(en_mot, inputs=[mot1_en, mot2_en, mot3_en, mot4_en, mot5_en, mot6_en])
        with gr.Row():
            b_mot1 = gr.Checkbox(label="Big Motor 1", value=False)
            b_mot2 = gr.Checkbox(label="Big Motor 2", value=False)
            b_mot3 = gr.Checkbox(label="Big Motor 3", value=True)
            b_mot4 = gr.Checkbox(label="Big Motor 4", value=True)
            b_mot5 = gr.Checkbox(label="Big Motor 5", value=False)
            b_mot6 = gr.Checkbox(label="Big Motor 6", value=False)
            big_mot = gr.Button("Submit States", interactive=False)
            # big_mot.click(mot_big, inputs=[b_mot1, b_mot2, b_mot3, b_mot4, b_mot5])

    init_tmc = gr.Button("INIT TMCs")
    init_tmc.click(initTMC)

    with gr.Column():
        home_all_btn = gr.Button("Home all Motors")
        home_all_btn.click(home_all_motors)

        with gr.Row():
            home1_btn = gr.Button("Home Motor 1")
            home1_btn.click(home_motor1)
            home2_btn = gr.Button("Home Motor 2")
            home2_btn.click(home_motor2)
            home3_btn = gr.Button("Home Motor 3")
            home3_btn.click(home_motor3)
            home4_btn = gr.Button("Home Motor 4")
            home4_btn.click(home_motor4)
            home5_btn = gr.Button("Home Motor 5")
            home5_btn.click(home_motor5)
            home6_btn = gr.Button("Home Motor 6")
            home6_btn.click(home_motor6)

    with gr.Row():
        # Position
        deg1 = gr.Number(value=0, label="Degree Position of 1st Motor")
        deg2 = gr.Number(value=0, label="Degree Position of 2nd Motor")
        deg3 = gr.Number(value=0, label="Degree Position of 3rd Motor")
        deg4 = gr.Number(value=0, label="Degree Position of 4th Motor")
        deg5 = gr.Number(value=0, label="Degree Position of 5th Motor")
        deg6 = gr.Number(value=0, label="Degree Position of 6th Motor")

    sync_movement = gr.Checkbox(value=False, label="Synchronous Movement")
    start_btn = gr.Button("Submit Position")
    start_btn.click(startMovement, inputs=[
        sync_movement,
        mot_speed, mot_accel, b_mot_speed, b_mot_accel,
        b_mot1, b_mot2, b_mot3, b_mot4, b_mot5, b_mot6,
        deg1, deg2, deg3, deg4, deg5, deg6
    ])

    global_deg = gr.Number(value=0, label="Global Position")

    home_btn = gr.Button("Set All Global Position")
    home_btn.click(startMovement, inputs=[
        sync_movement,
        mot_speed, mot_accel, b_mot_speed, b_mot_accel,
        b_mot1, b_mot2, b_mot3, b_mot4, b_mot5, b_mot6,
        global_deg, global_deg, global_deg, global_deg, global_deg, global_deg
    ])

iface.launch()
