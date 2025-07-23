# CHOPCONF


"""
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
        diss2g = gr.Checkbox(value=False, label="Short to Ground {diss2g}")"""