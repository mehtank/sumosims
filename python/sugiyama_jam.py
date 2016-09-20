import random
import itertools

import config as defaults
from loopsim import LoopSim
from agent_types import basicHumanParams as humanParams, \
    basicIDMParams as IDMParams, basicACCParams as ACCParams, \
    basicGapFillerParams as gapFillerParams, \
    basicFillGapMidpointParams as fillGapMidpointParams, \
    basicMidpointParams as midpointParams


if __name__ == "__main__":
    numLanes = 1

    sim = LoopSim("loopsim", length=230, numLanes=numLanes, simStepLength=0.5)

    vTypeParams = humanParams
    vTypeParams["laneSpread"] = True
    vTypeParams["tau"] = 0.5
    vTypeParams["speedDev"] = 0.0
    vTypeParams["speedFactor"] = 1
    vTypeParams["sigma"] = 0.5
    vTypeParams["count"] = 22

    if defaults.RANDOM_SEED:
        print "Setting random seed to ", defaults.RANDOM_SEED
        random.seed(defaults.RANDOM_SEED)

        opts = {
            "paramsList" : [vTypeParams],
            "simSteps"   : 500,
            "tag"        : "Sugiyama",
        }

        sim.simulate(opts)
        sim.plot(show=False, save=True, speedRange=(0,8), fuelRange=(0, 40)).close("all")
