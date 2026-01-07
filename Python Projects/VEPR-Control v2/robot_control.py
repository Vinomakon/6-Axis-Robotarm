import ui_tabs
import numpy as np
from data_transfer import *
import constants as c
import asyncio
from kinematics import ik_calculate, specific_ik_calculate
import kinematics
import json
import data_transfer
import tkinter as tk
from tkinter import ttk
import asyncio
import threading

class RobotControl:
    def __init__(self, root):
        self.root = root
        self.fk_tab: ui_tabs.FKControl = None
        self.ik_tab: ui_tabs.IKControl = None
        self.motor_tab: ui_tabs.MotorControl = None
        self.params_tabs: ui_tabs.VEPRParameters = None
        self.setup_tab: ui_tabs.RobotSetup = None
        self.automation: ui_tabs.RobotAutomation = None
        self.config = {}
        self.ik_config = {}
        self.positions = {}
        self.automations = {}
        self.data_transfer_notification: ttk.Label= ttk.Label(root, text="DATA TRANSFER OFFLINE", foreground="#ff0000", font=("bold", 30))
        self.run_automation = False
        self.automation_loop = asyncio.new_event_loop()
        self.automation_thread = None
        self._automation_future = None

    async def automation_runner(self):
        step = 0
        automations = self.automations["steps"]
        print(automations)
        while self.run_automation:
            if automations[step][0] == "fk":
                print("FK")
                self.submit_motor_rotations(*automations[step][1:-1])
            if automations[step][0] == "ik":
                print("IK")
                print(*automations[step][1:7])
                self.submit_ik(*automations[step][1:7])

            print("TOGETHER")
            await asyncio.sleep(automations[step][7] / 1000)
            print("YES")
            step = (step + 1) % len(self.automations["steps"])
            self.automation.next_step()

    def toggle_data_transfer(self, override: bool = None):
        if override is not None:
            data_transfer.allow_send = override
            if override:
                self.data_transfer_notification.pack_forget()
            else:
                self.data_transfer_notification.pack(fill="x")
            return
        data_transfer.allow_send = not data_transfer.allow_send
        if data_transfer.allow_send:
            self.data_transfer_notification.pack_forget()
        else:
            self.data_transfer_notification.pack(fill="x")

    def enable_automation(self, enable):
        self.run_automation = enable
        # Run the automation coroutine on a background asyncio event loop so
        # it doesn't block the Tkinter mainloop.
        if enable:
            # create a fresh loop and background thread for each enable
            self.automation_loop = asyncio.new_event_loop()

            def _run_loop():
                # set the event loop for this thread and run it
                asyncio.set_event_loop(self.automation_loop)
                try:
                    self.automation_loop.run_forever()
                finally:
                    # cancel any pending tasks and close the loop cleanly
                    try:
                        pending = asyncio.all_tasks(self.automation_loop)
                        for t in pending:
                            t.cancel()
                        self.automation_loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                    except Exception:
                        pass
                    try:
                        self.automation_loop.close()
                    except Exception:
                        pass

            self.automation_thread = threading.Thread(target=_run_loop, daemon=True)
            self.automation_thread.start()

            # schedule the automation coroutine on the background loop
            self._automation_future = asyncio.run_coroutine_threadsafe(self.automation_runner(), self.automation_loop)
        else:
            # signal the automation coroutine to stop
            self.run_automation = False
            # attempt to stop the loop and join the thread
            try:
                if self.automation_loop and self.automation_loop.is_running():
                    # stop the loop from the loop thread
                    self.automation_loop.call_soon_threadsafe(self.automation_loop.stop)
            except Exception:
                pass
            try:
                if self.automation_thread and self.automation_thread.is_alive():
                    self.automation_thread.join(timeout=1)
            except Exception:
                pass

    def set_tabs(self, fk: ui_tabs.FKControl, ik: ui_tabs.IKControl, motor: ui_tabs.MotorControl, params: ui_tabs.VEPRParameters, setup: ui_tabs.RobotSetup, automation: ui_tabs.RobotAutomation):
        self.fk_tab = fk
        self.ik_tab = ik
        self.motor_tab = motor
        self.params_tabs = params
        self.setup_tab = setup
        self.automation = automation

    def _run_coro_blocking(self, coro):
        """Run an async coroutine and return its result.

        If we're running inside the automation thread's event loop use
        run_coroutine_threadsafe against that loop. Otherwise fall back to
        asyncio.run so interactive calls from the Tk main thread still work.
        """
        try:
            # If the automation loop is running and we're inside its thread,
            # schedule the coroutine there and wait for the result.
            if getattr(self, 'automation_loop', None) and getattr(self, 'automation_thread', None) and self.automation_loop.is_running() and threading.current_thread() == self.automation_thread:
                fut = asyncio.run_coroutine_threadsafe(coro, self.automation_loop)
                return fut.result()
            # Otherwise run in this thread (synchronous blocking)
            return asyncio.run(coro)
        except Exception as e:
            print(f"Error while running coroutine: {e}")
            raise


    def submit_motor_rotations(self, m1, m2, m3, m4, m5, m6):
        print(m1, m2, m3, m4, m5, m6)
        self.calculate_movement(np.asarray([m1, m2, m3, m4, m5, m6], dtype="float"))

    def submit_tab_motor_rotations(self):
        self.calculate_movement(np.asarray([float(i.get()) for i in self.fk_tab.mot_pos]))

    def submit_tab_motor_rotations_zero(self):
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

        cur_pos = np.float64(np.asarray(self._run_coro_blocking(con_get([f'{mot}{c.icrpos}' for mot in range(6)]))))
        if len(cur_pos) == 0:
            cur_pos = np.zeros(6)

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
        self._run_coro_blocking(con(send_data))

    def submit_ik(self, x, y, z, psi, theta, phi):
        print(x, y, z, psi, theta, phi, "Hey")
        ik_results = specific_ik_calculate(x, y, z, psi, theta, phi)
        self.calculate_movement(ik_results)

    def submit_tab_ik(self):
        ik_results = specific_ik_calculate(self.ik_tab.x_pos.get(), self.ik_tab.y_pos.get(), self.ik_tab.z_pos.get(), self.ik_tab.x_rot.get(), self.ik_tab.y_rot.get(), self.ik_tab.z_rot.get())
        self.calculate_movement(ik_results)


    def submit_tab_ik_default(self):
        ik_results = specific_ik_calculate(*kinematics.default_configuration)
        self.calculate_movement(ik_results)

    def enable_mot(self):
        data = []
        for i in range(6):
            data.append(f'{i}{c.ienmot}{"1" if self.motor_tab.enable_mots[i].get() else "0"}')
        self._run_coro_blocking(con(data))

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
        self._run_coro_blocking(con(data))

    def submit_params(self):
        pass

    def set_motor_position(self, mot):
        self._run_coro_blocking(con([f'{mot}{c.istpos}{self.motor_tab.emergency_motor_position[mot]}']))

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

    def load_positions(self):
        with open('../data/positions.json') as f:
            self.positions = json.load(f)
            f.close()

    def save_positions(self):
        with open('../data/positions.json') as f:
            self.positions = json.load(f)
            f.close()

    def load_automation(self):
        with open('../data/automations.json') as f:
            self.automations = json.load(f)
            f.close()

        print(self.automations["steps"])
        self.automation.load_steps(self.automations["steps"])

    def save_automation(self):
        with open('../data/automations.json') as f:
            self.automations = json.load(f)
            f.close()