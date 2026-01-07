import tkinter as tk
from tkinter import ttk

from torch.backends.cudnn import enabled
import copy

import kinematics
import numpy as np
import asyncio

class ToggledFrame(tk.Frame):
    def __init__(self, parent, text="", *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.show = tk.IntVar()
        self.show.set(0)

        self.title_frame = ttk.Frame(self)
        self.title_frame.pack(fill="x", expand=1)

        ttk.Label(self.title_frame, text=text).pack(side="left", fill="x", expand=1)
        self.toggle_button = ttk.Checkbutton(self.title_frame, width=2, text='ᐯ', command=self.toggle, variable=self.show, style='Toolbutton')
        self.toggle_button.pack(side="left")

        self.sub_frame = tk.Frame(self, relief="sunken", borderwidth=1)

    def toggle(self):
        if bool(self.show.get()):
            self.sub_frame.pack(fill="x", expand=1)
            self.toggle_button.configure(text='ᐱ')
        else:
            self.sub_frame.forget()
            self.toggle_button.configure(text='ᐯ')

class FKControl(tk.Frame):
    def __init__(self, parent, robot, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        mot_args = tk.Frame(self)
        mot_args.pack(fill="x")

        self.mot_pos = [tk.IntVar(value=0) for i in range(6)]
        self.fk_results = [tk.DoubleVar(value=0) for i in range(6)]

        for i in range(6):
            mot = tk.Frame(mot_args)
            mot.pack(fill="x", side="left", expand=1)

            ttk.Label(mot, text=f'Motor {i}').pack(fill="x", expand=1, padx=3, pady=6)
            pos = ttk.Entry(mot, textvariable=self.mot_pos[i])
            pos.pack(fill="x", padx=3, expand=1, pady=3)

        self.calculate_xd_but = ttk.Button(self, text="Calculate Position and Rotation of End-Effector", command=self.calculate_end_effector)
        self.calculate_xd_but.pack(fill="x", padx=3, pady=3)

        mot_calcs = tk.Frame(self)
        mot_calcs.pack(fill="x", pady=3, padx=3)

        axes = ["X", "Y", "Z"]

        for i in range(3):
            mot = tk.Frame(mot_calcs)
            mot.pack(fill="x", side="left", expand=1)
            ttk.Label(mot, text=f"{axes[i]} Position").pack(fill="x", expand=1, padx=3, pady=6)
            ttk.Entry(mot, textvariable=self.fk_results[i], state="readonly").pack(fill="x", expand=1, padx=3, pady=6)
        for i in range(3):
            mot = tk.Frame(mot_calcs)
            mot.pack(fill="x", side="left", expand=1)
            ttk.Label(mot, text=f"{axes[i]} Rotation").pack(fill="x", expand=1, padx=3, pady=6)
            ttk.Entry(mot, textvariable=self.fk_results[i+3], state="readonly").pack(fill="x", expand=1, padx=3, pady=6)

        self.submit_but = ttk.Button(self, text="Submit Motor Rotations", command=robot.submit_tab_motor_rotations)
        self.submit_but.pack(fill="x", padx=3, pady=3)

        self.submit_default_but = ttk.Button(self, text="Set All to Rotation 0", command=robot.submit_tab_motor_rotations_zero)
        self.submit_default_but.pack(fill="x", padx=3, pady=3)

    def calculate_end_effector(self):
        for idx, val in enumerate(kinematics.fk_calculate(*[float(self.mot_pos[i].get()) for i in range(6)])):
            self.fk_results[idx].set(val)

class IKControl(tk.Frame):
    def __init__(self, parent, robot, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.x_pos = tk.DoubleVar(value=kinematics.default_configuration[0])
        self.y_pos = tk.DoubleVar(value=kinematics.default_configuration[1])
        self.z_pos = tk.DoubleVar(value=kinematics.default_configuration[2])
        self.x_rot = tk.DoubleVar(value=kinematics.default_configuration[3])
        self.y_rot = tk.DoubleVar(value=kinematics.default_configuration[4])
        self.z_rot = tk.DoubleVar(value=kinematics.default_configuration[5])

        self.ik_results_raw = [0.0 for i in range(6)]
        self.ik_results = [tk.DoubleVar(value=0) for i in range(6)]

        ik_args = tk.Frame(self)
        ik_args.pack(fill="x")

        positional_args = tk.Frame(ik_args)
        positional_args.pack(side="left", fill="x", padx=3, pady=3, expand=1)

        ttk.Label(positional_args, text='X Position').pack(fill="x", expand=1, pady=6)
        ttk.Entry(positional_args, textvariable=self.x_pos).pack(fill="x", expand=1)
        ttk.Label(positional_args, text='Y Position').pack(fill="x", expand=1, pady=6)
        ttk.Entry(positional_args, textvariable=self.y_pos).pack(fill="x", expand=1)
        ttk.Label(positional_args, text='Z Position').pack(fill="x", expand=1, pady=6)
        ttk.Entry(positional_args, textvariable=self.z_pos).pack(fill="x", expand=1)

        rotational_args = tk.Frame(ik_args)
        rotational_args.pack(side="right", fill="x", padx=3, expand=1)

        ttk.Label(rotational_args, text='X Rotation').pack(fill="x", expand=1, pady=6)
        ttk.Entry(rotational_args, textvariable=self.x_rot).pack(fill="x", expand=1)
        ttk.Label(rotational_args, text='Y Rotation').pack(fill="x", expand=1, pady=6)
        ttk.Entry(rotational_args, textvariable=self.y_rot).pack(fill="x", expand=1)
        ttk.Label(rotational_args, text='Z Rotation').pack(fill="x", expand=1, pady=6)
        ttk.Entry(rotational_args, textvariable=self.z_rot).pack(fill="x", expand=1)

        self.calculate_mots_but = ttk.Button(self, text="Calculate Rotations of Motors", command=self.calculate_motor_rotations)
        self.calculate_mots_but.pack(fill="x", padx=3, pady=3)

        mot_calcs = tk.Frame(self)
        mot_calcs.pack(fill="x", pady=3, padx=3)

        for i in range(6):
            mot = tk.Frame(mot_calcs)
            mot.pack(fill="x", side="left", expand=1)
            ttk.Label(mot, text=f"Rotation of Motor {i}").pack(fill="x", expand=1, padx=3, pady=6)
            ttk.Entry(mot, textvariable=self.ik_results[i], state="readonly").pack(fill="x", expand=1, padx=3, pady=6)

        self.submit_but = ttk.Button(self, text="Submit Positional and Rotational Arguments", command=robot.submit_tab_ik)
        self.submit_but.pack(fill="x", padx=3, pady=3)

        self.submit_default_but = ttk.Button(self, text="Set to Default", command=robot.submit_tab_ik_default)
        self.submit_default_but.pack(fill="x", padx=3, pady=3)

    def calculate_motor_rotations(self):
        self.ik_results_raw = kinematics.ik_calculate(self.x_pos.get(), self.y_pos.get(), self.z_pos.get(), self.x_rot.get(), self.y_rot.get(), self.z_rot.get())
        o3 = np.atan2(kinematics.l3.y, kinematics.l3.x)
        self.ik_results_raw[1] -= np.pi / 2
        self.ik_results_raw[2] -= -np.pi / 2 + o3
        print(self.ik_results_raw)
        for i in range(6):
            self.ik_results[i].set(np.round(np.rad2deg(self.ik_results_raw[i]), 6))

class MotorControl(tk.Frame):
    def __init__(self, parent, robot, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.enable_mots = [tk.BooleanVar(value=False) for i in range(6)]
        self.emergency_motor_position = [tk.IntVar(value=False) for i in range(6)]

        init_tmcs = ttk.Button(self, text="Initialize TMC5160-Drivers", command=robot.init_tmcs)
        init_tmcs.pack(fill="x", padx=3, pady=3)

        en_mots_frame = tk.Frame(self)
        en_mots_frame.pack(fill="x", padx=3, pady=3)

        for i in range(6):
            mot = tk.Frame(en_mots_frame, borderwidth=1, relief="solid", padx=1)
            mot.pack(expand=1, side="left")
            ttk.Label(en_mots_frame, text=f"Enable Motor {i}").pack(fill="x", side="left")
            en = ttk.Checkbutton(en_mots_frame, variable=self.enable_mots[i], takefocus=0, command=robot.enable_mot)
            en.pack(fill="x", side="left")

        emergency_set = tk.Frame(self, borderwidth=5, relief="ridge")
        emergency_set.pack(fill="x", padx=3, pady=3)

        ttk.Label(emergency_set, text="Emergency Motor Position Set").pack(fill="x", padx=3, pady=3, expand=1)

        for i in range(6):
            mot = tk.Frame(emergency_set)
            mot.pack(side="left", fill="x", expand=1)

            ttk.Label(mot, text=f"Motor {i} Position").pack(fill="x", expand=1)
            pos = ttk.Entry(mot, textvariable=self.emergency_motor_position[i])
            pos.pack(fill="x", padx=3, expand=1)

class VEPRParameters(tk.Frame):
    class MotorParameters(tk.Frame):
        def __init__(self, parent, *args, **kwargs):
            tk.Frame.__init__(self, parent, *args, **kwargs)

            self.global_motor_speed = tk.IntVar(value=0)
            self.global_motor_accel = tk.IntVar(value=0)

            self.max_speed = [tk.IntVar(value=0) for i in range(6)]
            self.inverse_direction = [tk.BooleanVar(value=False) for i in range(6)]
            self.max_accel = [tk.IntVar(value=0) for i in range(6)]
            self.reduction = [tk.DoubleVar(value=0) for i in range(6)]
            self.multiplier = [tk.DoubleVar(value=0) for i in range(6)]

            ttk.Label(self, text='Global Maximum Speed').pack(fill="x", padx=3, pady=3)
            ttk.Entry(self, textvariable=self.global_motor_speed).pack(fill="x", padx=3, pady=3)

            ttk.Label(self, text='Global Maximum Acceleration').pack(fill="x", padx=3, pady=3)
            ttk.Entry(self, textvariable=self.global_motor_accel).pack(fill="x", padx=3, pady=3)

            mots_frame = tk.Frame(self, relief="solid", borderwidth=1)
            mots_frame.pack(fill="x", padx=3, pady=3)

            for i in range(6):
                mot = tk.Frame(mots_frame, relief="solid", borderwidth=1)
                mot.pack(fill="x", expand=1, side="left")
                ttk.Label(mot, text=f'Motor {i}').pack(fill="x", padx=3, pady=8, expand=1)
                ttk.Label(mot, text='Maximum Speed').pack(fill="x", padx=3, pady=3, expand=1)
                ttk.Entry(mot, textvariable=self.max_speed[i]).pack(fill="x", padx=3, pady=3, expand=1)
                ttk.Label(mot, text='Speed Multiplier').pack(fill="x", padx=3, pady=3, expand=1)
                ttk.Entry(mot, textvariable=self.multiplier[i]).pack(fill="x", padx=3, pady=3, expand=1)
                inv_dir_frame = tk.Frame(mot)
                inv_dir_frame.pack(fill="x", padx=3, pady=3)
                ttk.Label(inv_dir_frame, text='Inverse Direction').pack(side="left", fill="x", padx=3, pady=3, expand=1)
                ttk.Checkbutton(inv_dir_frame, variable=self.inverse_direction[i], takefocus = 0).pack(side="left", fill="x", padx=3, pady=3, expand=1)
                ttk.Label(mot, text='Maximum Acceleration').pack(fill="x", padx=3, pady=3, expand=1)
                ttk.Entry(mot, textvariable=self.max_accel[i]).pack(fill="x", padx=3, pady=3, expand=1)
                ttk.Label(mot, text='Motor Reduction').pack(fill="x", padx=3, pady=3, expand=1)
                ttk.Entry(mot, textvariable=self.reduction[i]).pack(fill="x", padx=3, pady=3, expand=1)

    class HomingParameters(tk.Frame):
        def __init__(self, parent, *args, **kwargs):
            tk.Frame.__init__(self, parent, *args, **kwargs)

            self.homing_speed = [tk.IntVar(value=0) for i in range(6)]
            self.inverse_homing_direction = [tk.BooleanVar(value=False) for i in range(6)]
            self.homing_accel = [tk.IntVar(value=0) for i in range(6)]
            self.second_homing_mult = [tk.DoubleVar(value=0) for i in range(6)]
            self.second_homing_offset = [tk.IntVar(value=0) for i in range(6)]
            self.homing_offset = [tk.IntVar(value=0) for i in range(6)]

            mots_frame = tk.Frame(self)
            mots_frame.pack(fill="x", padx=3, pady=3)

            for i in range(6):
                mot = tk.Frame(mots_frame, relief="solid", borderwidth=1)
                mot.pack(fill="x", expand=1, side="left")
                ttk.Label(mot, text=f'Motor {i}').pack(fill="x", padx=3, pady=8, expand=1)
                ttk.Label(mot, text='Homing Speed').pack(fill="x", padx=3, pady=3, expand=1)
                ttk.Entry(mot, textvariable=self.homing_speed[i]).pack(fill="x", padx=3, pady=3, expand=1)
                inv_dir_frame = tk.Frame(mot)
                inv_dir_frame.pack(fill="x", padx=3, pady=3)
                ttk.Label(inv_dir_frame, text='Inverse Direction').pack(side="left", fill="x", padx=3, pady=3, expand=1)
                ttk.Checkbutton(inv_dir_frame, variable=self.inverse_homing_direction[i], takefocus=0).pack(side="left",fill="x", padx=3,pady=3, expand=1)
                ttk.Label(mot, text='Homing Acceleration').pack(fill="x", padx=3, pady=3, expand=1)
                ttk.Entry(mot, textvariable=self.homing_accel[i]).pack(fill="x", padx=3, pady=3, expand=1)
                ttk.Label(mot, text='Second Homing Speed Multiplier').pack(fill="x", padx=3, pady=3, expand=1)
                ttk.Entry(mot, textvariable=self.second_homing_mult[i]).pack(fill="x", padx=3, pady=3, expand=1)
                ttk.Label(mot, text='Second Homing Offset').pack(fill="x", padx=3, pady=3, expand=1)
                ttk.Entry(mot, textvariable=self.second_homing_offset[i]).pack(fill="x", padx=3, pady=3, expand=1)
                ttk.Label(mot, text='Homing Offset').pack(fill="x", padx=3, pady=3, expand=1)
                ttk.Entry(mot, textvariable=self.homing_offset[i]).pack(fill="x", padx=3, pady=3, expand=1)

    class TechnicalParameters(tk.Frame):
        def __init__(self, parent, *args, **kwargs):
            tk.Frame.__init__(self, parent, *args, **kwargs)
            self.microsteps = [tk.IntVar(value=0) for i in range(6)]
            self.irun = [tk.IntVar(value=0) for i in range(6)]
            self.ihold = [tk.IntVar(value=0) for i in range(6)]

            self.steps_per_full_revolution = tk.IntVar(value=200)

            mots_frame = tk.Frame(self)
            mots_frame.pack(fill="x", padx=3, pady=3)

            for i in range(6):
                mot = tk.Frame(mots_frame, relief="solid", borderwidth=1)
                mot.pack(fill="x", expand=1, side="left")
                ttk.Label(mot, text=f'Motor {i}').pack(fill="x", padx=3, pady=8, expand=1)
                ttk.Label(mot, text='Microsteps').pack(fill="x", padx=3, pady=3, expand=1)
                ttk.Entry(mot, textvariable=self.microsteps[i]).pack(fill="x", padx=3, pady=3, expand=1)
                ttk.Label(mot, text='Amperage at Run').pack(fill="x", padx=3, pady=3, expand=1)
                ttk.Entry(mot, textvariable=self.irun[i]).pack(fill="x", padx=3, pady=3, expand=1)
                ttk.Label(mot, text='Amperage at Hold').pack(fill="x", padx=3, pady=3, expand=1)
                ttk.Entry(mot, textvariable=self.ihold[i]).pack(fill="x", padx=3, pady=3, expand=1)

            ttk.Label(self, text='Steps per full Revolution').pack(fill="x", padx=3, pady=3)
            ttk.Entry(self, textvariable=self.steps_per_full_revolution).pack(fill="x", padx=3, pady=3)

    def __init__(self, parent, robot, *args, **kwargs):
        self.robot = robot
        tk.Frame.__init__(self, parent, *args, **kwargs)
        tabs = ttk.Notebook(self)
        tabs.pack(expand=True, fill="both", padx=3, pady=3)

        self.mot_params = self.MotorParameters(self)
        self.home_params = self.HomingParameters(self)
        self.tech_params = self.TechnicalParameters(self)

        tabs.add(self.mot_params, text='Motor Parameters')
        tabs.add(self.home_params, text='Homing Parameters')
        tabs.add(self.tech_params, text='Technical Parameters')

        submit_params = ttk.Button(self, text="Submit Parameters", command=robot.submit_params)
        submit_params.pack(fill="x", padx=3, pady=3)

class RobotSetup(tk.Frame):
    def __init__(self, parent, robot, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.x_offset = [tk.DoubleVar(value=0) for i in range(7)]
        self.y_offset = [tk.DoubleVar(value=0) for i in range(7)]
        self.z_offset = [tk.DoubleVar(value=0) for i in range(7)]

        joints = tk.Frame(self, relief="solid", borderwidth=1)
        joints.pack(fill="x", padx=3, pady=3)

        for i in range(6):
            joint = tk.Frame(joints, relief="solid", borderwidth=1)
            joint.pack(fill="x", side="left", expand=1)
            ttk.Label(joint, text=f'Joint {i}').pack(fill="x", padx=3, pady=8, expand=1)
            ttk.Label(joint, text='X Offset').pack(fill="x", padx=3, pady=3, expand=1)
            ttk.Entry(joint, textvariable=self.x_offset[i]).pack(fill="x", padx=3, pady=3, expand=1)
            ttk.Label(joint, text='Y Offset').pack(fill="x", padx=3, pady=3, expand=1)
            ttk.Entry(joint, textvariable=self.y_offset[i]).pack(fill="x", padx=3, pady=3, expand=1)
            ttk.Label(joint, text='Z Offset').pack(fill="x", padx=3, pady=3, expand=1)
            ttk.Entry(joint, textvariable=self.z_offset[i]).pack(fill="x", padx=3, pady=3, expand=1)

        extension = tk.Frame(joints, relief="solid", borderwidth=1)
        extension.pack(fill="x", side="left", expand=1)
        ttk.Label(extension, text=f'Extension').pack(fill="x", padx=3, pady=8, expand=1)
        ttk.Label(extension, text='X Offset').pack(fill="x", padx=3, pady=3, expand=1)
        ttk.Entry(extension, textvariable=self.x_offset[6]).pack(fill="x", padx=3, pady=3, expand=1)
        ttk.Label(extension, text='Y Offset').pack(fill="x", padx=3, pady=3, expand=1)
        ttk.Entry(extension, textvariable=self.y_offset[6]).pack(fill="x", padx=3, pady=3, expand=1)
        ttk.Label(extension, text='Z Offset').pack(fill="x", padx=3, pady=3, expand=1)
        ttk.Entry(extension, textvariable=self.z_offset[6]).pack(fill="x", padx=3, pady=3, expand=1)

        ttk.Button(self, text="Save Setup", command=robot.save_robot_setup).pack(fill="x", padx=3, pady=3)
        ttk.Button(self, text="Load Setup", command=robot.load_robot_setup).pack(fill="x", padx=3, pady=3)

class UIConfig(tk.Frame):
    def __init__(self, parent, robot, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        ttk.Button(self, text="Save Config", command=robot.save_config).pack(fill="x", padx=3, pady=3)
        ttk.Button(self, text="Load Config", command=robot.load_config).pack(fill="x", padx=3, pady=3)
        ttk.Button(self, text="Toggle \"Allow Data Transfer\"", command=robot.toggle_data_transfer).pack(fill="x", padx=3, pady=10)

class RobotAutomation(ToggledFrame):
    def __init__(self, parent, robot, *args, **kwargs):
        self.robot = robot
        ToggledFrame.__init__(self, parent, text="Automation", *args, **kwargs)
        button_frame = ttk.Frame(self.sub_frame)
        button_frame.pack(fill="both", expand=1)
        self.start_but = ttk.Button(button_frame, text="Start Automation", command=self.start_automation)
        self.start_but.pack(fill="both", side="left", expand=1)
        self.stop_but = ttk.Button(button_frame, text="Stop Automation", command=self.stop_automation, state="disabled")
        self.stop_but.pack(fill="both", side="left", expand=1)
        # self.update_but = ttk.Button(button_frame, text="Update Automation", command=self.update)
        # self.update_but.pack(fill="both", side="left", expand=1)
        self.steps_frame = ttk.Frame(self.sub_frame)
        self.steps_frame.pack(fill="both", expand=1, padx=4, pady=4)
        self.step_frames = []
        self.steps = []
        self.passage = 0

    def update(self):
        self.robot.automations["steps"] = []
        for step in enumerate(self.steps):
            self.robot.automations["steps"].append([])
            for param in enumerate(step[1]):
                self.robot.automations["steps"][step[0]].append(param[1].get())


    def add_step_fk(self, m1, m2, m3, m4, m5, m6, delay):
        print("added")
        self.robot.automations["steps"].append(["fk", m1, m2, m3, m4, m5, m6, delay])
        step = [tk.StringVar(value="  FK  "), tk.DoubleVar(value=m1), tk.DoubleVar(value=m2), tk.DoubleVar(value=m3),
                tk.DoubleVar(value=m4), tk.DoubleVar(value=m5), tk.DoubleVar(value=m6), tk.DoubleVar(value=delay), tk.IntVar(value=len(self.steps))]
        self.steps.append(step)
        step_frame = tk.Frame(self.steps_frame, relief="solid", borderwidth=1)
        step_frame.pack(fill="both", expand=1)
        self.step_frames.append(step_frame)
        ttk.Label(step_frame, textvariable=step[0]).pack(fill="both", side="left", expand=1)
        for i in range(7):
            ttk.Entry(step_frame, textvariable=step[1 + i]).pack(fill="both", side="left", expand=1)

    def add_step_ik(self, x, y, z, psi, theta, phi, delay):
        texts = ["X", "Y", "Z", "Psi", "Theta", "Phi", "Delay"]
        self.robot.automations["steps"].append(["ik", x, y, z, psi, theta, phi, delay])
        step = [tk.StringVar(value="ik"), tk.DoubleVar(value=float(x)), tk.DoubleVar(value=float(y)),
                tk.DoubleVar(value=float(z)),
                tk.DoubleVar(value=float(psi)), tk.DoubleVar(value=float(theta)), tk.DoubleVar(value=float(phi)),
                tk.DoubleVar(value=float(delay)), tk.IntVar(value=len(self.steps))]
        self.steps.append(step)
        step_frame = tk.Frame(self.steps_frame, relief="solid", borderwidth=1)
        step_frame.pack(fill="both", expand=1)
        self.step_frames.append(step_frame)
        ttk.Label(step_frame, text="  IK  ", font="bold").pack(fill="both", side="left", expand=1)
        for i in range(7):
            param_frame = ttk.Frame(step_frame)
            param_frame.pack(fill="both", side="left", expand=1, padx=4)
            ttk.Label(param_frame, text=texts[i]+": ").pack(side="left", expand=0)
            ttk.Entry(param_frame, textvariable=step[1 + i]).pack(fill="both", side="left", expand=1)
        """
        ttk.Button(step_frame, text="Remove").pack(side="left", expand=0)
        
        param_frame = ttk.Frame(step_frame)
        param_frame.pack(fill="both", side="left", expand=1, padx=4)
        ttk.Label(param_frame, text="Order").pack(side="left", expand=0)
        ttk.Entry(param_frame, textvariable=step[8]).pack(fill="both", side="left", expand=1)
        """

    def remove_step(self):
        pass

    def start_automation(self):
        self.update()
        self.robot.enable_automation(True)
        self.start_but.configure(state="disabled")
        self.stop_but.configure(state="enabled")
        self.step_frames[self.passage].configure(background="#00ff00")

    def stop_automation(self):
        self.robot.enable_automation(False)
        self.start_but.configure(state="enabled")
        self.stop_but.configure(state="disabled")
        self.step_frames[self.passage].configure(background=ttk.Style().lookup("TFrame", "background"))
        self.passage = 0

    def next_step(self):
        self.step_frames[self.passage].configure(background=ttk.Style().lookup("TFrame", "background"))
        self.passage = (self.passage + 1) % len(self.steps)
        if self.robot.run_automation:
            self.step_frames[self.passage].configure(background="#00ff00")

    def load_steps(self, steps):

        for step in copy.copy(steps):
            if step[0] == "fk":
                self.add_step_fk(*step[1:])
            elif step[0] == "ik":
                self.add_step_ik(*step[1:])
