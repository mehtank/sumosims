import random

import config as defaults
from loopsim import LoopSim

# this is the main entry point of this script
if __name__ == "__main__":
    from agent_types import basicHumanParams as humanParams

    for count in [20, 25, 30, 35, 40, 45, 50]:
        if defaults.RANDOM_SEED:
            print "Setting random seed to ", defaults.RANDOM_SEED
            random.seed(defaults.RANDOM_SEED)

        humanParams["count"] = count

        opts = {
            "paramsList" : [humanParams],
            "simSteps"   : 500,
            "tag"        : "humanTrafficJam"
        }

        sim = LoopSim("loopsim", length=1000, numLanes=2, simStepLength=0.5)

        sim.simulate(opts)
        sim.plot(show=True, save=True)
