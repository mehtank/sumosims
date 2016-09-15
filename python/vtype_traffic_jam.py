import random

import config as defaults
from loopsim import LoopSim
from agent_types import basicHumanParams as humanParams, \
    basicIDMParams as IDMParams, basicACCParams as ACCParams, \
    basicGapFillerParams as gapFillerParams, \
    basicFillGapMidpointParams as fillGapMidpointParams, \
    basicMidpointParams as midpointParams

# this is the main entry point of this script
if __name__ == "__main__":
    # vTypeParams = humanParams
    # vTypeParams = fillGapMidpointParams
    # vTypeParams = gapFillerParams
    # vTypeParams = IDMParams
    # vTypeParams = midpointParams
    vTypeParams = ACCParams   # FIXME(cathywu) not working

    # for count in [20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120]:
    for count in [40, 50, 60, 70, 80, 90, 100, 110, 120]:
        if defaults.RANDOM_SEED:
            print "Setting random seed to ", defaults.RANDOM_SEED
            random.seed(defaults.RANDOM_SEED)

        vTypeParams["count"] = count

        opts = {
            "paramsList" : [vTypeParams],
            "simSteps"   : 500,
            "tag"        : "TrafficJam",
        }

        sim = LoopSim("loopsim", length=1000, numLanes=2, simStepLength=0.5)

        sim.simulate(opts)
        sim.plot(show=True, save=True)
