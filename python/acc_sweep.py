import copy
import random

from carfns import SwitchVTypeFn, changeFasterLaneBuilder
from loopsim import LoopSim
from agent_types import basicHumanParams as humanParams, basicIDMParams as IDMParams, basicACCParams as ACCParams
import config as defaults

# this is the main entry point of this script
if __name__ == "__main__":
    # This sweep demonstrates that our ACC implementation is about as good as IDM in the loop setting

    changeFasterLane = changeFasterLaneBuilder()
    hybridParams = copy.copy(humanParams)
    hybridParams["name"] = "hybrid"

    for count in [20, 25, 30, 35, 40, 45, 50]:

        # IDM sweep
        if defaults.RANDOM_SEED:
            print "Setting random seed to ", defaults.RANDOM_SEED
            random.seed(defaults.RANDOM_SEED)

        hybridParams["count"] = count
        hybridParams["function"] = SwitchVTypeFn("idm", 0.5, initCarFn=changeFasterLane)

        opts = {
            "paramsList" : [humanParams, IDMParams, ACCParams, hybridParams],
            "simSteps"   : 500,
            "tag"        : "IDMSweep"
        }

        sim = LoopSim("loopsim", length=1000, numLanes=2, simStepLength=0.5)

        sim.simulate(opts)
        sim.plot(show=True, save=True)

        # ACC sweep
        if defaults.RANDOM_SEED:
            print "Setting random seed to ", defaults.RANDOM_SEED
            random.seed(defaults.RANDOM_SEED)

        hybridParams["function"] = SwitchVTypeFn("acc", 0.5, initCarFn=changeFasterLane)

        opts = {
            "paramsList" : [humanParams, ACCParams, hybridParams],
            "simSteps"   : 500,
            "tag"        : "ACCSweep"
        }

        sim = LoopSim("loopsim", length=1000, numLanes=2, simStepLength=0.5)

        sim.simulate(opts)
        sim.plot(show=True, save=True)
