import tkinter as tk
from tkinter import ttk
import ui_tabs
import robot_control


if __name__ == "__main__":
    root = tk.Tk()
    root.title("VEPR Control Panel")
    root.configure(bg="#ffffff")

    tabs = ttk.Notebook(root)
    tabs.pack(expand=True, fill="both", padx=3, pady=3)
    robot = robot_control.RobotControl()
    fk_control = ui_tabs.FKControl(tabs, robot=robot)
    fk_control.pack(fill="both", expand=1)
    ik_control = ui_tabs.IKControl(tabs, robot=robot)
    ik_control.pack(fill="both", expand=0)
    motor_control = ui_tabs.MotorControl(tabs, robot=robot)
    motor_control.pack(fill="both", expand=1)
    vepr_params = ui_tabs.VEPRParameters(tabs, robot=robot)
    vepr_params.pack(fill="both", expand=1)
    ui_config = ui_tabs.UIConfig(tabs, robot)
    ui_config.pack(fill="both", expand=1)

    robot.set_tabs(fk_control, ik_control, motor_control, vepr_params)
    robot.load_config()

    tabs.add(fk_control, text='Forward Kinematics')
    tabs.add(ik_control, text='Inverse Kinematics')
    tabs.add(motor_control, text='Motor Control')
    tabs.add(vepr_params, text='Parameters')
    tabs.add(ui_config, text='UI Config')

    vepr_params_frame = ui_tabs.ToggledFrame(root, text='Parameters', relief="raised", borderwidth=1)
    #vepr_params_frame.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")

    ttk.Label(vepr_params_frame.sub_frame, text='Global Motor Speed').pack(fill="x", expand=1)
    ttk.Entry(vepr_params_frame.sub_frame).pack()

    root.mainloop()
