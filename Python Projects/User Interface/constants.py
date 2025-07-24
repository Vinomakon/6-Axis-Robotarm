# First Adresses
# 0-5 are occupied by the motors
igener = '6' # General Parameters
istart = '9' # Starting all the motors

# Second Motor Addresses
ienmot = '00' # Enable motor
iangle = '01' # Set angle to move to
ispeed = '02' # Set speed
iaccel = '03' # Set acceleration
ireduc = '04' # Set reduction
isthom = '10' # Start homing
ihomsp = '11' # Set homing speed
ihomin = '12' # Set inverse homing
ihomac = '13' # Set homing acceleration
ihomof = '14' # Set homing offset
ihommu = '15' # Set homing speed multiplier
itmcen = '20' # Initiate TMC
imrstp = '21' # Set microstep resolution
ipkrms = '22' # Set peak RMS
ihcmlt = '23' # Set Hold Current Multiplier
icrpos = '80' # Get current Position

# General Addresses ('6' or 'igener')
idefst = '00' # Set default steps