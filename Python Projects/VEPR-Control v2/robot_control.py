import ui_tabs
import numpy as np
from data_transfer import *
import constants as c
import asyncio
from kinematics import ik_calculate
import kinematics
import json

class RobotControl:
    def __init__(self):
        self.fk_tab: ui_tabs.FKControl = None
        self.ik_tab: ui_tabs.IKControl = None
        self.motor_tab: ui_tabs.MotorControl = None
        self.params_tabs: ui_tabs.VEPRParameters = None
        self.setup_tab: ui_tabs.RobotSetup = None
        self.config = {}
        self.ik_config = {}

    def set_tabs(self, fk: ui_tabs.FKControl, ik: ui_tabs.IKControl, motor: ui_tabs.MotorControl, params: ui_tabs.VEPRParameters, setup: ui_tabs.RobotSetup):
        self.fk_tab = fk
        self.ik_tab = ik
        self.motor_tab = motor
        self.params_tabs = params
        self.setup_tab = setup

    def submit_motor_rotations(self):
        self.calculate_movement(np.array([float(i.get()) for i in self.fk_tab.mot_pos]))

    def submit_motor_rotations_zero(self):
        self.calculate_movement(np.zeros(6, dtype="float"))

    def calculate_movement(self, rotations):
        global_mot_speed = self.params_tabs.mot_params.global_motor_speed.get()
        global_mot_accel = self.params_tabs.mot_params.global_motor_accel.get()

        mot_inverse = np.where(np.asarray([int(i.get()) for i in self.params_tabs.mot_params.inverse_direction]) == 0, 1, -1)
        mot_speed = np.asarray([int(i.get()) for i in self.params_tabs.mot_params.max_speed])
        mot_mult = np.asarray([int(i.get()) for i in self.params_tabs.mot_params.multiplier])
        mot_speed *= mot_mult
        mot_accel = np.asarray([int(i.get()) for i in self.params_tabs.mot_params.max_accel])
        mot_reduc = np.asarray([int(i.get()) for i in self.params_tabs.mot_params.reduction])

        mot_microsteps = np.asarray([int(i.get()) for i in self.params_tabs.tech_params.microsteps]) / 16

        default_steps = self.params_tabs.tech_params.steps_per_full_revolution.get()



        """
        class StepModule:
            def __init__(self, mot_: int, deg_: float, speed_: int, mult_: float, accel_: int, reduc_: float,
                         cur_: float):
                self.motor = mot_
                self.deg = deg_
                self.a_deg = abs(deg_ - cur_)
                self.d_deg = abs(deg_)
                self.speed = 0
                self.accel = 0
                self.max_speed = round(speed_ * mult_)
                self.max_accel = round(accel_ * mult_)
                self.speed_overdrive = 0  # How much the calculated speed is over the current motor's maximum speed
                self.accel_overdrive = 0  # How much the calculated acceleration is over the current motor's maximum acceleration
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
                    return [f"{self.motor}{c.ispeed}{self.speed}", f"{self.motor}{c.iaccel}{self.accel}",
                            f"{self.motor}{c.ireduc}{self.reduc}", f"{self.motor}{c.iangle}{self.deg}"]
                else:
                    return []

        # cur_pos = asyncio.run(con_get([f'{mot}{c.icrpos}' for mot in range(6)]))
        cur_pos = [0 for n in range(6)]

        values = []
        highest_reduc = 0
        for n in range(6):
            temp_ = StepModule(n, rotations[n] * (-1 if mot_inverse[n] else 1), mot_speed[n], mot_mult[n],
                               mot_accel[n], mot_reduc[n], float(cur_pos[n]))
            if temp_.a_deg > 0:
                values.append(temp_)
                if highest_reduc < temp_.reduc:
                    highest_reduc = temp_.reduc
        if len(values) == 0:
            # print("no more values")
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
                values[n].set_values(main_val.a_deg, global_mot_speed, global_mot_accel, highest_reduc)
            overdrive_speed = 0
            overdrive_accel = 0
            for n in range(len(values)):
                overdrive = values[n].get_overdrive()
                if overdrive[1] > overdrive_speed or overdrive[3] > overdrive_accel:
                    overdrive_speed = overdrive[1]
                    global_mot_speed = overdrive[0] / (overdrive[4] / main_val.a_deg)
                    overdrive_accel = overdrive[3]
                    global_mot_accel = overdrive[2] / (overdrive[4] / main_val.a_deg)
                    # print( f"overdrive at {n} with speed now being {global_mot_speed_} and acceleration {global_mot_accel_}")
                    # print(f"overdriven speed {overdrive[0]} or acceleration {overdrive[2]}")

            if overdrive_speed <= 0 and overdrive_accel <= 0:
                not_satisfied = False
            # print("not satisfied")
        data = []
        for n in range(len(values)):
            data = data + values[n].get_msg()
        data.append(c.istart)
        # print(data)
        asyncio.run(con(data))
        """

        mot_dir = np.where(rotations < 0, -1, 1) * mot_inverse

        absolute_steps = np.abs(rotations * mot_reduc * mot_microsteps * default_steps)
        max_mot = np.argmax(absolute_steps)

        max_steps = absolute_steps[max_mot]

        if max_steps == 0:
            return

        mults = absolute_steps / max_steps
        speeds = mults * global_mot_speed
        accels = mults * global_mot_accel

        overdrives_speed = np.argwhere(speeds > mot_speed).flatten()
        print("Overdrive detected at:", overdrives_speed)
        if len(overdrives_speed):
            max_od_mult = 0
            max_od_idx = 0
            for od in overdrives_speed:
                cur_mult = (mults * global_mot_speed)[od] / mot_speed[od]
                if max_od_mult < cur_mult:
                    max_od_mult = cur_mult
                    max_od_idx = od
            speeds = mults * mot_speed[max_od_idx] / mults[max_od_idx]

        overdrives_accel = np.argwhere(accels > mot_accel).flatten()
        print("Overdrive detected at:", overdrives_accel)
        if len(overdrives_accel):
            max_od_mult = 0
            max_od_idx = 0
            for od in overdrives_speed:
                cur_mult = (mults * global_mot_accel)[od] / mot_accel[od]
                if max_od_mult < cur_mult:
                    max_od_mult = cur_mult
                    max_od_idx = od
            accels = mults * mot_accel[max_od_idx] / mults[max_od_idx]

        print("After:", speeds)
        print("Maximum:", mot_speed)

        print("After:", accels)
        print("Maximum:", mot_accel)

        new_rotations = rotations * mot_inverse

        send_data = []
        for n in range(6):
            send_data.append(f"{n}{c.ispeed}{speeds[n]}")
            send_data.append(f"{n}{c.iaccel}{accels[n]}")
            send_data.append(f"{n}{c.ireduc}{mot_reduc[n]}")
            send_data.append(f"{n}{c.iangle}{new_rotations[n]}")
        send_data.append(c.istart)
        print(send_data)
        # asyncio.run(con(send_data))

    def submit_ik(self):
        ik_results = ik_calculate(self.ik_tab.x_pos.get(), self.ik_tab.y_pos.get(), self.ik_tab.z_pos.get(), self.ik_tab.x_rot.get(), self.ik_tab.y_rot.get(), self.ik_tab.z_rot.get())

        o3 = np.atan2(kinematics.l3.y, kinematics.l3.x)
        ik_results[1] -= np.pi / 2
        ik_results[2] -= -np.pi / 2 + o3

        ik_results = np.asarray(ik_results)
        np.rad2deg(ik_results)
        print(ik_results)
        self.calculate_movement(ik_results)

    def submit_ik_default(self):
        print(kinematics.default_configuration)
        ik_results = ik_calculate(*kinematics.default_configuration)

        o3 = np.atan2(kinematics.l3.y, kinematics.l3.x)
        ik_results[1] -= np.pi / 2
        ik_results[2] -= -np.pi / 2 + o3

        ik_results = np.asarray(ik_results)
        np.rad2deg(ik_results)
        np.round(ik_results, 6)
        print(ik_results)
        self.calculate_movement(ik_results)

    def enable_mot(self, mot):
        asyncio.run(con([f'{mot}{c.ienmot}{"1" if self.motor_tab.enable_mots[mot] else "0"}']))

    def init_tmcs(self):
        microsteps = [int(i.get()) for i in self.params_tabs.tech_params.microsteps]
        irun = [int(i.get()) for i in self.params_tabs.tech_params.irun]
        ihold = [int(i.get()) for i in self.params_tabs.tech_params.ihold]
        data = []
        for mot in range(6):
            data.append(f'{mot}{c.imrstp}{microsteps[mot]}')
            data.append(f'{mot}{c.i_irun}{irun[mot]}')
            data.append(f'{mot}{c.i_hold}{ihold[mot]}')
            data.append(f'{mot}{c.itmcen}')
        data.append(f'{c.igener}{c.idefst}{self.params_tabs.tech_params.steps_per_full_revolution}')
        asyncio.run(con(data))

    def submit_params(self):
        pass

    def set_motor_position(self, mot):
        asyncio.run(con([f'{mot}{c.istpos}{self.motor_tab.emergency_motor_position[mot]}']))

    def load_config(self):
        with open('../data/user_config.json') as f:
            self.config = json.load(f)
            f.close()

        self.params_tabs.mot_params.global_motor_speed.set(self.config["general"]["global_mot_speed"])
        self.params_tabs.mot_params.global_motor_accel.set(self.config["general"]["global_mot_accel"])
        self.params_tabs.tech_params.steps_per_full_revolution.set(self.config["general"]["steps_p_revolution"])

        for m in range(6):
            mot_config = self.config[f"motor{m}"]
            self.params_tabs.mot_params.max_speed[m].set(mot_config["speed"])
            self.params_tabs.mot_params.max_accel[m].set(mot_config["acceleration"])
            self.params_tabs.mot_params.inverse_direction[m].set(mot_config["inverse_direction"])
            self.params_tabs.mot_params.reduction[m].set(mot_config["reduction"])
            self.params_tabs.mot_params.multiplier[m].set(mot_config["speed_mult"])

            self.params_tabs.home_params.homing_speed[m].set(mot_config["home_speed"])
            self.params_tabs.home_params.homing_accel[m].set(mot_config["home_acceleration"])
            self.params_tabs.home_params.inverse_homing_direction[m].set(mot_config["homing_inverse_direction"])
            self.params_tabs.home_params.second_homing_offset[m].set(mot_config["shome_offset"])
            self.params_tabs.home_params.second_homing_mult[m].set(mot_config["home_mult"])
            self.params_tabs.home_params.homing_offset[m].set(mot_config["home_offset"])

            self.params_tabs.tech_params.microsteps[m].set(mot_config["microsteps"])
            self.params_tabs.tech_params.irun[m].set(mot_config["irun"])
            self.params_tabs.tech_params.ihold[m].set(mot_config["ihold"])

    def save_config(self):
        config = {}
        for m in range(6):
            config[f'motor{m}'] = {}
            config[f'motor{m}']['speed'] = self.params_tabs.mot_params.max_speed[m].get()
            config[f'motor{m}']['acceleration'] = self.params_tabs.mot_params.max_accel[m].get()
            config[f'motor{m}']['inverse_direction'] = self.params_tabs.mot_params.inverse_direction[m].get()
            config[f'motor{m}']['reduction'] = self.params_tabs.mot_params.reduction[m].get()
            config[f'motor{m}']['speed_mult'] = self.params_tabs.mot_params.multiplier[m].get()
            config[f'motor{m}']['home_speed'] = self.params_tabs.home_params.homing_speed[m].get()
            config[f'motor{m}']['homing_inverse_direction'] = self.params_tabs.home_params.inverse_homing_direction[m].get()
            config[f'motor{m}']['home_acceleration'] = self.params_tabs.home_params.homing_accel[m].get()
            config[f'motor{m}']['shome_offset'] = self.params_tabs.home_params.second_homing_offset[m].get()
            config[f'motor{m}']['home_mult'] = self.params_tabs.home_params.second_homing_mult[m].get()
            config[f'motor{m}']['home_offset'] = self.params_tabs.home_params.homing_offset[m].get()

            config[f'motor{m}']['microsteps'] = self.params_tabs.tech_params.microsteps[m].get()
            config[f'motor{m}']['irun'] = self.params_tabs.tech_params.irun[m].get()
            config[f'motor{m}']['ihold'] = self.params_tabs.tech_params.ihold[m].get()
        config['general'] = {}
        config['general']['global_mot_speed'] = self.params_tabs.mot_params.global_motor_speed.get()
        config['general']['global_mot_accel'] = self.params_tabs.mot_params.global_motor_accel.get()
        config['general']['steps_p_revolution'] = self.params_tabs.tech_params.steps_per_full_revolution.get()

        with open('../data/user_config.json', "w") as f:
            json.dump(config, f)
            f.close()

        self.config = config

        print('Successfully saved config to \'user_config.json\'')

    def load_robot_setup(self):
        with open('../data/ik_config.json') as f:
            self.ik_config = json.load(f)
            f.close()

        for i in range(6):
            self.setup_tab.x_offset[i].set(self.ik_config[f"motor{i}"]["x"])
            self.setup_tab.y_offset[i].set(self.ik_config[f"motor{i}"]["y"])
            self.setup_tab.z_offset[i].set(self.ik_config[f"motor{i}"]["z"])

        self.setup_tab.x_offset[6].set(self.ik_config["extension"]["x"])
        self.setup_tab.y_offset[6].set(self.ik_config["extension"]["y"])
        self.setup_tab.z_offset[6].set(self.ik_config["extension"]["z"])

    def save_robot_setup(self):
        config = {}

        for i in range(6):
            config[f"motor{i}"] = {}
            config[f"motor{i}"]["x"] = self.setup_tab.x_offset[i].get()
            config[f"motor{i}"]["y"] = self.setup_tab.y_offset[i].get()
            config[f"motor{i}"]["z"] = self.setup_tab.z_offset[i].get()

        config["extension"] = {}
        config["extension"]["x"] = self.setup_tab.x_offset[6].get()
        config["extension"]["y"] = self.setup_tab.y_offset[6].get()
        config["extension"]["z"] = self.setup_tab.z_offset[6].get()

        with open('../data/ik_config.json', "w") as f:
            json.dump(config, f)
            f.close()
        print('Successfully saved setup to \'ik_config.json\'')