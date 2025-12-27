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
        self.calculate_movement(np.asarray([float(i.get()) for i in self.fk_tab.mot_pos]))

    def submit_motor_rotations_zero(self):
        self.calculate_movement(np.zeros(6, dtype="float"))

    def calculate_movement(self, rotations):
        global_mot_speed = self.params_tabs.mot_params.global_motor_speed.get()
        global_mot_accel = self.params_tabs.mot_params.global_motor_accel.get()

        mot_inverse = np.where(np.asarray([int(i.get()) for i in self.params_tabs.mot_params.inverse_direction]) == 0, 1, -1)
        mot_speed = np.asarray([int(i.get()) for i in self.params_tabs.mot_params.max_speed], dtype="float")
        mot_mult = np.asarray([float(i.get()) for i in self.params_tabs.mot_params.multiplier])
        mot_speed *= mot_mult
        mot_accel = np.asarray([int(i.get()) for i in self.params_tabs.mot_params.max_accel], dtype="float")
        mot_reduc = np.asarray([float(i.get()) for i in self.params_tabs.mot_params.reduction], dtype="float")

        mot_microsteps = np.asarray([int(i.get()) for i in self.params_tabs.tech_params.microsteps], dtype="float") / 16

        default_steps = self.params_tabs.tech_params.steps_per_full_revolution.get()

        cur_pos = np.float64(np.asarray(asyncio.run(con_get([f'{mot}{c.icrpos}' for mot in range(6)]))))

        absolute_steps = np.abs(np.abs(rotations - cur_pos) * mot_reduc * mot_microsteps * default_steps)
        max_mot = np.argmax(absolute_steps)

        max_steps = absolute_steps[max_mot]


        if max_steps == 0:
            return

        mults = absolute_steps / max_steps
        speeds = mults * global_mot_speed
        accels = mults * global_mot_accel

        overdrives_speed = np.argwhere(speeds > mot_speed).flatten()
        # print("Overdrive detected at:", overdrives_speed)
        if len(overdrives_speed):
            max_od_mult = 0
            max_od_idx = 0
            for od in overdrives_speed:
                cur_mult = (mults * global_mot_speed)[od] / mot_speed[od]
                if max_od_mult < cur_mult:
                    max_od_mult = cur_mult
                    max_od_idx = od
            speeds = mults * mot_speed[max_od_idx] / mults[max_od_idx]

        # FIX ACCELERATION, WHERE IT SHOULD BE DEPENDENT ON THE REDUCTION, NOT THE ABSOLUTE AMOUNT OF STEPS
        
        overdrives_accel = np.argwhere(accels > mot_accel).flatten()
        print("Overdrive detected at:", overdrives_accel)
        if len(overdrives_accel):
            max_od_mult = 0
            max_od_idx = 0
            for od in overdrives_accel:
                cur_mult = (mults * global_mot_accel)[od] / mot_accel[od]
                if max_od_mult < cur_mult:
                    max_od_mult = cur_mult
                    max_od_idx = od
            accels = mults * mot_accel[max_od_idx] / mults[max_od_idx]

        print("Speeds:", speeds)
        # print("Maximum:", mot_speed)

        print("Accelerations:", accels)
        # print("Maximum:", mot_accel)

        new_rotations = rotations * mot_inverse

        send_data = []
        for n in range(6):
            if absolute_steps[n] == 0:
                continue
            send_data.append(f"{n}{c.ispeed}{speeds[n]}")
            send_data.append(f"{n}{c.iaccel}{accels[n]}")
            send_data.append(f"{n}{c.ireduc}{mot_reduc[n]}")
            send_data.append(f"{n}{c.iangle}{new_rotations[n]}")
        send_data.append(c.istart)
        # print(send_data)
        asyncio.run(con(send_data))

    def submit_ik(self):
        print([self.ik_tab.x_pos.get(), self.ik_tab.y_pos.get(), self.ik_tab.z_pos.get(), self.ik_tab.x_rot.get(), self.ik_tab.y_rot.get(), self.ik_tab.z_rot.get()])

        ik_results = ik_calculate(self.ik_tab.x_pos.get(), self.ik_tab.y_pos.get(), self.ik_tab.z_pos.get(), self.ik_tab.x_rot.get(), self.ik_tab.y_rot.get(), self.ik_tab.z_rot.get())

        o3 = np.atan2(kinematics.l3.y, kinematics.l3.x)
        ik_results[1] -= np.pi / 2
        ik_results[2] -= -np.pi / 2 + o3

        ik_results = np.asarray(ik_results)
        self.calculate_movement(np.round(np.rad2deg(ik_results), 6))

    def submit_ik_default(self):
        print(kinematics.default_configuration)
        ik_results = ik_calculate(*kinematics.default_configuration)

        o3 = np.atan2(kinematics.l3.y, kinematics.l3.x)
        ik_results[1] -= np.pi / 2
        ik_results[2] -= -np.pi / 2 + o3

        ik_results = np.round(np.rad2deg(np.asarray(ik_results)), 6)

        print(ik_results)
        self.calculate_movement(ik_results)

    def enable_mot(self):
        data = []
        for i in range(6):
            data.append(f'{i}{c.ienmot}{"1" if self.motor_tab.enable_mots[i].get() else "0"}')
        asyncio.run(con(data))

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