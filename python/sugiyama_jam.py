import random

import config as defaults
from loopsim import LoopSim
from agent_types import basicHumanParams as humanParams, \
    basicIDMParams as IDMParams, basicACCParams as ACCParams, \
    basicGapFillerParams as gapFillerParams, \
    basicFillGapMidpointParams as fillGapMidpointParams, \
    basicMidpointParams as midpointParams


if __name__ == "__main__":
    numLanes = 1
    vTypeParams = humanParams
    vTypeParams["tau"] = 0.5
    vTypeParams["sigma"] = 0.5
    vTypeParams["speedDev"] = 0
    vTypeParams["speedFactor"] = 1

    # vTypeParams = fillGapMidpointParams
    # vTypeParams = gapFillerParams
    # vTypeParams = midpointParams
    # vTypeParams = IDMParams
    # vTypeParams = ACCParams

    if defaults.RANDOM_SEED:
        print "Setting random seed to ", defaults.RANDOM_SEED
        random.seed(defaults.RANDOM_SEED)

    vTypeParams["count"] = 22 * numLanes

    opts = {
        "paramsList" : [vTypeParams],
        "simSteps"   : 500,
        "tag"        : "SugiyamaJam",
    }

    sim = LoopSim("loopsim", length=230, numLanes=numLanes, simStepLength=0.5)

    sim.simulate(opts)
    sim.plot(show=True, save=True)
