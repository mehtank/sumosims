# random seed
RANDOM_SEED = 23434

# the port used for communicating with your sumo instance
PORT = 8873

# the timestep used for simulation (s)
SIM_STEP_LENGTH = 1.0

LENGTH = 1000
L4 = LENGTH/4.
EDGESTARTS = {"bottom": 0, "right": L4, "top": 2*L4, "left": 3*L4}

NET_PATH = "net/"
IMG_PATH = "img/"
DATA_PATH = "data/"

# Roadway speed limit
# 30 m/s = 67.1081 mph
SPEED_LIMIT = 30
